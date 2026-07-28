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

from notification_service import create_app
from notification_service.application.commands.handle_wallet_transaction import (
    HandleWalletTransactionInteractor,
)
from notification_service.application.commands.handle_wallet_transaction import (
    gateway as notification_gateway,
)
from notification_service.application.queries.list_notifications.gateway import (
    NotificationQueryGateway,
)
from notification_service.application.queries.list_notifications.interactor import (
    ListNotificationsInteractor,
)
from notification_service.application.unit_of_work import NotificationUnitOfWork
from notification_service.domain.notification import WalletOperationType
from notification_service.infrastructure.sa.models import Base, NotificationModel
from notification_service.infrastructure.sa.repositories import (
    notification_repository as notification_repository_module,
)
from notification_service.infrastructure.sa.unit_of_work import (
    SQLAlchemyNotificationUnitOfWork,
)

POSTGRES_IMAGE = "postgres:15.17-trixie"
OWNER_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")


class TestProvider(Provider):
    notification_command_gateway = from_context(
        provides=notification_gateway.NotificationCommandGateway,
        scope=Scope.REQUEST,
    )
    notification_query_gateway = from_context(
        provides=NotificationQueryGateway,
        scope=Scope.REQUEST,
    )
    notification_unit_of_work = from_context(
        provides=NotificationUnitOfWork,
        scope=Scope.REQUEST,
    )
    handle_wallet_transaction_interactor = provide(
        HandleWalletTransactionInteractor,
        scope=Scope.REQUEST,
    )
    list_notifications_interactor = provide(
        ListNotificationsInteractor,
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
def mock_notification_repository() -> MagicMock:
    return MagicMock(
        spec=notification_repository_module.SQLAlchemyNotificationRepository
    )


@pytest.fixture
def mock_notification_unit_of_work() -> AsyncMock:
    return AsyncMock(spec=SQLAlchemyNotificationUnitOfWork)


@pytest.fixture
def handle_wallet_transaction_interactor(
    mock_notification_repository: MagicMock,
    mock_notification_unit_of_work: AsyncMock,
) -> HandleWalletTransactionInteractor:
    mock_notification_unit_of_work.notifications = mock_notification_repository
    return HandleWalletTransactionInteractor(mock_notification_unit_of_work)


@pytest.fixture
def list_notifications_interactor(
    mock_notification_repository: MagicMock,
) -> ListNotificationsInteractor:
    return ListNotificationsInteractor(mock_notification_repository)


@pytest_asyncio.fixture
async def app(
    mock_notification_repository: MagicMock,
    mock_notification_unit_of_work: AsyncMock,
) -> AsyncIterator[FastAPI]:
    mock_notification_unit_of_work.notifications = mock_notification_repository

    class ApiTestProvider(Provider):
        @provide(
            scope=Scope.REQUEST,
            provides=notification_gateway.NotificationCommandGateway,
        )
        def notification_command_gateway(
            self,
        ) -> notification_gateway.NotificationCommandGateway:
            return mock_notification_repository

        @provide(scope=Scope.REQUEST, provides=NotificationQueryGateway)
        def notification_query_gateway(self) -> NotificationQueryGateway:
            return mock_notification_repository

        @provide(scope=Scope.REQUEST, provides=NotificationUnitOfWork)
        def notification_unit_of_work(self) -> NotificationUnitOfWork:
            return mock_notification_unit_of_work

        handle_wallet_transaction_interactor = provide(
            HandleWalletTransactionInteractor,
            scope=Scope.REQUEST,
        )
        list_notifications_interactor = provide(
            ListNotificationsInteractor,
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
            setup_consumer=False,
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


@pytest_asyncio.fixture
async def notification_event(
    test_db: async_sessionmaker[AsyncSession],
) -> uuid.UUID:
    source_event_id = uuid.uuid4()
    async with test_db() as session:
        session.add(
            NotificationModel(
                source_event_id=source_event_id,
                user_id=OWNER_USER_ID,
                wallet_id=uuid.uuid4(),
                operation_type=WalletOperationType.DEPOSIT,
                amount_cent=5000,
                balance_cent=15000,
                message="Deposit received: 50.00 RUB. Current balance: 150.00 RUB.",
            )
        )
        await session.commit()
    return source_event_id
