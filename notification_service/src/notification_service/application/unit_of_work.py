from typing import Protocol

from notification_service.application.commands.handle_wallet_transaction import (
    gateway as notification_gateway,
)


class NotificationUnitOfWork(Protocol):
    notifications: notification_gateway.NotificationCommandGateway

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
