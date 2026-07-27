import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class RefreshSession:
    user_id: uuid.UUID
    family_id: uuid.UUID
    expires_at: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    revoked_at: datetime | None = None
    replaced_by_session_id: uuid.UUID | None = None

    def revoke(
        self,
        *,
        replaced_by_session_id: uuid.UUID | None = None,
        now: datetime | None = None,
    ) -> None:
        self.revoked_at = now or datetime.now(UTC)
        self.replaced_by_session_id = replaced_by_session_id

    def is_active(self, *, now: datetime | None = None) -> bool:
        current = now or datetime.now(UTC)
        return self.revoked_at is None and self.expires_at > current
