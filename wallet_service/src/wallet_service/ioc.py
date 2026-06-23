from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from wallet_service.application.commands.apply_wallet_operation.gateway import (
    WalletCommandGateway,
)
from wallet_service.application.commands.apply_wallet_operation.interactor import (
    ApplyWalletOperationInteractor,
)
from wallet_service.application.outbox.gateway import OutboxGateway
from wallet_service.application.queries.get_wallet_balance.gateway import (
    WalletBalanceGateway,
)
from wallet_service.application.queries.get_wallet_balance.interactor import (
    GetWalletBalanceInteractor,
)
from wallet_service.application.unit_of_work import WalletUnitOfWork
from wallet_service.infrastructure.sa.repositories.outbox_repository import (
    SQLAlchemyOutboxRepository,
)
from wallet_service.infrastructure.sa.repositories.wallet_repository import (
    SQLAlchemyWalletRepository,
)
from wallet_service.infrastructure.sa.session import async_session_factory
from wallet_service.infrastructure.sa.unit_of_work import (
    SQLAlchemyWalletUnitOfWork,
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

    wallet_balance_gateway = provide(
        SQLAlchemyWalletRepository,
        provides=WalletBalanceGateway,
        scope=Scope.REQUEST,
    )
    wallet_command_gateway = provide(
        SQLAlchemyWalletRepository,
        provides=WalletCommandGateway,
        scope=Scope.REQUEST,
    )
    outbox_gateway = provide(
        SQLAlchemyOutboxRepository,
        provides=OutboxGateway,
        scope=Scope.REQUEST,
    )
    wallet_unit_of_work = provide(
        SQLAlchemyWalletUnitOfWork,
        provides=WalletUnitOfWork,
        scope=Scope.REQUEST,
    )
    get_wallet_balance_interactor = provide(
        GetWalletBalanceInteractor,
        scope=Scope.REQUEST,
    )
    apply_wallet_operation_interactor = provide(
        ApplyWalletOperationInteractor,
        scope=Scope.REQUEST,
    )
