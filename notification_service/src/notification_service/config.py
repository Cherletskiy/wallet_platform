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
    kafka_bootstrap_servers: str

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
            db_name=os.getenv("POSTGRES_DB", "notification_db"),
            db_user=os.getenv("POSTGRES_USER", "postgres"),
            db_password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            kafka_bootstrap_servers=os.getenv(
                "KAFKA_BOOTSTRAP_SERVERS",
                "localhost:29092",
            ),
        )


config = Config.from_env()
