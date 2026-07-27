import uuid

import jwt

from auth_service.application.commands.logout.dto import LogoutInput
from auth_service.application.common.security import JWTService
from auth_service.application.unit_of_work import AuthUnitOfWork
from auth_service.domain.exceptions import InvalidRefreshTokenError


class LogoutInteractor:
    def __init__(
        self,
        uow: AuthUnitOfWork,
        jwt_service: JWTService,
    ) -> None:
        self._uow = uow
        self._jwt_service = jwt_service

    async def execute(self, data: LogoutInput) -> None:
        try:
            payload = self._jwt_service.decode_token(
                data.refresh_token,
                expected_type="refresh",
            )
        except jwt.PyJWTError as exc:
            raise InvalidRefreshTokenError from exc

        session_id = uuid.UUID(payload["jti"])
        session = await self._uow.refresh_sessions.get_refresh_session_by_id(session_id)
        if session is None or not session.is_active():
            raise InvalidRefreshTokenError

        session.revoke()
        await self._uow.refresh_sessions.update_refresh_session(session)
        await self._uow.commit()
