from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import async_session_factory
from app.repositories.wallet_repository import WalletRepository
from app.services.wallet_service import WalletService


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

    wallet_repository = provide(WalletRepository, scope=Scope.REQUEST)
    wallet_service = provide(WalletService, scope=Scope.REQUEST)
