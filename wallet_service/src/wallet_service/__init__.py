import argparse
import os
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any

import uvicorn
from dishka import AsyncContainer, Scope, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from wallet_service.config import config
from wallet_service.infrastructure.logging import setup_logger
from wallet_service.infrastructure.sa.migrations import run_migrations
from wallet_service.infrastructure.sa.session import close_db, init_db
from wallet_service.ioc import MainProvider
from wallet_service.presentation.api import register_exception_handlers, routers
from wallet_service.presentation.outbox_scheduler import (
    create_outbox_scheduler_lifespan,
)

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting app")
    try:
        await run_migrations()
        await init_db()
        yield
    except Exception as exc:
        logger.error(f"Error in lifespan: {exc}")
        raise
    finally:
        logger.info("Stopping app")
        await close_db()


def create_app(
    container: AsyncContainer | None = None,
    *,
    setup_di: bool = True,
    lifespan_context: Any = lifespan,
) -> FastAPI:
    if container is None and setup_di:
        container = make_async_container(
            MainProvider(),
            start_scope=Scope.RUNTIME,
        )
    if container is not None and setup_di and lifespan_context is lifespan:
        outbox_scheduler_lifespan = create_outbox_scheduler_lifespan(container, config)

        @asynccontextmanager
        async def combined_lifespan(app: FastAPI) -> AsyncIterator[None]:
            async with AsyncExitStack() as stack:
                await stack.enter_async_context(lifespan(app))
                await stack.enter_async_context(outbox_scheduler_lifespan())
                yield

        lifespan_context = combined_lifespan
    app = FastAPI(
        title="Wallet Service API",
        description="API for wallet operations",
        version="1.0.0",
        lifespan=lifespan_context,
    )

    register_exception_handlers(app)
    for router in routers:
        app.include_router(router)
    if container is not None and setup_di:
        setup_dishka(container=container, app=app)
    return app


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="wallet-service",
        description="Run the wallet service application.",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("APP_HOST", "0.0.0.0"),
        help="HTTP host to bind.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("APP_PORT", "8000")),
        help="HTTP port to bind.",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=os.getenv("APP_RELOAD", "").lower() == "true",
        help="Enable auto-reload for local development.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    uvicorn.run(
        "wallet_service:create_app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        use_colors=True,
        factory=True,
    )
