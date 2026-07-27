from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.application.unit_of_work import (
    AuthRefreshSessionGateway,
    AuthUserGateway,
)
from auth_service.infrastructure.sa.repositories.auth_repository import (
    SQLAlchemyAuthRepository,
)


class SQLAlchemyAuthUnitOfWork:
    users: AuthUserGateway
    refresh_sessions: AuthRefreshSessionGateway

    def __init__(self, session: AsyncSession) -> None:
        repository = SQLAlchemyAuthRepository(session)
        self._session = session
        self.users = repository
        self.refresh_sessions = repository

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
