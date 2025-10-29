from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


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
    status: Literal["conpleted", "pending"] = Field(
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
    status: Optional[Literal["conpleted", "pending"]] = None
