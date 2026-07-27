import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Config:
    auth_service_url: str
    wallet_service_url: str
    jwt_secret_key: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            auth_service_url=os.getenv("AUTH_SERVICE_URL", "http://localhost:8002"),
            wallet_service_url=os.getenv(
                "WALLET_SERVICE_URL",
                "http://localhost:8000",
            ),
            jwt_secret_key=os.getenv("JWT_SECRET_KEY", "super-secret-key-change-me"),
        )


config = Config.from_env()
