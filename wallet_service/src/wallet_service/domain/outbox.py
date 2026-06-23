import enum
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

OUTBOX_BACKOFF_MAX_MINUTES = 30


class OutboxStatus(enum.StrEnum):
    PENDING = "PENDING"
    FAILED = "FAILED"
    PUBLISHED = "PUBLISHED"
    DEAD_LETTER = "DEAD_LETTER"


@dataclass
class OutboxEvent:
    aggregate_type: str
    aggregate_id: uuid.UUID
    event_type: str
    payload: dict[str, Any]
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: OutboxStatus = OutboxStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime | None = None
    published_at: datetime | None = None
    next_retry_at: datetime | None = None
    last_error: str | None = None
    last_error_at: datetime | None = None

    def mark_published(self, *, now: datetime | None = None) -> None:
        published_at = now or datetime.now(UTC)
        self.status = OutboxStatus.PUBLISHED
        self.published_at = published_at
        self.next_retry_at = None
        self.last_error = None
        self.last_error_at = None

    def mark_failed(self, reason: str, *, now: datetime | None = None) -> None:
        failed_at = now or datetime.now(UTC)
        self.retry_count += 1
        self.last_error = reason
        self.last_error_at = failed_at

        if self.retry_count > self.max_retries:
            self.status = OutboxStatus.DEAD_LETTER
            self.next_retry_at = None
            return

        self.status = OutboxStatus.FAILED
        self.next_retry_at = failed_at + self.next_retry_delay()

    @staticmethod
    def _backoff_delay(retry_count: int) -> timedelta:
        minutes = min(
            OUTBOX_BACKOFF_MAX_MINUTES,
            2 ** max(retry_count - 1, 0),
        )
        return timedelta(minutes=minutes)

    def next_retry_delay(self) -> timedelta:
        return self._backoff_delay(self.retry_count)
