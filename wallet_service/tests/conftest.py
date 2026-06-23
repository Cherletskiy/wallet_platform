import os
import uuid
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import pytest_asyncio
from dishka import Provider, Scope, from_context, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from wallet_service import create_app
from wallet_service.application.commands.apply_wallet_operation.gateway import (
    WalletCommandGateway,
)
from wallet_service.application.commands.apply_wallet_operation.interactor import (
    ApplyWalletOperationInteractor,
)
from wallet_service.application.commands.outbox_processor.interactor import (
    OutboxProcessorInteractor,
)
from wallet_service.application.commands.outbox_processor.publisher import (
    OutboxPublisher,
)
from wallet_service.application.outbox.gateway import OutboxGateway
from wallet_service.application.queries.get_wallet_balance.gateway import (
    WalletBalanceGateway,
)
from wallet_service.application.queries.get_wallet_balance.interactor import (
    GetWalletBalanceInteractor,
)
from wallet_service.application.unit_of_work import WalletUnitOfWork
from wallet_service.infrastructure.sa.models import Base, WalletModel
from wallet_service.infrastructure.sa.repositories.outbox_repository import (
    SQLAlchemyOutboxRepository,
)
from wallet_service.infrastructure.sa.repositories.wallet_repository import (
    SQLAlchemyWalletRepository,
)
from wallet_service.infrastructure.sa.unit_of_work import (
    SQLAlchemyWalletUnitOfWork,
)

POSTGRES_IMAGE = "postgres:15.17-trixie"


class TestProvider(Provider):
    wallet_balance_gateway = from_context(
        provides=WalletBalanceGateway,
        scope=Scope.REQUEST,
    )
    wallet_command_gateway = from_context(
        provides=WalletCommandGateway,
        scope=Scope.REQUEST,
    )
    wallet_unit_of_work = from_context(
        provides=WalletUnitOfWork,
        scope=Scope.REQUEST,
    )
    outbox_gateway = from_context(
        provides=OutboxGateway,
        scope=Scope.REQUEST,
    )
    get_wallet_balance_interactor = provide(
        GetWalletBalanceInteractor,
        scope=Scope.REQUEST,
    )
    apply_wallet_operation_interactor = provide(
        ApplyWalletOperationInteractor,
        scope=Scope.REQUEST,
    )


def build_asyncpg_dsn(container: PostgresContainer) -> str:
    return (
        "postgresql+asyncpg://"
        f"{container.username}:{container.password}@"
        f"{container.get_container_host_ip()}:{container.get_exposed_port(5432)}/"
        f"{container.dbname}"
    )


@pytest.fixture
def mock_wallet_repository() -> MagicMock:
    return MagicMock(spec=SQLAlchemyWalletRepository)


@pytest.fixture
def mock_outbox_repository() -> MagicMock:
    return MagicMock(spec=SQLAlchemyOutboxRepository)


@pytest.fixture
def mock_wallet_unit_of_work() -> AsyncMock:
    return AsyncMock(spec=SQLAlchemyWalletUnitOfWork)


@pytest.fixture
def mock_outbox_publisher() -> AsyncMock:
    return AsyncMock(spec=OutboxPublisher)


@pytest.fixture
def get_wallet_balance_interactor(
    mock_wallet_repository: MagicMock,
) -> GetWalletBalanceInteractor:
    return GetWalletBalanceInteractor(mock_wallet_repository)


@pytest.fixture
def apply_wallet_operation_interactor(
    mock_wallet_repository: MagicMock,
    mock_outbox_repository: MagicMock,
    mock_wallet_unit_of_work: AsyncMock,
) -> ApplyWalletOperationInteractor:
    mock_wallet_unit_of_work.wallets = mock_wallet_repository
    mock_wallet_unit_of_work.outbox = mock_outbox_repository
    return ApplyWalletOperationInteractor(mock_wallet_unit_of_work)


@pytest.fixture
def outbox_processor_interactor(
    mock_outbox_repository: MagicMock,
    mock_outbox_publisher: AsyncMock,
    mock_wallet_unit_of_work: AsyncMock,
) -> OutboxProcessorInteractor:
    mock_wallet_unit_of_work.outbox = mock_outbox_repository
    return OutboxProcessorInteractor(mock_wallet_unit_of_work, mock_outbox_publisher)


@pytest_asyncio.fixture
async def app(
    mock_wallet_repository: MagicMock,
    mock_outbox_repository: MagicMock,
    mock_wallet_unit_of_work: AsyncMock,
) -> AsyncIterator:
    mock_wallet_unit_of_work.wallets = mock_wallet_repository
    mock_wallet_unit_of_work.outbox = mock_outbox_repository

    class ApiTestProvider(Provider):
        @provide(
            scope=Scope.REQUEST,
            provides=WalletBalanceGateway,
        )
        def wallet_balance_gateway(self) -> WalletBalanceGateway:
            return mock_wallet_repository

        @provide(
            scope=Scope.REQUEST,
            provides=WalletCommandGateway,
        )
        def wallet_command_gateway(self) -> WalletCommandGateway:
            return mock_wallet_repository

        @provide(
            scope=Scope.REQUEST,
            provides=WalletUnitOfWork,
        )
        def wallet_unit_of_work(self) -> WalletUnitOfWork:
            return mock_wallet_unit_of_work

        @provide(
            scope=Scope.REQUEST,
            provides=OutboxGateway,
        )
        def outbox_gateway(self) -> OutboxGateway:
            return mock_outbox_repository

        get_wallet_balance_interactor = provide(
            GetWalletBalanceInteractor,
            scope=Scope.REQUEST,
        )
        apply_wallet_operation_interactor = provide(
            ApplyWalletOperationInteractor,
            scope=Scope.REQUEST,
        )

    container = make_async_container(
        ApiTestProvider(),
        start_scope=Scope.RUNTIME,
    )
    async with container(scope=Scope.APP) as app_container:

        @asynccontextmanager
        async def test_lifespan(_: object) -> AsyncIterator[None]:
            yield

        app = create_app(
            setup_di=False,
            lifespan_context=test_lifespan,
        )
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
        session.add(WalletModel(id=wallet_id, balance_cent=10000))
        await session.commit()
    return wallet_id
