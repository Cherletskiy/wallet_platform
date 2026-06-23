import uuid
from datetime import UTC, datetime, timedelta

import pytest

from wallet_service.domain.outbox import OutboxEvent, OutboxStatus
from wallet_service.infrastructure.sa.models import OutboxEventModel
from wallet_service.infrastructure.sa.repositories.outbox_repository import (
    SQLAlchemyOutboxRepository,
)

pytestmark = pytest.mark.asyncio


async def test_add_outbox_event_persists_row(test_db, wallet):
    wallet_id = wallet
    event = OutboxEvent(
        aggregate_type="wallet",
        aggregate_id=wallet_id,
        event_type="wallet.transaction.created",
        payload={
            "wallet_id": str(wallet_id),
            "operation_type": "DEPOSIT",
            "amount_cent": 5000,
            "balance_cent": 15000,
        },
    )

    async with test_db() as session:
        repository = SQLAlchemyOutboxRepository(session)

        await repository.add(event)
        await session.commit()

        stored_event = await session.get(OutboxEventModel, event.id)

        assert stored_event is not None
        assert stored_event.aggregate_type == "wallet"
        assert stored_event.aggregate_id == wallet_id
        assert stored_event.event_type == "wallet.transaction.created"
        assert stored_event.status == OutboxStatus.PENDING
        assert stored_event.retry_count == 0


async def test_get_waiting_returns_only_ready_events(test_db, wallet):
    now = datetime.now(UTC)
    wallet_id = wallet

    ready = OutboxEventModel(
        id=uuid.uuid4(),
        aggregate_type="wallet",
        aggregate_id=wallet_id,
        event_type="wallet.transaction.created",
        payload={"wallet_id": str(wallet_id)},
        status=OutboxStatus.PENDING,
    )
    retriable = OutboxEventModel(
        id=uuid.uuid4(),
        aggregate_type="wallet",
        aggregate_id=wallet_id,
        event_type="wallet.transaction.created",
        payload={"wallet_id": str(wallet_id)},
        status=OutboxStatus.FAILED,
        retry_count=1,
        next_retry_at=now - timedelta(minutes=1),
    )
    future_retry = OutboxEventModel(
        id=uuid.uuid4(),
        aggregate_type="wallet",
        aggregate_id=wallet_id,
        event_type="wallet.transaction.created",
        payload={"wallet_id": str(wallet_id)},
        status=OutboxStatus.FAILED,
        retry_count=1,
        next_retry_at=now + timedelta(minutes=1),
    )
    published = OutboxEventModel(
        id=uuid.uuid4(),
        aggregate_type="wallet",
        aggregate_id=wallet_id,
        event_type="wallet.transaction.created",
        payload={"wallet_id": str(wallet_id)},
        status=OutboxStatus.PUBLISHED,
        published_at=now,
    )
    dead_letter = OutboxEventModel(
        id=uuid.uuid4(),
        aggregate_type="wallet",
        aggregate_id=wallet_id,
        event_type="wallet.transaction.created",
        payload={"wallet_id": str(wallet_id)},
        status=OutboxStatus.DEAD_LETTER,
        retry_count=4,
        max_retries=3,
    )

    async with test_db() as session:
        session.add_all([ready, retriable, future_retry, published, dead_letter])
        await session.commit()

        repository = SQLAlchemyOutboxRepository(session)
        waiting = await repository.get_waiting(limit=10)

        assert {event.id for event in waiting} == {ready.id, retriable.id}


async def test_update_outbox_event_status(test_db, wallet):
    wallet_id = wallet
    event = OutboxEvent(
        aggregate_type="wallet",
        aggregate_id=wallet_id,
        event_type="wallet.transaction.created",
        payload={"wallet_id": str(wallet_id)},
    )

    async with test_db() as session:
        repository = SQLAlchemyOutboxRepository(session)
        await repository.add(event)
        await session.commit()

        event.mark_failed("Temporary broker error", now=datetime.now(UTC))
        await repository.update(event)
        await session.commit()
        session.expire_all()

        stored_event = await session.get(OutboxEventModel, event.id)

        assert stored_event is not None
        assert stored_event.status == OutboxStatus.FAILED
        assert stored_event.retry_count == 1
        assert stored_event.last_error == "Temporary broker error"
