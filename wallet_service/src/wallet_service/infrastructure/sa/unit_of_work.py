from sqlalchemy.ext.asyncio import AsyncSession

from wallet_service.infrastructure.sa.repositories.wallet_repository import (
    SQLAlchemyWalletRepository,
)


class SQLAlchemyWalletUnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.wallets = SQLAlchemyWalletRepository(session)

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
