import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.domain.session import RefreshSession
from auth_service.domain.user import User
from auth_service.infrastructure.sa.mappers import map_refresh_session, map_user
from auth_service.infrastructure.sa.models import RefreshSessionModel, UserModel


class SQLAlchemyAuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        model = await self._session.scalar(stmt)
        return None if model is None else map_user(model)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return None if model is None else map_user(model)

    async def add_user(self, user: User) -> None:
        self._session.add(
            UserModel(
                id=user.id,
                email=user.email,
                password_hash=user.password_hash,
                role=user.role.value,
                is_active=user.is_active,
                is_email_verified=user.is_email_verified,
                created_at=user.created_at,
            )
        )

    async def add_refresh_session(self, session: RefreshSession) -> None:
        self._session.add(
            RefreshSessionModel(
                id=session.id,
                user_id=session.user_id,
                family_id=session.family_id,
                created_at=session.created_at,
                expires_at=session.expires_at,
                revoked_at=session.revoked_at,
                replaced_by_session_id=session.replaced_by_session_id,
            )
        )

    async def get_refresh_session_by_id(
        self,
        session_id: uuid.UUID,
    ) -> RefreshSession | None:
        model = await self._session.get(RefreshSessionModel, session_id)
        return None if model is None else map_refresh_session(model)

    async def update_refresh_session(self, session: RefreshSession) -> None:
        model = await self._session.get(RefreshSessionModel, session.id)
        if model is None:
            return
        model.revoked_at = session.revoked_at
        model.replaced_by_session_id = session.replaced_by_session_id
