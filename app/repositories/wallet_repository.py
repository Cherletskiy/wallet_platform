import uuid

from app.models.wallet import Wallet, Operation, OperationType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class WalletRepository:
    """Репозиторий для работы с БД"""

    async def get_wallet_by_id(
            self,
            session: AsyncSession,
            wallet_id: uuid.UUID,
            nowait: bool = False
    ) -> Wallet:
        """Получение кошелька по UUID.
        with_for_update (SELECT FOR UPDATE) обеспечивает корректную работу в конкурентной среде.

        Args:
            session (AsyncSession): Сессия БД
            wallet_id (uuid.UUID): ID кошелька
            nowait (bool, optional): Ожидание. Defaults to False.

        Returns:
            Wallet: Кошелек
        """
        wallet = await session.scalar(
            select(Wallet)
            .where(Wallet.id == wallet_id)
            .with_for_update(nowait=nowait)
        )
        return wallet

    async def get_wallet_balance_cent(
            self,
            session: AsyncSession,
            wallet_id: uuid.UUID
    ) -> int:
        """Получение баланса кошелька по UUID. Для чтения без блокировки.

        Args:
            session (AsyncSession): Сессия БД
            wallet_id (uuid.UUID): ID кошелька

        Returns:
            int: Баланс в копейках
        """
        return await session.scalar(
            select(Wallet.balance_cent)
            .where(Wallet.id == wallet_id)
        )

    async def update_wallet_balance_cent(
            self,
            session: AsyncSession,
            wallet_id: uuid.UUID,
            balance_cent: int) -> None:
        """Обновление баланса кошелька по id. Используется блокировка из get_wallet_by_id.

        Args:
            session (AsyncSession): Сессия БД
            wallet_id (uuid.UUID): ID кошелька
            balance_cent (int): Баланс в копейках

        Returns:
            None
        """
        wallet = await self.get_wallet_by_id(session, wallet_id)
        if wallet is None:
            raise ValueError
        wallet.balance_cent = balance_cent
        session.add(wallet)

    async def add_operation(
            self,
            session: AsyncSession,
            wallet_id: uuid.UUID,
            operation_type: OperationType,
            amount_cent: int
    ):
        """Добавление операции в таблицу operations.

        Args:
            session (AsyncSession): Сессия БД
            wallet_id (uuid.UUID): ID кошелька
            operation_type (OperationType): Тип операции DEPOSIT | WITHDRAWAL
            amount_cent (int): Сумма в копейках

        Returns:
            None
        """
        operation = Operation(wallet_id=wallet_id, operation_type=operation_type, amount_cent=amount_cent)
        session.add(operation)