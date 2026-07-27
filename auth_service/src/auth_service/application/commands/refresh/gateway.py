import uuid
from typing import Protocol

from auth_service.domain.session import RefreshSession
from auth_service.domain.user import User


class RefreshSessionGateway(Protocol):
    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None: ...

    async def get_refresh_session_by_id(
        self,
        session_id: uuid.UUID,
    ) -> RefreshSession | None: ...

    async def add_refresh_session(self, session: RefreshSession) -> None: ...

    async def update_refresh_session(self, session: RefreshSession) -> None: ...
