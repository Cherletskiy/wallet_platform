import os
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.dependencies import get_async_session, get_wallet_repository
from app.main import app
from app.models.wallet import Wallet
from app.repositories.wallet_repository import WalletRepository
from app.services.wallet_service import WalletService

load_dotenv()

TEST_DB_NAME = os.getenv("TEST_DB_NAME", "test_wallet_db")
TEST_DB_USER = os.getenv("TEST_DB_USER", "postgres")
TEST_DB_PWD = os.getenv("TEST_DB_PWD", "postgres")
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "db")
TEST_DB_PORT = os.getenv("TEST_DB_PORT", 5432)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr("app.main.run_migrations", AsyncMock())
    monkeypatch.setattr("app.main.init_db", AsyncMock())
    monkeypatch.setattr("app.main.close_db", AsyncMock())

    @asynccontextmanager
    async def test_lifespan(_: object) -> AsyncIterator[None]:
        yield

    app.router.lifespan_context = test_lifespan

    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_wallet_repository():
    """Фикстура для мокового репозитория."""
    return MagicMock(spec=WalletRepository)


@pytest.fixture
def wallet_service(mock_wallet_repository):
    """Фикстура для сервиса с моковым репозиторием."""
    return WalletService(wallet_repository=mock_wallet_repository)


@pytest.fixture(autouse=True)
def override_dependencies(mock_wallet_repository):
    async def get_test_session() -> AsyncIterator[AsyncSession]:
        yield AsyncMock(spec=AsyncSession)

    app.dependency_overrides[get_wallet_repository] = lambda: mock_wallet_repository
    app.dependency_overrides[get_async_session] = get_test_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_db():
    """Фикстура для тестовой базы данных."""
    test_dsn = f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PWD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
    engine = create_async_engine(url=test_dsn, echo=False, pool_size=5, max_overflow=10)
    from app.models.wallet import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

    yield async_session_factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def wallet(test_db):
    """Фикстура для создания тестового кошелька."""
    wallet_id = uuid.uuid4()
    async with test_db() as session:
        wallet = Wallet(id=wallet_id, balance_cent=10000)  # 100 рублей
        session.add(wallet)
        await session.commit()
    return wallet_id
