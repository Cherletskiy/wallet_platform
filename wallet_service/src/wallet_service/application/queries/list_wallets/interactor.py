import uuid

from wallet_service.application.queries.get_wallet_balance.gateway import (
    WalletBalanceGateway,
)
from wallet_service.domain.exceptions import WalletBalanceError
from wallet_service.domain.wallet import Wallet


class ListWalletsInteractor:
    def __init__(self, gateway: WalletBalanceGateway) -> None:
        self._gateway = gateway

    async def execute(self, owner_user_id: uuid.UUID) -> list[Wallet]:
        try:
            return await self._gateway.list_wallets_by_owner(owner_user_id)
        except Exception as exc:
            raise WalletBalanceError from exc
