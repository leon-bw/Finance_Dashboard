from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import Budget, Category, User
from app.schemas import BudgetCreate, BudgetResponse, BudgetUpdate

router = APIRouter(prefix="/budgets", tags=["Budgets"])


def _as_aware(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Normalise a datetime to timezone-aware UTC.

    SQLite returns naive datetimes, while values parsed from request bodies are
    timezone-aware; coerce both so they can be compared safely.
    """
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _validate_category(db: Session, category_id: UUID, user: User) -> None:
    """
    Ensure a referenced category exists and is usable by the user.
    """
    category = (
        db.query(Category)
        .filter(
            Category.id == category_id,
            (Category.is_default) | (Category.user_id == user.id),
        )
        .first()
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found",
        )


@router.get("/", response_model=List[BudgetResponse])
def get_budgets(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get all budgets for the current user with optional filtering
    """
    query = db.query(Budget).filter(Budget.user_id == current_user.id)

    if is_active is not None:
        query = query.filter(Budget.is_active == is_active)
    if category_id:
        query = query.filter(Budget.category_id == category_id)

    return query.all()


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(
    budget_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific budget by ID
    """
    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id, Budget.user_id == current_user.id)
        .first()
    )

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget with id {budget_id} not found",
        )

    return budget


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget: BudgetCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new budget for the current user
    """
    if budget.category_id is not None:
        _validate_category(db, budget.category_id, current_user)

    new_budget = Budget(**budget.model_dump(), user_id=current_user.id)

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    return new_budget


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: UUID,
    budget_update: BudgetUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing budget
    """
    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id, Budget.user_id == current_user.id)
        .first()
    )

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget with id {budget_id} not found",
        )

    update_data = budget_update.model_dump(exclude_unset=True)

    if update_data.get("category_id") is not None:
        _validate_category(db, update_data["category_id"], current_user)

    # Guard against an update producing an end date on or before the start date
    new_start = _as_aware(update_data.get("start_date", budget.start_date))
    new_end = _as_aware(update_data.get("end_date", budget.end_date))
    if new_end <= new_start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )

    for field, value in update_data.items():
        setattr(budget, field, value)

    budget.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(budget)

    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete an existing budget
    """
    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id, Budget.user_id == current_user.id)
        .first()
    )

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget with id {budget_id} not found",
        )

    db.delete(budget)
    db.commit()

    return None
