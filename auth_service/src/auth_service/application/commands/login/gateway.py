from typing import Protocol

from auth_service.domain.session import RefreshSession
from auth_service.domain.user import User


class LoginUserGateway(Protocol):
    async def get_user_by_email(self, email: str) -> User | None: ...

    async def add_refresh_session(self, session: RefreshSession) -> None: ...
