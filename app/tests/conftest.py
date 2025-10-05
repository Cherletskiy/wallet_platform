import uuid

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.dependencies import get_wallet_repository
from app.models.wallet import Wallet
from app.repositories.wallet_repository import WalletRepository
from app.services.wallet_service import WalletService
from unittest.mock import MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


@pytest.fixture
def client():
    """Фикстура для синхронного HTTP-клиента FastAPI."""
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
    """Переопределение зависимостей для использования мокового репозитория."""
    app.dependency_overrides[get_wallet_repository] = lambda: mock_wallet_repository
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_db():
    """Фикстура для тестовой базы данных."""
    test_dsn = "postgresql+asyncpg://postgres:postgres@localhost:5433/test_wallet_db"
    engine = create_async_engine(
        url=test_dsn,
        echo=False,
        pool_size=5,
        max_overflow=10
    )
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