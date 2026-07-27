import uuid

import jwt

from auth_service.application.commands.login.dto import TokenPair
from auth_service.application.commands.refresh.dto import RefreshInput
from auth_service.application.common.security import JWTService
from auth_service.application.unit_of_work import AuthUnitOfWork
from auth_service.domain.exceptions import InvalidRefreshTokenError, UserNotFoundError
from auth_service.domain.session import RefreshSession


class RefreshInteractor:
    def __init__(
        self,
        uow: AuthUnitOfWork,
        jwt_service: JWTService,
    ) -> None:
        self._uow = uow
        self._jwt_service = jwt_service

    async def execute(self, data: RefreshInput) -> TokenPair:
        try:
            payload = self._jwt_service.decode_token(
                data.refresh_token,
                expected_type="refresh",
            )
        except jwt.PyJWTError as exc:
            raise InvalidRefreshTokenError from exc

        session_id = uuid.UUID(payload["jti"])
        user_id = uuid.UUID(payload["sub"])
        session = await self._uow.refresh_sessions.get_refresh_session_by_id(session_id)
        if session is None or not session.is_active():
            raise InvalidRefreshTokenError

        user = await self._uow.users.get_user_by_id(user_id)
        if user is None:
            raise UserNotFoundError

        new_session = RefreshSession(
            user_id=user.id,
            family_id=session.family_id,
            expires_at=self._jwt_service.refresh_session_expires_at(),
        )
        session.revoke(replaced_by_session_id=new_session.id)
        await self._uow.refresh_sessions.update_refresh_session(session)
        await self._uow.refresh_sessions.add_refresh_session(new_session)
        await self._uow.commit()

        return TokenPair(
            access_token=self._jwt_service.create_access_token(user),
            refresh_token=self._jwt_service.create_refresh_token(
                user.id,
                new_session.id,
            ),
        )
