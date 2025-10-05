import uuid
import pytest
from sqlalchemy import select
from app.repositories.wallet_repository import WalletRepository
from app.models.wallet import Wallet, Operation, OperationType


pytestmark = pytest.mark.asyncio


async def test_get_wallet_by_id_success(test_db, wallet):
    """Тест успешного получения кошелька по ID."""
    wallet_id = wallet
    wallet_repo = WalletRepository()

    async with test_db() as session:
        wallet = await wallet_repo.get_wallet_by_id(session, wallet_id)

        assert wallet is not None
        assert wallet.id == wallet_id
        assert wallet.balance_cent == 10000


async def test_get_wallet_by_id_not_found(test_db):
    """Тест получения несуществующего кошелька."""
    wallet_id = uuid.uuid4()  # Несуществующий ID
    wallet_repo = WalletRepository()

    async with test_db() as session:
        wallet = await wallet_repo.get_wallet_by_id(session, wallet_id)

        assert wallet is None


async def test_get_wallet_balance_cent_success(test_db, wallet):
    """Тест успешного получения баланса кошелька."""
    wallet_id = wallet
    wallet_repo = WalletRepository()

    async with test_db() as session:
        balance_cent = await wallet_repo.get_wallet_balance_cent(session, wallet_id)

        assert balance_cent == 10000  # 100 рублей


async def test_get_wallet_balance_cent_not_found(test_db):
    """Тест получения баланса несуществующего кошелька."""
    wallet_id = uuid.uuid4()  # Несуществующий ID
    wallet_repo = WalletRepository()

    async with test_db() as session:
        balance_cent = await wallet_repo.get_wallet_balance_cent(session, wallet_id)

        assert balance_cent is None


async def test_update_wallet_balance_cent_success(test_db, wallet):
    """Тест успешного обновления баланса кошелька."""
    wallet_id = wallet
    wallet_repo = WalletRepository()
    new_balance_cent = 20000  # 200 рублей

    async with test_db() as session:
        await wallet_repo.update_wallet_balance_cent(session, wallet_id, new_balance_cent)
        await session.commit()
        wallet = await wallet_repo.get_wallet_by_id(session, wallet_id)

        assert wallet is not None
        assert wallet.balance_cent == new_balance_cent


async def test_update_wallet_balance_cent_not_found(test_db):
    """Тест обновления баланса несуществующего кошелька."""
    wallet_id = uuid.uuid4()  # Несуществующий ID
    wallet_repo = WalletRepository()
    new_balance_cent = 30000

    with pytest.raises(ValueError):
        async with test_db() as session:
            await wallet_repo.update_wallet_balance_cent(session, wallet_id, new_balance_cent)


async def test_add_operation_success(test_db, wallet):
    """Тест успешного добавления операции кошелька."""
    wallet_id = wallet
    wallet_repo = WalletRepository()
    amount_cent = 1000
    operation_type = OperationType.DEPOSIT

    async with test_db() as session:
        await wallet_repo.add_operation(session, wallet_id, operation_type, amount_cent)
        await session.commit()
        operation = await session.scalar(
            select(Operation)
            .where(Operation.wallet_id == wallet_id)
            .limit(1)
        )

        assert operation is not None
        assert operation.wallet_id == wallet_id
        assert operation.operation_type == operation_type
        assert operation.amount_cent == amount_cent