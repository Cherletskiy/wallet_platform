import uuid
from typing import Protocol

from auth_service.domain.user import User


class MeGateway(Protocol):
    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None: ...
