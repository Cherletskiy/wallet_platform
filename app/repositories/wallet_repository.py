import uuid
from typing import Optional, cast

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.domain.wallet import OperationType, Wallet
from app.infrastructure.db.models import OperationModel, WalletModel
from app.infrastructure.mappers.wallet_mapper import map_wallet_model


class WalletRepository:
    async def get_wallet_by_id(
        self, session: AsyncSession, wallet_id: uuid.UUID, nowait: bool = False
    ) -> Optional[Wallet]:
        wallet_model = cast(
            Optional[WalletModel],
            await session.scalar(
                select(WalletModel)
                .where(WalletModel.id == wallet_id)
                .with_for_update(nowait=nowait)
            ),
        )
        if wallet_model is None:
            return None
        return map_wallet_model(wallet_model)

    async def get_wallet_balance_cent(
        self, session: AsyncSession, wallet_id: uuid.UUID
    ) -> Optional[int]:
        return cast(
            Optional[int],
            await session.scalar(
                select(WalletModel.balance_cent).where(WalletModel.id == wallet_id)
            ),
        )

    async def update_wallet_balance_cent(
        self, session: AsyncSession, wallet_id: uuid.UUID, balance_cent: int
    ) -> None:
        wallet_model = cast(
            Optional[WalletModel],
            await session.scalar(
                select(WalletModel)
                .where(WalletModel.id == wallet_id)
                .with_for_update()
            ),
        )
        if wallet_model is None:
            raise ValueError
        wallet_model.balance_cent = balance_cent
        session.add(wallet_model)

    async def add_operation(
        self,
        session: AsyncSession,
        wallet_id: uuid.UUID,
        operation_type: OperationType,
        amount_cent: int,
    ) -> None:
        operation = OperationModel(
            wallet_id=wallet_id, operation_type=operation_type, amount_cent=amount_cent
        )
        session.add(operation)
