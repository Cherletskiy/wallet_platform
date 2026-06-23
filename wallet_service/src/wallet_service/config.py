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
    outbox_scheduler_enabled: bool
    outbox_scheduler_interval_seconds: float
    outbox_scheduler_batch_size: int

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
            kafka_bootstrap_servers=os.getenv(
                "KAFKA_BOOTSTRAP_SERVERS",
                "localhost:19092",
            ),
            outbox_scheduler_enabled=os.getenv(
                "OUTBOX_SCHEDULER_ENABLED",
                "true",
            ).lower()
            == "true",
            outbox_scheduler_interval_seconds=float(
                os.getenv("OUTBOX_SCHEDULER_INTERVAL_SECONDS", "5")
            ),
            outbox_scheduler_batch_size=int(
                os.getenv("OUTBOX_SCHEDULER_BATCH_SIZE", "100")
            ),
        )


config = Config.from_env()
