import uuid

import pytest
from sqlalchemy import select

from wallet_service.domain.wallet import OperationType
from wallet_service.infrastructure.sa.models import OperationModel
from wallet_service.infrastructure.sa.repositories.wallet_repository import (
    SQLAlchemyWalletRepository,
)

pytestmark = pytest.mark.asyncio


async def test_get_wallet_by_id_success(test_db, wallet):
    wallet_id = wallet
    async with test_db() as session:
        wallet_repo = SQLAlchemyWalletRepository(session)

        wallet = await wallet_repo.get_wallet_by_id(wallet_id)

        assert wallet is not None
        assert wallet.id == wallet_id
        assert wallet.owner_user_id == uuid.UUID("11111111-1111-1111-1111-111111111111")
        assert wallet.balance_cent == 10000


async def test_get_wallet_by_id_not_found(test_db):
    wallet_id = uuid.uuid4()
    async with test_db() as session:
        wallet_repo = SQLAlchemyWalletRepository(session)

        wallet = await wallet_repo.get_wallet_by_id(wallet_id)

        assert wallet is None


async def test_update_wallet_balance_cent_success(test_db, wallet):
    wallet_id = wallet
    new_balance_cent = 20000

    async with test_db() as session:
        wallet_repo = SQLAlchemyWalletRepository(session)
        await wallet_repo.update_wallet_balance_cent(wallet_id, new_balance_cent)
        await session.commit()
        wallet = await wallet_repo.get_wallet_by_id(wallet_id)

        assert wallet is not None
        assert wallet.balance_cent == new_balance_cent


async def test_update_wallet_balance_cent_not_found(test_db):
    wallet_id = uuid.uuid4()
    new_balance_cent = 30000

    with pytest.raises(ValueError):
        async with test_db() as session:
            wallet_repo = SQLAlchemyWalletRepository(session)
            await wallet_repo.update_wallet_balance_cent(wallet_id, new_balance_cent)


async def test_add_operation_success(test_db, wallet):
    wallet_id = wallet
    amount_cent = 1000
    operation_type = OperationType.DEPOSIT

    async with test_db() as session:
        wallet_repo = SQLAlchemyWalletRepository(session)
        await wallet_repo.add_operation(wallet_id, operation_type, amount_cent)
        await session.commit()
        operation = await session.scalar(
            select(OperationModel).where(OperationModel.wallet_id == wallet_id).limit(1)
        )

        assert operation is not None
        assert operation.wallet_id == wallet_id
        assert operation.operation_type == operation_type
        assert operation.amount_cent == amount_cent


async def test_create_wallet_success(test_db):
    owner_user_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    async with test_db() as session:
        wallet_repo = SQLAlchemyWalletRepository(session)
        wallet = await wallet_repo.create_wallet(owner_user_id)
        await session.commit()

        persisted = await wallet_repo.get_wallet_by_id(wallet.id)

        assert persisted is not None
        assert persisted.owner_user_id == owner_user_id
        assert persisted.balance_cent == 0
