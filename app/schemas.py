from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

# Transaction class models


class TransactionBase(BaseModel):
    """
    Base model with shared fields for all transactions
    """

    amount: float = Field(description="The amount of the transaction")
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


# User class models


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
    currency_preference: Optional[str] = (
        None,
        Field(description="The currency preference of the user"),
    )
    monthly_budget: Optional[float] = (
        None,
        Field(description="The monthly budget of the user"),
    )


class UserResponse(BaseModel):
    """
    Model for properties returned to client
    """

    id: UUID
    is_active: bool
    is_demo: bool = Field(description="Confirm is this is a demo account or not")
    currency_preference: str
    monthly_budget: Optional[float]
    created_at: datetime = Field(
        description="The date and time the account was created in the database"
    )
    last_login: Optional[datetime]


class Token(BaseModel):
    """
    JWT token response
    """

    access_token: str = Field(description="The access token for the user")
    token_type: str = "bearer", Field(description="The type of token (always bearer)")


class TokenData(BaseModel):
    """
    Data that is stored in JWT Token
    """

    username: Optional[str] = None
    user_id: Optional[UUID] = None
