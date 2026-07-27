from auth_service.application.commands.register.dto import RegisterInput
from auth_service.application.common.security import PasswordHasher
from auth_service.application.unit_of_work import AuthUnitOfWork
from auth_service.domain.exceptions import EmailAlreadyExistsError
from auth_service.domain.user import User


class RegisterInteractor:
    def __init__(
        self,
        uow: AuthUnitOfWork,
        password_hasher: PasswordHasher,
    ) -> None:
        self._uow = uow
        self._password_hasher = password_hasher

    async def execute(self, data: RegisterInput) -> User:
        existing = await self._uow.users.get_user_by_email(data.email)
        if existing is not None:
            raise EmailAlreadyExistsError

        user = User(
            email=data.email,
            password_hash=self._password_hasher.hash_password(data.password),
        )
        await self._uow.users.add_user(user)
        await self._uow.commit()
        return user
