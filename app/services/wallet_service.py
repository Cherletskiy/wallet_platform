import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    WalletBalanceError,
    WalletNotFoundError,
    WalletOperationError,
)
from app.core.logging_config import setup_logger
from app.models.wallet import OperationType
from app.repositories.wallet_repository import WalletRepository

logger = setup_logger(__name__)


class WalletService:
    def __init__(self, wallet_repository: WalletRepository):
        self.wallet_repository = wallet_repository

    async def get_wallet_balance_rub(
        self, session: AsyncSession, wallet_id: uuid.UUID
    ) -> float:
        try:
            balance_cent = await self.wallet_repository.get_wallet_balance_cent(
                session, wallet_id
            )
            if balance_cent is None:
                raise WalletNotFoundError
        except WalletNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting wallet balance {wallet_id}: {e}")
            raise WalletBalanceError from e

        return round(balance_cent / 100, 2)

    async def update_wallet_balance_cent(
        self,
        session: AsyncSession,
        wallet_id: uuid.UUID,
        amount_cent: int,
        operation_type: OperationType,
    ) -> float:
        if amount_cent <= 0:
            raise InvalidAmountError

        wallet = await self.wallet_repository.get_wallet_by_id(session, wallet_id)
        if wallet is None:
            raise WalletNotFoundError

        if (
            operation_type == OperationType.WITHDRAWAL
            and wallet.balance_cent < amount_cent
        ):
            raise InsufficientFundsError

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
            raise WalletNotFoundError
        except Exception as e:
            logger.error(
                f"Error updating wallet balance {wallet_id}. "
                f"Balance before: {balance}, after: {new_balance_cent}. Error: {e}"
            )
            raise WalletOperationError from e

        return round(new_balance_cent / 100, 2)
