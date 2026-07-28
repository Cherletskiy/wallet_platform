import uuid
from typing import Protocol

from notification_service.domain.notification import Notification


class NotificationQueryGateway(Protocol):
    async def list_recent(
        self,
        *,
        user_id: uuid.UUID,
        wallet_id: uuid.UUID | None = None,
        limit: int = 50,
    ) -> list[Notification]: ...
