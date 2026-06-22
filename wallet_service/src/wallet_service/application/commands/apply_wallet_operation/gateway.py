import uuid
from typing import Protocol

from wallet_service.domain.wallet import OperationType, Wallet


class WalletCommandGateway(Protocol):
    async def get_wallet_by_id(
        self,
        wallet_id: uuid.UUID,
        nowait: bool = False,
    ) -> Wallet | None: ...

    async def update_wallet_balance_cent(
        self,
        wallet_id: uuid.UUID,
        balance_cent: int,
    ) -> None: ...

    async def add_operation(
        self,
        wallet_id: uuid.UUID,
        operation_type: OperationType,
        amount_cent: int,
    ) -> None: ...
