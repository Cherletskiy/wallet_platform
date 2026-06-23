from typing import Protocol

from wallet_service.domain.outbox import OutboxEvent


class OutboxGateway(Protocol):
    async def add(self, event: OutboxEvent) -> None: ...

    async def get_waiting(self, limit: int = 100) -> list[OutboxEvent]: ...

    async def update(self, event: OutboxEvent) -> None: ...
