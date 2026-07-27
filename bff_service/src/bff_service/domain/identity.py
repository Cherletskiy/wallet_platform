import uuid
from dataclasses import dataclass


@dataclass(slots=True)
class UserContext:
    user_id: uuid.UUID
    email: str
    roles: list[str]
    email_verified: bool
