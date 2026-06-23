from typing import Protocol

from wallet_service.application.outbox.gateway import OutboxGateway


class OutboxUnitOfWork(Protocol):
    outbox: OutboxGateway

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
