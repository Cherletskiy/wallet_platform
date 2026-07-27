import uuid
from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from wallet_service.domain.wallet import OperationType, Wallet
from wallet_service.infrastructure.sa.mappers import map_wallet_model
from wallet_service.infrastructure.sa.models import OperationModel, WalletModel


class SQLAlchemyWalletRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_wallet(self, owner_user_id: uuid.UUID) -> Wallet:
        wallet_model = WalletModel(owner_user_id=owner_user_id, balance_cent=0)
        self._session.add(wallet_model)
        await self._session.flush()
        return map_wallet_model(wallet_model)

    async def get_wallet_by_id(
        self,
        wallet_id: uuid.UUID,
        nowait: bool = False,
    ) -> Wallet | None:
        wallet_model = cast(
            WalletModel | None,
            await self._session.scalar(
                select(WalletModel)
                .where(WalletModel.id == wallet_id)
                .with_for_update(nowait=nowait)
            ),
        )
        if wallet_model is None:
            return None
        return map_wallet_model(wallet_model)

    async def update_wallet_balance_cent(
        self,
        wallet_id: uuid.UUID,
        balance_cent: int,
    ) -> None:
        wallet_model = cast(
            WalletModel | None,
            await self._session.scalar(
                select(WalletModel).where(WalletModel.id == wallet_id).with_for_update()
            ),
        )
        if wallet_model is None:
            raise ValueError
        wallet_model.balance_cent = balance_cent
        self._session.add(wallet_model)

    async def add_operation(
        self,
        wallet_id: uuid.UUID,
        operation_type: OperationType,
        amount_cent: int,
    ) -> None:
        self._session.add(
            OperationModel(
                wallet_id=wallet_id,
                operation_type=operation_type,
                amount_cent=amount_cent,
            )
        )
