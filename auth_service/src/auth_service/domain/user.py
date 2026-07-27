import enum
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


class Role(enum.StrEnum):
    USER = "user"
    ADMIN = "admin"


@dataclass
class User:
    email: str
    password_hash: str
    role: Role = Role.USER
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    is_active: bool = True
    is_email_verified: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
