from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, UUID4


class TransactionSchema(BaseModel):
    transaction_id: UUID4
    user_id: UUID4
    amount: Decimal
    transaction_type: str
    task_id: Optional[UUID4]
    created_at: str


class TransactionCreateSchema(BaseModel):
    user_id: UUID4
    amount: Decimal
    transaction_type: str
    task_id: Optional[UUID4] = None
