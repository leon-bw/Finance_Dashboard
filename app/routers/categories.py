from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import Category, Transaction, User
from app.schemas import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """
    Get all default and user categories
    """
    categories = (
        db.query(Category)
        .filter((Category.is_default) | (Category.user_id == current_user.id))
        .all()
    )

    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get specific category by ID
    """
    category = (
        db.query(Category)
        .filter(
            Category.id == category_id,
            (Category.is_default) | (Category.user_id == current_user.id),
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with id: {category_id} not found",
        )

    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new custom category for current user
    """
    # Does category already exist for user?
    existing_category = db.query(Category).filter(
        Category.name == category.name,
        (Category.is_default) | (Category.user_id == current_user.id),
    )

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with name {category.name} already exists",
        )

    # Create new category
    new_category = Category(
        **category.model_dump(), user_id=current_user.id, is_default=False
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: UUID,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update a custom category
    """
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == current_user.id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category with id: {category_id} not found",
        )

    # Prevent default category from being updated
    if category.is_default:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Default category cannot be updated",
        )

    # Does new name clash with existing name
    update_data = category_update.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing_category = (
            db.query(Category)
            .filter(
                Category.name == update_data["name"],
                Category.id != category_id,
                (Category.is_default) | (Category.user_id == current_user.id),
            )
            .first()
        )

        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f" Category with {update_data['name']} already exists",
            )

    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete custom category for user
    """
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == current_user.id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category with id: {category_id} not found",
        )

    # Prevent deletion of default category
    if category.is_default:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Default category cannot be deleted",
        )

    transaction_count = (
        db.query(Transaction).filter(Transaction.category_id == category_id).count()
    )

    if transaction_count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Category with {transaction_count} transaction(s) cannot be deleted, delete or reassign transaction(s) first",
        )

    db.delete(category)
    db.commit()

    return None
