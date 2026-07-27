import enum
import uuid
from dataclasses import dataclass
from datetime import datetime


class WalletOperationType(enum.StrEnum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"


@dataclass(slots=True)
class Notification:
    source_event_id: uuid.UUID
    wallet_id: uuid.UUID
    operation_type: WalletOperationType
    amount_cent: int
    balance_cent: int
    message: str
    id: uuid.UUID | None = None
    created_at: datetime | None = None
