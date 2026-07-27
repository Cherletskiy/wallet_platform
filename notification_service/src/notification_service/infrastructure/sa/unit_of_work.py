from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.application.commands.handle_wallet_transaction import (
    gateway as notification_gateway,
)
from notification_service.infrastructure.sa.repositories import (
    notification_repository as notification_repository_module,
)


class SQLAlchemyNotificationUnitOfWork:
    notifications: notification_gateway.NotificationCommandGateway

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.notifications = (
            notification_repository_module.SQLAlchemyNotificationRepository(session)
        )

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
