import uuid
from unittest.mock import AsyncMock

import pytest

from wallet_service.domain.outbox import OutboxEvent
from wallet_service.infrastructure.faststream.publisher import (
    FastStreamKafkaOutboxPublisher,
)

pytestmark = pytest.mark.asyncio


async def test_faststream_publisher_encodes_kafka_key() -> None:
    broker = AsyncMock()
    wallet_id = uuid.uuid4()
    event = OutboxEvent(
        aggregate_type="wallet",
        aggregate_id=wallet_id,
        event_type="wallet.transaction.created",
        payload={"wallet_id": str(wallet_id)},
    )
    publisher = FastStreamKafkaOutboxPublisher(broker)

    await publisher.publish(event)

    broker.publish.assert_awaited_once_with(
        event.payload,
        topic=event.event_type,
        key=str(event.id).encode(),
        correlation_id=str(event.id),
    )
