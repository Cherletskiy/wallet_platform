from typing import Protocol

from auth_service.domain.user import User


class RegisterUserGateway(Protocol):
    async def get_user_by_email(self, email: str) -> User | None: ...

    async def add_user(self, user: User) -> None: ...
