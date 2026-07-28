import uuid
from dataclasses import dataclass


@dataclass(slots=True)
class UserContext:
    user_id: uuid.UUID
    roles: set[str]
    email_verified: bool
