from typing import Protocol

from wallet_service.application.commands.apply_wallet_operation.gateway import (
    WalletCommandGateway,
)


class WalletUnitOfWork(Protocol):
    wallets: WalletCommandGateway

    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
