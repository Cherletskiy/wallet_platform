import uuid
from dataclasses import dataclass

from wallet_service.domain.wallet import OperationType


@dataclass(slots=True)
class ApplyWalletOperationInput:
    wallet_id: uuid.UUID
    amount_cent: int
    operation_type: OperationType
