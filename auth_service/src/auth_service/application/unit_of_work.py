from collections.abc import Awaitable
from typing import Protocol

from auth_service.application.commands.login.gateway import LoginUserGateway
from auth_service.application.commands.logout.gateway import LogoutSessionGateway
from auth_service.application.commands.refresh.gateway import RefreshSessionGateway
from auth_service.application.commands.register.gateway import RegisterUserGateway
from auth_service.application.queries.me.gateway import MeGateway


class AuthUserGateway(
    RegisterUserGateway,
    LoginUserGateway,
    MeGateway,
    Protocol,
):
    pass


class AuthRefreshSessionGateway(
    RefreshSessionGateway,
    LogoutSessionGateway,
    Protocol,
):
    pass


class AuthUnitOfWork(Protocol):
    users: AuthUserGateway
    refresh_sessions: AuthRefreshSessionGateway

    def commit(self) -> Awaitable[None]: ...

    def rollback(self) -> Awaitable[None]: ...
