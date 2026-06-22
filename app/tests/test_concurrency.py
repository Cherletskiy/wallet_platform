import asyncio
import random

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import OperationType
from app.repositories.wallet_repository import WalletRepository
from app.services.wallet_service import WalletService

pytestmark = pytest.mark.asyncio


async def test_concurrent(test_db, wallet):
    """Тест множества конкурентных операций (депозиты и снятия)."""
    wallet_id = wallet
    wallet_repo = WalletRepository()
    wallet_service = WalletService(wallet_repository=wallet_repo)
    deposit_amount = 1000  # 10 рублей
    withdrawal_amount = 500  # 5 рублей
    num_deposits = 25
    num_withdrawals = 25

    async def perform_operation(
        session: AsyncSession, operation_type: OperationType, amount: int
    ):
        """Вспомогательная функция для выполнения операции."""
        async with session.begin():
            await asyncio.sleep(random.uniform(0.01, 0.1))  # Случайная задержка
            await wallet_service.update_wallet_balance_cent(
                session=session,
                wallet_id=wallet_id,
                amount_cent=amount,
                operation_type=operation_type,
            )

    # Создаем список операций
    tasks = []
    for _ in range(num_deposits):
        async with test_db() as session:
            tasks.append(
                perform_operation(session, OperationType.DEPOSIT, deposit_amount)
            )
    for _ in range(num_withdrawals):
        async with test_db() as session:
            tasks.append(
                perform_operation(session, OperationType.WITHDRAWAL, withdrawal_amount)
            )

    # Запускаем все операции одновременно
    await asyncio.gather(*tasks, return_exceptions=True)

    # Проверяем итоговый баланс
    async with test_db() as session:
        final_balance = await wallet_service.get_wallet_balance_rub(session, wallet_id)
        expected_balance = (
            100.0
            + (num_deposits * deposit_amount - num_withdrawals * withdrawal_amount)
            / 100
        )
        assert (
            final_balance == expected_balance
        )  # 10000 + 25*1000 - 25*500 = 22500 центов (225 рублей)
