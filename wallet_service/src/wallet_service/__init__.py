import argparse
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from dishka import AsyncContainer, Scope, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from wallet_service.infrastructure.logging import setup_logger
from wallet_service.infrastructure.sa.migrations import run_migrations
from wallet_service.infrastructure.sa.session import close_db, init_db
from wallet_service.ioc import MainProvider
from wallet_service.presentation.api import register_exception_handlers, routers

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


def create_app(container: AsyncContainer | None = None) -> FastAPI:
    container = container or make_async_container(
        MainProvider(),
        start_scope=Scope.APP,
    )
    app = FastAPI(
        title="Wallet Service API",
        description="API for wallet operations",
        version="1.0.0",
        lifespan=lifespan,
    )

    register_exception_handlers(app)
    for router in routers:
        app.include_router(router)
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


app = create_app()
