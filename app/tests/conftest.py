import asyncio
import os
import uuid
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from dishka import Provider, Scope, from_context, make_async_container, provide
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from app.infrastructure.db.models import Base, WalletModel
from app.main import create_app
from app.repositories.wallet_repository import WalletRepository
from app.services.wallet_service import WalletService

load_dotenv()

POSTGRES_IMAGE = "postgres:15.17-trixie"


class TestProvider(Provider):
    session = from_context(provides=AsyncSession, scope=Scope.REQUEST)
    wallet_repository = from_context(
        provides=WalletRepository,
        scope=Scope.REQUEST,
    )
    wallet_service = provide(WalletService, scope=Scope.REQUEST)


def build_asyncpg_dsn(container: PostgresContainer) -> str:
    return (
        "postgresql+asyncpg://"
        f"{container.username}:{container.password}@"
        f"{container.get_container_host_ip()}:{container.get_exposed_port(5432)}/"
        f"{container.dbname}"
    )


@pytest.fixture
def mock_wallet_repository() -> MagicMock:
    return MagicMock(spec=WalletRepository)


@pytest.fixture
def wallet_service(mock_wallet_repository: MagicMock) -> WalletService:
    return WalletService(wallet_repository=mock_wallet_repository)


@pytest.fixture
def client(mock_wallet_repository: MagicMock) -> Iterator[TestClient]:
    request_session = AsyncMock(spec=AsyncSession)
    container = make_async_container(
        TestProvider(),
        context={
            AsyncSession: request_session,
            WalletRepository: mock_wallet_repository,
        },
        start_scope=Scope.APP,
    )
    app = create_app(container=container)

    @asynccontextmanager
    async def test_lifespan(_: object) -> AsyncIterator[None]:
        yield

    app.router.lifespan_context = test_lifespan

    with TestClient(app) as test_client:
        yield test_client

    asyncio.run(container.close())


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    with PostgresContainer(
        POSTGRES_IMAGE,
        username=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD") or os.getenv("DB_PWD", "postgres"),
        dbname=os.getenv("DB_NAME", "postgres"),
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


@pytest_asyncio.fixture
async def wallet(
    test_db: async_sessionmaker[AsyncSession],
) -> uuid.UUID:
    wallet_id = uuid.uuid4()
    async with test_db() as session:
        wallet = WalletModel(id=wallet_id, balance_cent=10000)
        session.add(wallet)
        await session.commit()
    return wallet_id
