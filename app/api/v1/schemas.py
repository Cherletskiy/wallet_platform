from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.wallet import OperationType


class WalletBalanceResponse(BaseModel):
    balance_rub: float


class WalletOperationRequest(BaseModel):
    amount: Decimal = Field(gt=0, decimal_places=2)
    operation_type: OperationType