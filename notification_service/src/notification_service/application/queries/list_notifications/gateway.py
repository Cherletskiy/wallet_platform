from typing import Protocol

from notification_service.domain.notification import Notification


class NotificationQueryGateway(Protocol):
    async def list_recent(self, limit: int = 50) -> list[Notification]: ...
