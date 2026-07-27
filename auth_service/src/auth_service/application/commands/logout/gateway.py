import uuid
from typing import Protocol

from auth_service.domain.session import RefreshSession


class LogoutSessionGateway(Protocol):
    async def get_refresh_session_by_id(
        self,
        session_id: uuid.UUID,
    ) -> RefreshSession | None: ...

    async def update_refresh_session(self, session: RefreshSession) -> None: ...
