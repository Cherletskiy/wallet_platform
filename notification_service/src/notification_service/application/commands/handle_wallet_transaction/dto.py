import uuid
from dataclasses import dataclass

from notification_service.domain.notification import WalletOperationType


@dataclass(slots=True)
class HandleWalletTransactionInput:
    source_event_id: uuid.UUID
    wallet_id: uuid.UUID
    operation_type: WalletOperationType
    amount_cent: int
    balance_cent: int
