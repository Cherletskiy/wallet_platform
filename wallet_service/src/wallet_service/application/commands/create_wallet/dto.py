import uuid
from dataclasses import dataclass


@dataclass(slots=True)
class CreateWalletInput:
    owner_user_id: uuid.UUID
