from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from notification_service.application.commands.handle_wallet_transaction import (
    HandleWalletTransactionInteractor,
)
from notification_service.application.commands.handle_wallet_transaction import (
    gateway as notification_gateway,
)
from notification_service.application.queries.list_notifications.gateway import (
    NotificationQueryGateway,
)
from notification_service.application.queries.list_notifications.interactor import (
    ListNotificationsInteractor,
)
from notification_service.application.unit_of_work import NotificationUnitOfWork
from notification_service.infrastructure.sa.repositories import (
    notification_repository as notification_repository_module,
)
from notification_service.infrastructure.sa.session import async_session_factory
from notification_service.infrastructure.sa.unit_of_work import (
    SQLAlchemyNotificationUnitOfWork,
)


class MainProvider(Provider):
    @provide(scope=Scope.APP)
    def get_sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        return async_session_factory

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AsyncSession]:
        async with sessionmaker() as session:
            yield session

    notification_command_gateway = provide(
        notification_repository_module.SQLAlchemyNotificationRepository,
        provides=notification_gateway.NotificationCommandGateway,
        scope=Scope.REQUEST,
    )
    notification_query_gateway = provide(
        notification_repository_module.SQLAlchemyNotificationRepository,
        provides=NotificationQueryGateway,
        scope=Scope.REQUEST,
    )
    notification_unit_of_work = provide(
        SQLAlchemyNotificationUnitOfWork,
        provides=NotificationUnitOfWork,
        scope=Scope.REQUEST,
    )
    handle_wallet_transaction_interactor = provide(
        HandleWalletTransactionInteractor,
        scope=Scope.REQUEST,
    )
    list_notifications_interactor = provide(
        ListNotificationsInteractor,
        scope=Scope.REQUEST,
    )
