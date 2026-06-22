import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import setup_logger
from app.models.wallet import OperationType
from app.repositories.wallet_repository import WalletRepository

logger = setup_logger(__name__)


class WalletService:
    """Сервис для работы с кошельками."""

    def __init__(self, wallet_repository: WalletRepository):
        self.wallet_repository = wallet_repository

    async def get_wallet_balance_rub(
        self, session: AsyncSession, wallet_id: uuid.UUID
    ) -> float:
        """Получение баланса кошелька в рублях по UUID кошелька.

        Args:
            session (AsyncSession): Сессия БД
            wallet_id (uuid.UUID): ID кошелька

        Returns:
            float: Баланс в рублях
        """
        try:
            balance_cent = await self.wallet_repository.get_wallet_balance_cent(
                session, wallet_id
            )
            if balance_cent is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting wallet balance {wallet_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error getting wallet balance",
            )

        return round(balance_cent / 100, 2)

    async def update_wallet_balance_cent(
        self,
        session: AsyncSession,
        wallet_id: uuid.UUID,
        amount_cent: int,
        operation_type: OperationType,
    ) -> float:
        """Обновление баланса кошелька по UUID, типу операции и сумме.

        Args:
            session (AsyncSession): Сессия БД
            wallet_id (uuid.UUID): ID кошелька
            amount_cent (int): Сумма в центах
            operation_type (OperationType): Тип операции DEPOSIT | WITHDRAWAL

        Returns:
            float: Баланс в рублях
        """
        if amount_cent <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than 0",
            )

        wallet = await self.wallet_repository.get_wallet_by_id(session, wallet_id)
        if wallet is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
            )

        if (
            operation_type == OperationType.WITHDRAWAL
            and wallet.balance_cent < amount_cent
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough balance"
            )

        balance = wallet.balance_cent
        new_balance_cent = (
            balance - amount_cent
            if operation_type == OperationType.WITHDRAWAL
            else balance + amount_cent
        )

        try:
            await self.wallet_repository.update_wallet_balance_cent(
                session, wallet_id, new_balance_cent
            )
            await self.wallet_repository.add_operation(
                session, wallet_id, operation_type, amount_cent
            )
            await session.commit()
            logger.info(
                f"Updated wallet balance id: {wallet_id}."
                f"Operation type: {operation_type}."
                f"Balance_cent before: {balance}, after: {new_balance_cent}"
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
            )
        except Exception as e:
            logger.error(
                f"Error updating wallet balance {wallet_id}. "
                f"Balance before: {balance}, after: {new_balance_cent}. Error: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error updating wallet balance",
            )

        return round(new_balance_cent / 100, 2)
