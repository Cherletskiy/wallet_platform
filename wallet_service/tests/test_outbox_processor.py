import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from wallet_service.application.commands.outbox_processor import (
    OutboxProcessorInteractor,
)
from wallet_service.domain.outbox import OutboxEvent, OutboxStatus

pytestmark = pytest.mark.asyncio


async def test_outbox_processor_marks_event_as_published(
    outbox_processor_interactor: OutboxProcessorInteractor,
    mock_outbox_repository,
    mock_outbox_publisher,
    mock_wallet_unit_of_work,
):
    event = OutboxEvent(
        aggregate_type="wallet",
        aggregate_id=uuid.uuid4(),
        event_type="wallet.transaction.created",
        payload={"wallet_id": "1"},
    )
    mock_outbox_repository.get_waiting = AsyncMock(return_value=[event])
    mock_outbox_repository.update = AsyncMock(return_value=None)

    result = await outbox_processor_interactor.execute()

    assert result.fetched == 1
    assert result.published == 1
    assert result.retried == 0
    assert result.dead_lettered == 0
    assert event.status == OutboxStatus.PUBLISHED
    assert event.published_at is not None
    mock_outbox_publisher.publish.assert_awaited_once_with(event)
    mock_outbox_repository.update.assert_awaited_once_with(event)
    mock_wallet_unit_of_work.commit.assert_awaited_once()


async def test_outbox_processor_marks_event_for_retry_after_publish_error(
    outbox_processor_interactor: OutboxProcessorInteractor,
    mock_outbox_repository,
    mock_outbox_publisher,
    mock_wallet_unit_of_work,
):
    now = datetime(2026, 6, 23, 12, 0, tzinfo=UTC)
    event = OutboxEvent(
        aggregate_type="wallet",
        aggregate_id=uuid.uuid4(),
        event_type="wallet.transaction.created",
        payload={"wallet_id": "1"},
    )
    mock_outbox_repository.get_waiting = AsyncMock(return_value=[event])
    mock_outbox_repository.update = AsyncMock(return_value=None)
    mock_outbox_publisher.publish = AsyncMock(
        side_effect=RuntimeError("Broker is down")
    )

    original_mark_failed = event.mark_failed

    def mark_failed(reason: str, *, now: datetime | None = None) -> None:
        original_mark_failed(reason, now=now or now_value)

    now_value = now
    event.mark_failed = mark_failed  # type: ignore[method-assign]

    result = await outbox_processor_interactor.execute()

    assert result.fetched == 1
    assert result.published == 0
    assert result.retried == 1
    assert result.dead_lettered == 0
    assert event.status == OutboxStatus.FAILED
    assert event.retry_count == 1
    assert event.next_retry_at == now + event.next_retry_delay()
    assert event.last_error == "Broker is down"
    mock_outbox_repository.update.assert_awaited_once_with(event)
    mock_wallet_unit_of_work.commit.assert_awaited_once()


async def test_outbox_processor_marks_dead_letter_when_retries_are_exhausted(
    outbox_processor_interactor: OutboxProcessorInteractor,
    mock_outbox_repository,
    mock_outbox_publisher,
    mock_wallet_unit_of_work,
):
    event = OutboxEvent(
        aggregate_type="wallet",
        aggregate_id=uuid.uuid4(),
        event_type="wallet.transaction.created",
        payload={"wallet_id": "1"},
        retry_count=3,
        max_retries=3,
    )
    mock_outbox_repository.get_waiting = AsyncMock(return_value=[event])
    mock_outbox_repository.update = AsyncMock(return_value=None)
    mock_outbox_publisher.publish = AsyncMock(side_effect=RuntimeError("Still down"))

    result = await outbox_processor_interactor.execute()

    assert result.fetched == 1
    assert result.published == 0
    assert result.retried == 0
    assert result.dead_lettered == 1
    assert event.status == OutboxStatus.DEAD_LETTER
    assert event.next_retry_at is None
    mock_outbox_repository.update.assert_awaited_once_with(event)
    mock_wallet_unit_of_work.commit.assert_awaited_once()
