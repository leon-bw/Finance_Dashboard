from uuid import UUID

from pydantic import BaseModel, DateTime, Field


class Transaction(BaseModel):
    id: UUID = Field(
        default_factory=UUID.uuid4,
        description="The unique identifier of the transaction",
    )
    amount: float = Field(description="The amount of the transaction")
    description: str = Field(description="The description of the transaction")
    date: DateTime = Field(
        default_factory=DateTime.now,
        description="The date and time the transaction occurred",
    )
    category: str = Field(description="The category the transaction belongs to")
    type: str = Field(
        description="The type of the transaction", enum=["income", "expense"]
    )
    account: str = Field(description="The account the transaction belongs to")
    currency: str = Field(description="The currecny the transaction is in")
    status: str = Field(
        default="active",
        enum=["active", "inactive"],
        description="The status of the transaction",
    )
    created_at: DateTime = Field(
        default_factory=DateTime.now,
        description="The date and time the transaction was created in the database",
        read_only=True,
    )
    updated_at: DateTime = Field(
        default_factory=DateTime.now,
        description="The date and time the transaction was last updated in the database",
    )
