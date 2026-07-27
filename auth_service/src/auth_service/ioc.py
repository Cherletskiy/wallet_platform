from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from auth_service.application.commands.login.gateway import LoginUserGateway
from auth_service.application.commands.login.interactor import LoginInteractor
from auth_service.application.commands.logout.gateway import LogoutSessionGateway
from auth_service.application.commands.logout.interactor import LogoutInteractor
from auth_service.application.commands.refresh.gateway import RefreshSessionGateway
from auth_service.application.commands.refresh.interactor import RefreshInteractor
from auth_service.application.commands.register.gateway import RegisterUserGateway
from auth_service.application.commands.register.interactor import RegisterInteractor
from auth_service.application.common.security import JWTService, PasswordHasher
from auth_service.application.queries.me.gateway import MeGateway
from auth_service.application.queries.me.interactor import MeInteractor
from auth_service.application.unit_of_work import AuthUnitOfWork
from auth_service.config import config
from auth_service.infrastructure.sa.repositories.auth_repository import (
    SQLAlchemyAuthRepository,
)
from auth_service.infrastructure.sa.session import async_session_factory
from auth_service.infrastructure.sa.unit_of_work import SQLAlchemyAuthUnitOfWork


class MainProvider(Provider):
    @provide(scope=Scope.APP)
    def get_sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        return async_session_factory

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AsyncSession]:
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.APP)
    def get_password_hasher(self) -> PasswordHasher:
        return PasswordHasher()

    @provide(scope=Scope.APP)
    def get_jwt_service(self) -> JWTService:
        return JWTService(config)

    register_user_gateway = provide(
        SQLAlchemyAuthRepository,
        provides=RegisterUserGateway,
        scope=Scope.REQUEST,
    )
    login_user_gateway = provide(
        SQLAlchemyAuthRepository,
        provides=LoginUserGateway,
        scope=Scope.REQUEST,
    )
    refresh_session_gateway = provide(
        SQLAlchemyAuthRepository,
        provides=RefreshSessionGateway,
        scope=Scope.REQUEST,
    )
    logout_session_gateway = provide(
        SQLAlchemyAuthRepository,
        provides=LogoutSessionGateway,
        scope=Scope.REQUEST,
    )
    me_gateway = provide(
        SQLAlchemyAuthRepository,
        provides=MeGateway,
        scope=Scope.REQUEST,
    )
    auth_unit_of_work = provide(
        SQLAlchemyAuthUnitOfWork,
        provides=AuthUnitOfWork,
        scope=Scope.REQUEST,
    )
    register_interactor = provide(RegisterInteractor, scope=Scope.REQUEST)
    login_interactor = provide(LoginInteractor, scope=Scope.REQUEST)
    refresh_interactor = provide(RefreshInteractor, scope=Scope.REQUEST)
    logout_interactor = provide(LogoutInteractor, scope=Scope.REQUEST)
    me_interactor = provide(MeInteractor, scope=Scope.REQUEST)
