import uuid
from datetime import UTC, datetime, timedelta

from wallet_service.domain.outbox import OutboxEvent, OutboxStatus


def test_outbox_event_mark_failed_schedules_retry() -> None:
    event = OutboxEvent(
        aggregate_type="wallet",
        aggregate_id=uuid.uuid4(),
        event_type="wallet.transaction.created",
        payload={"wallet_id": "1"},
    )
    now = datetime(2026, 6, 23, 12, 0, tzinfo=UTC)

    event.mark_failed("Kafka is unavailable", now=now)

    assert event.status == OutboxStatus.FAILED
    assert event.retry_count == 1
    assert event.last_error == "Kafka is unavailable"
    assert event.last_error_at == now
    assert event.next_retry_at == now + timedelta(minutes=1)


def test_outbox_event_dead_letters_after_retry_limit() -> None:
    event = OutboxEvent(
        aggregate_type="wallet",
        aggregate_id=uuid.uuid4(),
        event_type="wallet.transaction.created",
        payload={"wallet_id": "1"},
        retry_count=3,
        max_retries=3,
    )

    event.mark_failed("Still failing", now=datetime(2026, 6, 23, 12, 0, tzinfo=UTC))

    assert event.status == OutboxStatus.DEAD_LETTER
    assert event.retry_count == 4
    assert event.next_retry_at is None
