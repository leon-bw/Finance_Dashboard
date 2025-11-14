from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator

# ----Transaction class models----


class TransactionBase(BaseModel):
    """
    Base model with shared fields for all transactions
    """

    amount: float = Field(gt=0, description="The amount of the transaction")
    description: str = Field(description="The description of the transaction")
    date: datetime | None = Field(
        description="The date and time the transaction occurred"
    )
    category: str = Field(description="The category the transaction belongs to")
    type: Literal["income", "expense"] = Field(
        description="The type of the transaction"
    )
    account: str = Field(description="The account the transaction belongs to")
    currency: str = Field(
        default="GBP", description="The currency the transaction is in"
    )


class TransactionCreate(TransactionBase):
    """
    Model inherits from TransactionBase for creating a new transaction
    """

    pass


class TransactionResponse(TransactionBase):
    """
    This model is used to return a transaction to the client when retrieving data
    """

    id: UUID = Field(description="The unique identifier of the transaction")
    status: Literal["completed", "pending"] = Field(
        description="The status of the transaction"
    )
    created_at: datetime = Field(
        description="The date and time the transaction was created in the database"
    )
    updated_at: datetime = Field(
        description="The date and time the transaction was last updated in the database"
    )

    class Config:
        from_attributes = True


class TransactionUpdate(TransactionBase):
    """
    Model inherits from TransactionBase for updating transactions
    """

    amount: Optional[float] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    category: Optional[str] = None
    type: Optional[Literal["income", "expense"]] = None
    account: Optional[str] = None
    currency: Optional[str] = None
    status: Optional[Literal["completed", "pending"]] = None


# ----User class models----


class UserBase(BaseModel):
    """
    Base model with shared fields for all users
    """

    email: EmailStr = Field(description="The email address of the user (unique)")
    username: str = Field(
        min_length=3, max_length=50, description="The username of the user"
    )
    first_name: str = Field(description="The first name of the user")
    last_name: str = Field(description="The last name of the user")


class UserCreate(UserBase):
    """
    Model inherits from UserBase, properties for user registration
    """

    password: str = Field(min_length=8, description="User password (hashed)")
    currency_preference: str = Field(
        default="GBP", description="The preferred currency of the user"
    )
    monthly_budget: float = Field(
        default=0, description="The monthly budget of the user"
    )


class UserLogin(BaseModel):
    """
    Model for user login
    """

    username: str
    password: str


class UserUpdate(BaseModel):
    """
    Model for updating the users profile information
    """

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    currency_preference: Optional[str] = None
    monthly_budget: Optional[float] = None


class UserResponse(BaseModel):
    """
    Model for properties returned to client
    """

    id: UUID
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    is_active: bool
    is_demo: bool = Field(description="Confirm if demo account is in use")
    currency_preference: str
    monthly_budget: Optional[float]
    created_at: datetime = Field(
        description="The date and time the account was created in the database"
    )
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


# ----JWT Token class models----


class Token(BaseModel):
    """
    JWT token response
    """

    access_token: str = Field(description="The access token for the user")
    token_type: str = Field(
        default="bearer", description="The type of token (always bearer)"
    )


class TokenData(BaseModel):
    """
    Data that is stored in JWT Token
    """

    username: Optional[str] = None
    user_id: Optional[UUID] = None


# ----Category class models----


class CategoryBase(BaseModel):
    """
    Base model with shared fields for categories
    """

    name: str = Field(
        min_length=1, max_length=50, description="The name of the category"
    )
    type: Literal["income", "expense"] = Field(description="THe type of the category")
    description: Optional[str] = Field(description="The description of the category")
    colour: Optional[str] = Field(description="The colour of the category")
    icon: Optional[str] = Field(description="The icon of the category")


class CategoryCreate(CategoryBase):
    """
    Model inherits from CategoryBase for creating a new category
    """

    pass


class CategoryResponse(CategoryBase):
    """
    Model for properties returned to client
    """

    id: UUID = Field(description="The unique identifier of the category")
    is_default: bool = Field(description="Whether this is a default category or not")
    created_at: datetime = Field(
        description="The date and time the category was created in the database"
    )
    updated_at: datetime = Field(
        description="The date and time the category was last updated in the database"
    )

    class Config:
        from_attributes = True


class CategoryUpdate(CategoryBase):
    """
    Model inherits from CategoryBase for updating categories
    """

    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    colour: Optional[str] = None


# ----Budget class models----


class BudgetBase(BaseModel):
    """
    Base model with shared fields for budgets
    """

    amount: float = Field(gt=0, description="The limit of the budget")
    period: Literal["daily", "weekly", "monthly", "yearly"] = Field(
        default="monthly", description="The period of the budget"
    )
    category_id: Optional[UUID] = Field(
        description="The category the budget belongs to"
    )
    start_date: datetime = Field(description="The start date of the budget")
    end_date: datetime = Field(description="The end date of the budget")
    alert_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="The alert threshold when (%) of budget is spent",
    )

    @field_validator("end_date")
    @classmethod
    def end_date_must_be_after_start_date(cls, value, info: ValidationInfo):
        # Validate that the end date is after start date
        if value is not None and "start_date" in info.data:
            if value <= info.data["start_date"]:
                raise ValueError("End date must be after start date")
        return value


class BudgetCreate(BudgetBase):
    """
    Model inherits from BudgetBase for creating a new budget
    """

    pass


class BudgetResponse(BudgetBase):
    """
    Model for properties returned to client
    """

    id: UUID = Field(description="The unique identifier of the budget")
    user_id: UUID = Field(description="The user the budget belongs to")
    is_active: bool = Field(
        default=True, description="Whether the budget is active or not"
    )
    created_at: datetime = Field(
        description="The date and time the budget was created in the database"
    )
    updated_at: datetime = Field(
        description="The date and time the budget was last updated in the database"
    )

    class Config:
        from_attributes = True


class BudgetUpdate(BudgetBase):
    """
    Model inherits from BudgetBase for updating budgets
    """

    amount: Optional[float] = Field(None, gt=0)
    period: Optional[Literal["daily", "weekly", "monthly", "yearly"]] = None
    category_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    alert_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
