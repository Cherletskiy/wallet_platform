import pytest
from sqlalchemy import select

from auth_service.application.commands.login.dto import LoginInput
from auth_service.application.commands.login.interactor import LoginInteractor
from auth_service.application.commands.logout.dto import LogoutInput
from auth_service.application.commands.logout.interactor import LogoutInteractor
from auth_service.application.commands.refresh.dto import RefreshInput
from auth_service.application.commands.refresh.interactor import RefreshInteractor
from auth_service.application.commands.register.dto import RegisterInput
from auth_service.application.commands.register.interactor import RegisterInteractor
from auth_service.application.common.security import JWTService, PasswordHasher
from auth_service.application.queries.me.interactor import MeInteractor
from auth_service.config import config
from auth_service.domain.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from auth_service.infrastructure.sa.models import RefreshSessionModel, UserModel
from auth_service.infrastructure.sa.unit_of_work import SQLAlchemyAuthUnitOfWork

pytestmark = pytest.mark.asyncio


async def test_register_persists_user(
    test_db,
) -> None:
    async with test_db() as session:
        interactor = RegisterInteractor(
            SQLAlchemyAuthUnitOfWork(session), PasswordHasher()
        )
        user = await interactor.execute(
            RegisterInput(email="user@example.com", password="Password123")
        )

    async with test_db() as session:
        persisted = await session.get(UserModel, user.id)
        assert persisted is not None
        assert persisted.email == "user@example.com"


async def test_register_raises_for_duplicate_email(test_db) -> None:
    async with test_db() as session:
        interactor = RegisterInteractor(
            SQLAlchemyAuthUnitOfWork(session), PasswordHasher()
        )
        await interactor.execute(
            RegisterInput(email="user@example.com", password="Password123")
        )

    async with test_db() as session:
        interactor = RegisterInteractor(
            SQLAlchemyAuthUnitOfWork(session), PasswordHasher()
        )
        with pytest.raises(EmailAlreadyExistsError):
            await interactor.execute(
                RegisterInput(email="user@example.com", password="Password123")
            )


async def test_login_creates_refresh_session(test_db) -> None:
    async with test_db() as session:
        register = RegisterInteractor(
            SQLAlchemyAuthUnitOfWork(session), PasswordHasher()
        )
        user = await register.execute(
            RegisterInput(email="user@example.com", password="Password123")
        )

    async with test_db() as session:
        login = LoginInteractor(
            SQLAlchemyAuthUnitOfWork(session),
            PasswordHasher(),
            JWTService(config),
        )
        token_pair = await login.execute(
            LoginInput(email="user@example.com", password="Password123")
        )

        assert token_pair.access_token
        assert token_pair.refresh_token

    async with test_db() as session:
        rows = await session.execute(
            select(RefreshSessionModel).where(RefreshSessionModel.user_id == user.id)
        )
        assert rows.scalar_one() is not None


async def test_login_raises_for_invalid_credentials(test_db) -> None:
    async with test_db() as session:
        register = RegisterInteractor(
            SQLAlchemyAuthUnitOfWork(session), PasswordHasher()
        )
        await register.execute(
            RegisterInput(email="user@example.com", password="Password123")
        )

    async with test_db() as session:
        login = LoginInteractor(
            SQLAlchemyAuthUnitOfWork(session),
            PasswordHasher(),
            JWTService(config),
        )
        with pytest.raises(InvalidCredentialsError):
            await login.execute(
                LoginInput(email="user@example.com", password="WrongPassword123")
            )


async def test_refresh_rotates_session(test_db) -> None:
    async with test_db() as session:
        register = RegisterInteractor(
            SQLAlchemyAuthUnitOfWork(session), PasswordHasher()
        )
        await register.execute(
            RegisterInput(email="user@example.com", password="Password123")
        )

    async with test_db() as session:
        login = LoginInteractor(
            SQLAlchemyAuthUnitOfWork(session),
            PasswordHasher(),
            JWTService(config),
        )
        token_pair = await login.execute(
            LoginInput(email="user@example.com", password="Password123")
        )

    async with test_db() as session:
        refresh = RefreshInteractor(
            SQLAlchemyAuthUnitOfWork(session), JWTService(config)
        )
        rotated = await refresh.execute(
            RefreshInput(refresh_token=token_pair.refresh_token)
        )

        assert rotated.access_token
        assert rotated.refresh_token != token_pair.refresh_token

    async with test_db() as session:
        rows = await session.execute(select(RefreshSessionModel))
        sessions = list(rows.scalars().all())
        assert len(sessions) == 2
        assert any(item.revoked_at is not None for item in sessions)


async def test_refresh_rejects_revoked_session(test_db) -> None:
    async with test_db() as session:
        register = RegisterInteractor(
            SQLAlchemyAuthUnitOfWork(session), PasswordHasher()
        )
        await register.execute(
            RegisterInput(email="user@example.com", password="Password123")
        )

    async with test_db() as session:
        login = LoginInteractor(
            SQLAlchemyAuthUnitOfWork(session),
            PasswordHasher(),
            JWTService(config),
        )
        token_pair = await login.execute(
            LoginInput(email="user@example.com", password="Password123")
        )

    async with test_db() as session:
        refresh = RefreshInteractor(
            SQLAlchemyAuthUnitOfWork(session), JWTService(config)
        )
        await refresh.execute(RefreshInput(refresh_token=token_pair.refresh_token))

    async with test_db() as session:
        refresh = RefreshInteractor(
            SQLAlchemyAuthUnitOfWork(session), JWTService(config)
        )
        with pytest.raises(InvalidRefreshTokenError):
            await refresh.execute(RefreshInput(refresh_token=token_pair.refresh_token))


async def test_logout_revokes_refresh_session(test_db) -> None:
    async with test_db() as session:
        register = RegisterInteractor(
            SQLAlchemyAuthUnitOfWork(session), PasswordHasher()
        )
        await register.execute(
            RegisterInput(email="user@example.com", password="Password123")
        )

    async with test_db() as session:
        login = LoginInteractor(
            SQLAlchemyAuthUnitOfWork(session),
            PasswordHasher(),
            JWTService(config),
        )
        token_pair = await login.execute(
            LoginInput(email="user@example.com", password="Password123")
        )

    async with test_db() as session:
        logout = LogoutInteractor(SQLAlchemyAuthUnitOfWork(session), JWTService(config))
        await logout.execute(LogoutInput(refresh_token=token_pair.refresh_token))

    async with test_db() as session:
        rows = await session.execute(select(RefreshSessionModel))
        refresh_session = rows.scalar_one()
        assert refresh_session.revoked_at is not None


async def test_me_returns_registered_user(test_db) -> None:
    async with test_db() as session:
        register = RegisterInteractor(
            SQLAlchemyAuthUnitOfWork(session), PasswordHasher()
        )
        user = await register.execute(
            RegisterInput(email="user@example.com", password="Password123")
        )

    async with test_db() as session:
        me = MeInteractor(SQLAlchemyAuthUnitOfWork(session).users)
        current_user = await me.execute(user.id)

        assert current_user.id == user.id
        assert current_user.email == user.email
