from decimal import Decimal

from pydantic import BaseModel, Field

from wallet_service.domain.wallet import OperationType


class WalletBalanceResponse(BaseModel):
    balance_rub: float


class WalletResponse(BaseModel):
    wallet_id: str
    balance_rub: float


class WalletListItemResponse(BaseModel):
    wallet_id: str
    balance_rub: float


class WalletOperationRequest(BaseModel):
    amount: Decimal = Field(gt=0, decimal_places=2)
    operation_type: OperationType
