from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import Category, Transaction, User
from app.schemas import CategorySpending, DashboardStats, QuickStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyse"),
):
    """
    Get dashboard statistics
    """
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    transactions = (
        db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        )
    ).all()

    # Calculate income and expenses
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expense = sum(t.amount for t in transactions if t.type == "expense")
    net_balance = total_income - total_expense

    total_transactions = len(transactions)
    income_transactions = len([t for t in transactions if t.type == "income"])
    expense_transactions = len([t for t in transactions if t.type == "expense"])

    # Averages
    average_transaction_amount = (
        (total_income + total_expense) / total_transactions
        if total_transactions > 0
        else 0
    )
    average_daily_spend = total_expense / days if days > 0 else 0
    average_weekly_spend = (total_expense / days) * 7 if days > 0 else 0

    category_spending = (
        db.query(
            Category.name,
            Category.icon,
            Category.colour,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "expense",
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        )
        .group_by(Category.id)
        .order_by(func.sum(Transaction.amount).desc())
        .limit(5)
        .all()
    )

    top_categories = [
        CategorySpending(
            category_name=cat.name,
            category_icon=cat.icon,
            category_colour=cat.colour,
            total_amount=float(cat.total),
            transaction_count=cat.count,
            percentage=(float(cat.total) / total_expense * 100)
            if total_expense > 0
            else 0,
        )
        for cat in category_spending
    ]

    # Budgets
    monthly_budget = current_user.monthly_budget
    budget_spent_percentage = None
    budget_remaining = None

    if monthly_budget and monthly_budget > 0:
        days_in_period = min(days, 30)
        budget_for_period = (monthly_budget / 30) * days_in_period
        budget_spent_percentage = (
            (total_expense / budget_for_period * 100) if budget_for_period > 0 else 0
        )
        budget_remaining = budget_for_period - total_expense

    recent_transactions_query = {
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.date.desc())
        .limit(5)
        .all()
    }

    recent_transactions = [
        {
            "id": t.id,
            "amount": t.amount,
            "description": t.description,
            "date": t.date,
            "category": t.category.name if t.category else "Uncategorised",
            "type": t.type,
            "account": t.account,
            "currency": t.currency,
            "status": t.status,
            "created_at": t.created_at,
            "updated_at": t.updated_at,
        }
        for t in recent_transactions_query
    ]

    return DashboardStats(
        period=f"last_{days}_days",
        start_date=start_date,
        end_date=end_date,
        total_income=total_income,
        total_expense=total_expense,
        net_balance=net_balance,
        top_spending_categories=top_categories,
        total_transactions=total_transactions,
        income_transactions=income_transactions,
        expense_transactions=expense_transactions,
        average_transaction_amount=average_transaction_amount,
        average_daily_spend=average_daily_spend,
        average_weekly_spend=average_weekly_spend,
        monthly_budget=monthly_budget,
        budget_spent_percentage=budget_spent_percentage,
        budget_remaining=budget_remaining,
        recent_transactions=recent_transactions,
    )


@router.get("/quick-stats", response_model=QuickStats)
def get_quick_stats(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """
    Quick financial overview with basic metrics and budget status
    """
    transactions = (
        db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    )

    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expense = sum(t.amount for t in transactions if t.type == "expense")
    net_balance = total_income - total_expense

    # Budgets
    monthly_budget = current_user.monthly_budget
    budget_spent_percentage = None
    budget_remaining = None

    if monthly_budget and monthly_budget > 0:
        now = datetime.now(timezone.utc)
        start_of_month = now.replace(days=1, hour=0, minute=0, second=0, microsecond=0)

        current_month_expense = sum(
            t.amount
            for t in transactions
            if t.type == "expense" and t.date >= start_of_month
        )

        budget_spent_percentage = (
            (current_month_expense / monthly_budget * 100) if monthly_budget > 0 else 0
        )
        budget_remaining = monthly_budget - current_month_expense

    return QuickStats(
        total_income=total_income,
        total_expense=total_expense,
        net_balance=net_balance,
        budget_spent_percentage=budget_spent_percentage,
        budget_remaining=budget_remaining,
    )


@router.get("/spending-by-category", response_model=List[CategorySpending])
def get_spending_by_category(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
):
    """
    Get spending by category
    """
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    total_expense = (
        db.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "expense",
            Transaction.date >= start_date,
        )
        .scalar()
        or 0
    )

    category_data = (
        db.query(
            Category.name,
            Category.icon,
            Category.colour,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "expense",
            Transaction.date >= start_date,
        )
        .group_by(Category.id)
        .order_by(func.sum(Transaction.amount).desc())
        .limit(limit)
        .all(),
    )

    return [
        CategorySpending(
            category_name=cat.name,
            category_icon=cat.icon,
            category_colour=cat.colour,
            total_amount=float(cat.total),
            transaction_count=cat.count,
            percentage=(float(cat.total) / total_expense * 100)
            if total_expense > 0
            else 0,
        )
        for cat in category_data
    ]
