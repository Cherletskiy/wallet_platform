import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Config:
    db_host: str
    db_port: str
    db_name: str
    db_user: str
    db_password: str

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
            db_host=os.getenv("DB_HOST", "db"),
            db_port=os.getenv("DB_PORT", "5432"),
            db_name=os.getenv("DB_NAME", "wallet_db"),
            db_user=os.getenv("DB_USER", "postgres"),
            db_password=os.getenv("DB_PASSWORD", os.getenv("DB_PWD", "postgres")),
        )


config = Config.from_env()
