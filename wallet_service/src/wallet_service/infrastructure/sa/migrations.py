import os

import anyio
from alembic import command
from alembic.config import Config


async def run_migrations():
    def _run():
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        alembic_ini = os.path.join(base_dir, "alembic.ini")
        alembic_folder = os.path.join(
            base_dir,
            "src",
            "wallet_service",
            "infrastructure",
            "sa",
            "alembic",
        )

        alembic_cfg = Config(alembic_ini)
        alembic_cfg.set_main_option("script_location", alembic_folder)

        command.upgrade(alembic_cfg, "head")

    await anyio.to_thread.run_sync(_run)
