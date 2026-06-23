from typing import Protocol

from wallet_service.domain.outbox import OutboxEvent


class OutboxPublisher(Protocol):
    async def publish(self, event: OutboxEvent) -> None: ...
