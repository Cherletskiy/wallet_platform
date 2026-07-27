import uuid
from typing import Protocol

from notification_service.domain.notification import Notification


class NotificationCommandGateway(Protocol):
    async def get_by_source_event_id(
        self,
        source_event_id: uuid.UUID,
    ) -> Notification | None: ...

    async def add(self, notification: Notification) -> None: ...
