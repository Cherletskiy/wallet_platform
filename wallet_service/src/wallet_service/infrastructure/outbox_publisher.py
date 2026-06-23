from wallet_service.application.commands.outbox_processor.publisher import (
    OutboxPublisher,
)
from wallet_service.domain.outbox import OutboxEvent
from wallet_service.infrastructure.logging import setup_logger

logger = setup_logger(__name__)


class LoggingOutboxPublisher(OutboxPublisher):
    async def publish(self, event: OutboxEvent) -> None:
        logger.info(
            "Publishing outbox event: "
            "id=%s event_type=%s aggregate_type=%s aggregate_id=%s payload=%s",
            event.id,
            event.event_type,
            event.aggregate_type,
            event.aggregate_id,
            event.payload,
        )
