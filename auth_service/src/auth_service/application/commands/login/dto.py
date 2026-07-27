from dataclasses import dataclass


@dataclass(slots=True)
class LoginInput:
    email: str
    password: str


@dataclass(slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
