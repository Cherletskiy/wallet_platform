from dataclasses import dataclass


@dataclass(slots=True)
class RegisterInput:
    email: str
    password: str
