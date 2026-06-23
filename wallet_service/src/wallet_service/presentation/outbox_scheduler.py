import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import Any

from dishka import AsyncContainer, Scope

from wallet_service.application.commands.outbox_processor import (
    OutboxProcessorInteractor,
)
from wallet_service.config import Config
from wallet_service.infrastructure.logging import setup_logger

logger = setup_logger(__name__)


def create_outbox_scheduler_lifespan(
    container: AsyncContainer,
    config: Config,
) -> Any:
    @asynccontextmanager
    async def lifespan() -> AsyncIterator[None]:
        scheduler_task: asyncio.Task[None] | None = None
        if config.outbox_scheduler_enabled:
            scheduler_task = asyncio.create_task(
                run_scheduler_loop(container, config),
                name="wallet-outbox-scheduler",
            )

        try:
            yield
        finally:
            if scheduler_task is not None:
                scheduler_task.cancel()
                with suppress(asyncio.CancelledError):
                    await scheduler_task

    return lifespan


async def run_scheduler_loop(
    container: AsyncContainer,
    config: Config,
) -> None:
    logger.info("Outbox scheduler started")
    while True:
        await asyncio.sleep(config.outbox_scheduler_interval_seconds)
        try:
            async with container(scope=Scope.REQUEST) as request_container:
                interactor = await request_container.get(OutboxProcessorInteractor)
                await interactor.execute(config.outbox_scheduler_batch_size)
        except Exception:
            logger.exception("Outbox scheduler iteration failed")
