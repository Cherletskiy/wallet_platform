from pathlib import Path

import anyio
from alembic import command
from alembic.config import Config as AlembicConfig

from auth_service.config import config


async def run_migrations() -> None:
    project_root = Path(__file__).resolve().parents[4]
    alembic_ini = project_root / "alembic.ini"
    alembic_dir = (
        project_root / "src" / "auth_service" / "infrastructure" / "sa" / "alembic"
    )

    def _run() -> None:
        alembic_cfg = AlembicConfig(str(alembic_ini))
        alembic_cfg.set_main_option(
            "sqlalchemy.url", config.dsn.replace("+asyncpg", "")
        )
        alembic_cfg.set_main_option("script_location", str(alembic_dir))
        command.upgrade(alembic_cfg, "head")

    await anyio.to_thread.run_sync(_run)
