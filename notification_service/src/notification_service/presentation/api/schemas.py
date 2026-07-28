import uuid
from datetime import datetime

from pydantic import BaseModel

from notification_service.domain.notification import WalletOperationType


class HealthResponse(BaseModel):
    status: str


class NotificationResponse(BaseModel):
    id: uuid.UUID
    source_event_id: uuid.UUID
    user_id: uuid.UUID
    wallet_id: uuid.UUID
    operation_type: WalletOperationType
    amount_rub: float
    balance_rub: float
    message: str
    created_at: datetime | None
