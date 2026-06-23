from datetime import UTC, datetime
from typing import cast

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from wallet_service.domain.outbox import OutboxEvent, OutboxStatus
from wallet_service.infrastructure.sa.models import OutboxEventModel


def map_outbox_event_model(model: OutboxEventModel) -> OutboxEvent:
    return OutboxEvent(
        id=model.id,
        aggregate_type=model.aggregate_type,
        aggregate_id=model.aggregate_id,
        event_type=model.event_type,
        payload=model.payload,
        status=model.status,
        retry_count=model.retry_count,
        max_retries=model.max_retries,
        created_at=model.created_at,
        published_at=model.published_at,
        next_retry_at=model.next_retry_at,
        last_error=model.last_error,
        last_error_at=model.last_error_at,
    )


class SQLAlchemyOutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, event: OutboxEvent) -> None:
        self._session.add(
            OutboxEventModel(
                id=event.id,
                aggregate_type=event.aggregate_type,
                aggregate_id=event.aggregate_id,
                event_type=event.event_type,
                payload=event.payload,
                status=event.status,
                retry_count=event.retry_count,
                max_retries=event.max_retries,
                created_at=event.created_at,
                published_at=event.published_at,
                next_retry_at=event.next_retry_at,
                last_error=event.last_error,
                last_error_at=event.last_error_at,
            )
        )

    async def get_waiting(self, limit: int = 100) -> list[OutboxEvent]:
        now = datetime.now(UTC)
        waiting_statuses = (OutboxStatus.PENDING, OutboxStatus.FAILED)
        result = await self._session.scalars(
            select(OutboxEventModel)
            .where(OutboxEventModel.published_at.is_(None))
            .where(OutboxEventModel.status.in_(waiting_statuses))
            .where(OutboxEventModel.retry_count <= OutboxEventModel.max_retries)
            .where(
                or_(
                    OutboxEventModel.next_retry_at.is_(None),
                    OutboxEventModel.next_retry_at <= now,
                )
            )
            .order_by(OutboxEventModel.created_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return [map_outbox_event_model(model) for model in result.all()]

    async def update(self, event: OutboxEvent) -> None:
        model = cast(
            OutboxEventModel | None,
            await self._session.get(OutboxEventModel, event.id, with_for_update=True),
        )
        if model is None:
            raise ValueError

        model.status = event.status
        model.retry_count = event.retry_count
        model.max_retries = event.max_retries
        model.published_at = event.published_at
        model.next_retry_at = event.next_retry_at
        model.last_error = event.last_error
        model.last_error_at = event.last_error_at
