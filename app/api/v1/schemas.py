from pydantic import BaseModel, Field
from app.models.wallet import OperationType


class WalletBalanceResponse(BaseModel):
    balance_rub: float


class WalletOperationRequest(BaseModel):
    amount: float = Field(gt=0)
    operation_type: OperationType