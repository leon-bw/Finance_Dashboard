import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    date = Column(datetime, default=datetime.timestamp)
    category = Column(String, nullable=False)
    type = Column(String, nullable=False)
    account = Column(String, nullable=False)
    currency = Column(String, default="GBP")
    status = Column(String, default="completed")
    created_at = Column(datetime, default=datetime.timestamp)
    updated_at = Column(
        datetime, default=datetime.timestamp, onupdate=datetime.timestamp
    )


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    currency_preference = Column(String, default="GBP")
    monthly_budget = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    is_demo = Column(Boolean, default=False)
    created_at = Column(datetime, default=datetime.timestamp)
    updated_at = Column(
        datetime, default=datetime.timestamp, onupdate=datetime.timestamp
    )
    last_login = Column(datetime, nullable=True)

    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    description = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(datetime, default=datetime.timestamp)
    updated_at = Column(
        datetime, default=datetime.timestamp, onupdate=datetime.timestamp
    )

    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("category.id"), nullable=True)
    amount = Column(Float, nullable=False)
    period = Column(String, default="monthly")
    start_date = Column(datetime, nullable=False)
    end_date = Column(datetime, nullable=False)
    is_active = Column(Boolean, default=True)
    alert_threshold = Column(Float, default=0.8)
    created_at = Column(datetime, default=datetime.timestamp)
    updated_at = Column(
        datetime, default=datetime.timestamp, onupdate=datetime.timestamp
    )
