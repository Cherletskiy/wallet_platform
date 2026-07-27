import os
import uuid
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

import httpx
import pytest
import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from auth_service import create_app
from auth_service.application.commands.login.dto import TokenPair
from auth_service.application.commands.login.interactor import LoginInteractor
from auth_service.application.commands.logout.interactor import LogoutInteractor
from auth_service.application.commands.refresh.interactor import RefreshInteractor
from auth_service.application.commands.register.interactor import RegisterInteractor
from auth_service.application.common.security import JWTService
from auth_service.application.queries.me.interactor import MeInteractor
from auth_service.config import config
from auth_service.domain.user import Role, User
from auth_service.infrastructure.sa.models import Base

POSTGRES_IMAGE = "postgres:15.17-trixie"


def build_asyncpg_dsn(container: PostgresContainer) -> str:
    return (
        "postgresql+asyncpg://"
        f"{container.username}:{container.password}@"
        f"{container.get_container_host_ip()}:{container.get_exposed_port(5432)}/"
        f"{container.dbname}"
    )


@pytest.fixture
def mock_register_interactor() -> AsyncMock:
    return AsyncMock(spec=RegisterInteractor)


@pytest.fixture
def mock_login_interactor() -> AsyncMock:
    return AsyncMock(spec=LoginInteractor)


@pytest.fixture
def mock_refresh_interactor() -> AsyncMock:
    return AsyncMock(spec=RefreshInteractor)


@pytest.fixture
def mock_logout_interactor() -> AsyncMock:
    return AsyncMock(spec=LogoutInteractor)


@pytest.fixture
def mock_me_interactor() -> AsyncMock:
    return AsyncMock(spec=MeInteractor)


@pytest.fixture
def jwt_service() -> JWTService:
    return JWTService(config)


@pytest_asyncio.fixture
async def app(
    mock_register_interactor: AsyncMock,
    mock_login_interactor: AsyncMock,
    mock_refresh_interactor: AsyncMock,
    mock_logout_interactor: AsyncMock,
    mock_me_interactor: AsyncMock,
    jwt_service: JWTService,
) -> AsyncIterator[FastAPI]:
    class ApiTestProvider(Provider):
        @provide(scope=Scope.REQUEST, provides=RegisterInteractor)
        def register_interactor(self) -> RegisterInteractor:
            return mock_register_interactor

        @provide(scope=Scope.REQUEST, provides=LoginInteractor)
        def login_interactor(self) -> LoginInteractor:
            return mock_login_interactor

        @provide(scope=Scope.REQUEST, provides=RefreshInteractor)
        def refresh_interactor(self) -> RefreshInteractor:
            return mock_refresh_interactor

        @provide(scope=Scope.REQUEST, provides=LogoutInteractor)
        def logout_interactor(self) -> LogoutInteractor:
            return mock_logout_interactor

        @provide(scope=Scope.REQUEST, provides=MeInteractor)
        def me_interactor(self) -> MeInteractor:
            return mock_me_interactor

        @provide(scope=Scope.APP, provides=JWTService)
        def jwt_service_provider(self) -> JWTService:
            return jwt_service

    container = make_async_container(ApiTestProvider(), start_scope=Scope.RUNTIME)
    async with container(scope=Scope.APP) as app_container:

        @asynccontextmanager
        async def test_lifespan(_: object) -> AsyncIterator[None]:
            yield

        app = create_app(setup_di=False, lifespan_context=test_lifespan)
        setup_dishka(app_container, app)
        yield app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    with PostgresContainer(
        POSTGRES_IMAGE,
        username=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        dbname=os.getenv("POSTGRES_DB", "postgres"),
    ) as container:
        yield container


@pytest_asyncio.fixture(scope="session")
async def engine(postgres_container: PostgresContainer) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(
        url=build_asyncpg_dsn(postgres_container),
        echo=False,
        pool_size=5,
        max_overflow=10,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(
    engine: AsyncEngine,
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    yield session_factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def test_user() -> User:
    return User(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        email="user@example.com",
        password_hash="hash",
        role=Role.USER,
    )


@pytest.fixture
def issued_token_pair() -> TokenPair:
    return TokenPair(access_token="access-token", refresh_token="refresh-token")
