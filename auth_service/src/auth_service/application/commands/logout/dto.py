from dataclasses import dataclass


@dataclass(slots=True)
class LogoutInput:
    refresh_token: str
