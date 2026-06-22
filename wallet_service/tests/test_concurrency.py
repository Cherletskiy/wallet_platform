import asyncio
import random

import pytest

from wallet_service.application.commands.apply_wallet_operation import (
    ApplyWalletOperationInput,
    ApplyWalletOperationInteractor,
)
from wallet_service.application.queries.get_wallet_balance import (
    GetWalletBalanceInteractor,
)
from wallet_service.domain.wallet import OperationType
from wallet_service.infrastructure.sa.repositories.wallet_repository import (
    SQLAlchemyWalletRepository,
)
from wallet_service.infrastructure.sa.unit_of_work import (
    SQLAlchemyWalletUnitOfWork,
)

pytestmark = pytest.mark.asyncio


async def test_concurrent(test_db, wallet):
    wallet_id = wallet
    deposit_amount = 1000  # 10 рублей
    withdrawal_amount = 500  # 5 рублей
    num_deposits = 25
    num_withdrawals = 25

    async def perform_operation(operation_type: OperationType, amount: int):
        async with test_db() as session:
            interactor = ApplyWalletOperationInteractor(
                SQLAlchemyWalletUnitOfWork(session)
            )
            await asyncio.sleep(random.uniform(0.01, 0.1))
            await interactor.execute(
                ApplyWalletOperationInput(wallet_id, amount, operation_type)
            )

    tasks = []
    for _ in range(num_deposits):
        tasks.append(perform_operation(OperationType.DEPOSIT, deposit_amount))
    for _ in range(num_withdrawals):
        tasks.append(perform_operation(OperationType.WITHDRAWAL, withdrawal_amount))

    await asyncio.gather(*tasks, return_exceptions=True)

    async with test_db() as session:
        final_balance = await GetWalletBalanceInteractor(
            SQLAlchemyWalletRepository(session)
        ).execute(wallet_id)
        expected_balance = (
            100.0
            + (num_deposits * deposit_amount - num_withdrawals * withdrawal_amount)
            / 100
        )
        assert final_balance == expected_balance
