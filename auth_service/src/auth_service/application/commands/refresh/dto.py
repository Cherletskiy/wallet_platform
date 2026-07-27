from dataclasses import dataclass

from auth_service.application.commands.login.dto import TokenPair


@dataclass(slots=True)
class RefreshInput:
    refresh_token: str


__all__ = ["RefreshInput", "TokenPair"]
