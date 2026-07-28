import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

DEFAULT_JWT_SECRET_KEY = "super-secret-key-change-me-32-bytes"


@dataclass(slots=True)
class Config:
    db_host: str
    db_port: str
    db_name: str
    db_user: str
    db_password: str
    jwt_secret_key: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    @property
    def dsn(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            db_host=os.getenv("POSTGRES_HOST", "db"),
            db_port=os.getenv("POSTGRES_PORT", "5432"),
            db_name=os.getenv("POSTGRES_DB", "auth_db"),
            db_user=os.getenv("POSTGRES_USER", "postgres"),
            db_password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            jwt_secret_key=os.getenv("JWT_SECRET_KEY", DEFAULT_JWT_SECRET_KEY),
            access_token_expire_minutes=int(
                os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
            ),
            refresh_token_expire_days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
        )


config = Config.from_env()
