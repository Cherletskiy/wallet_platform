import uuid

from auth_service.application.commands.login.dto import LoginInput, TokenPair
from auth_service.application.common.security import JWTService, PasswordHasher
from auth_service.application.unit_of_work import AuthUnitOfWork
from auth_service.domain.exceptions import InvalidCredentialsError
from auth_service.domain.session import RefreshSession


class LoginInteractor:
    def __init__(
        self,
        uow: AuthUnitOfWork,
        password_hasher: PasswordHasher,
        jwt_service: JWTService,
    ) -> None:
        self._uow = uow
        self._password_hasher = password_hasher
        self._jwt_service = jwt_service

    async def execute(self, data: LoginInput) -> TokenPair:
        user = await self._uow.users.get_user_by_email(data.email)
        if user is None or not self._password_hasher.verify_password(
            data.password, user.password_hash
        ):
            raise InvalidCredentialsError

        session = RefreshSession(
            user_id=user.id,
            family_id=uuid.uuid4(),
            expires_at=self._jwt_service.refresh_session_expires_at(),
        )
        await self._uow.refresh_sessions.add_refresh_session(session)
        await self._uow.commit()
        return TokenPair(
            access_token=self._jwt_service.create_access_token(user),
            refresh_token=self._jwt_service.create_refresh_token(user.id, session.id),
        )
