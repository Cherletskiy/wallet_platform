from typing import Protocol

from wallet_service.application.commands.apply_wallet_operation.gateway import (
    WalletCommandGateway,
)
from wallet_service.application.outbox.gateway import OutboxGateway


class WalletUnitOfWork(Protocol):
    wallets: WalletCommandGateway
    outbox: OutboxGateway

    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
