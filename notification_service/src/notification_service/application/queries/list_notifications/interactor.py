from notification_service.application.queries.list_notifications.gateway import (
    NotificationQueryGateway,
)
from notification_service.domain.notification import Notification


class ListNotificationsInteractor:
    def __init__(self, gateway: NotificationQueryGateway) -> None:
        self._gateway = gateway

    async def execute(self, limit: int = 50) -> list[Notification]:
        return await self._gateway.list_recent(limit)
