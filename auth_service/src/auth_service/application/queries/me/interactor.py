import uuid

from auth_service.application.queries.me.gateway import MeGateway
from auth_service.domain.exceptions import UserNotFoundError
from auth_service.domain.user import User


class MeInteractor:
    def __init__(self, gateway: MeGateway) -> None:
        self._gateway = gateway

    async def execute(self, user_id: uuid.UUID) -> User:
        user = await self._gateway.get_user_by_id(user_id)
        if user is None:
            raise UserNotFoundError
        return user
