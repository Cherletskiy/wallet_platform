import inspect
from typing import Any

from wallet_service.application.commands.outbox_processor.publisher import (
    OutboxPublisher,
)
from wallet_service.domain.outbox import OutboxEvent
from wallet_service.infrastructure.logging import setup_logger

logger = setup_logger(__name__)


class FastStreamKafkaOutboxPublisher(OutboxPublisher):
    def __init__(self, broker: Any) -> None:
        self._broker = broker

    async def publish(self, event: OutboxEvent) -> None:
        logger.info(
            "Kafka publish started: event_id=%s topic=%s",
            event.id,
            event.event_type,
        )
        published: Any = self._broker.publish(
            event.payload,
            topic=event.event_type,
            key=str(event.id).encode(),
            correlation_id=str(event.id),
        )
        if inspect.isawaitable(published):
            await published
        logger.info(
            "Kafka publish finished: event_id=%s topic=%s",
            event.id,
            event.event_type,
        )
