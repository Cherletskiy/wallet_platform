from pathlib import Path

import anyio
from alembic import command
from alembic.config import Config


async def run_migrations():
    def _run():
        project_dir = Path(__file__).resolve().parents[4]
        alembic_ini = project_dir / "alembic.ini"
        alembic_folder = (
            project_dir
            / "src"
            / "wallet_service"
            / "infrastructure"
            / "sa"
            / "alembic"
        )

        alembic_cfg = Config(str(alembic_ini))
        alembic_cfg.set_main_option("script_location", str(alembic_folder))

        command.upgrade(alembic_cfg, "head")

    await anyio.to_thread.run_sync(_run)
