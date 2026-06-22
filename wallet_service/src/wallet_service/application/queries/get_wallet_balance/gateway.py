import uuid
from typing import Protocol


class WalletBalanceGateway(Protocol):
    async def get_wallet_balance_cent(self, wallet_id: uuid.UUID) -> int | None: ...
