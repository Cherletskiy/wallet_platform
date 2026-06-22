import enum
import uuid
from dataclasses import dataclass, field
from datetime import datetime


class OperationType(enum.Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"


@dataclass(slots=True)
class Operation:
    wallet_id: uuid.UUID
    operation_type: OperationType
    amount_cent: int
    id: int | None = None
    created_at: datetime | None = None


@dataclass(slots=True)
class Wallet:
    id: uuid.UUID
    balance_cent: int = 0
    created_at: datetime | None = None
    operations: list[Operation] = field(default_factory=list)
