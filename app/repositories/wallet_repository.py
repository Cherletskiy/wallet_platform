import uuid
from typing import Optional, cast

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.wallet import Operation, OperationType, Wallet


class WalletRepository:
    async def get_wallet_by_id(
        self, session: AsyncSession, wallet_id: uuid.UUID, nowait: bool = False
    ) -> Optional[Wallet]:
        wallet = cast(
            Optional[Wallet],
            await session.scalar(
                select(Wallet)
                .where(Wallet.id == wallet_id)
                .with_for_update(nowait=nowait)
            ),
        )
        return wallet

    async def get_wallet_balance_cent(
        self, session: AsyncSession, wallet_id: uuid.UUID
    ) -> Optional[int]:
        return cast(
            Optional[int],
            await session.scalar(
                select(Wallet.balance_cent).where(Wallet.id == wallet_id)
            ),
        )

    async def update_wallet_balance_cent(
        self, session: AsyncSession, wallet_id: uuid.UUID, balance_cent: int
    ) -> None:
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
        amount_cent: int,
    ) -> None:
        operation = Operation(
            wallet_id=wallet_id, operation_type=operation_type, amount_cent=amount_cent
        )
        session.add(operation)
