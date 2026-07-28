import uuid
from typing import Protocol

from wallet_service.domain.wallet import Wallet


class WalletBalanceGateway(Protocol):
    async def get_wallet_by_id(self, wallet_id: uuid.UUID) -> Wallet | None: ...

    async def list_wallets_by_owner(self, owner_user_id: uuid.UUID) -> list[Wallet]: ...
