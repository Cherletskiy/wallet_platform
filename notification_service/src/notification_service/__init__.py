import argparse
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from dishka import AsyncContainer, Scope, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from faststream.kafka import KafkaBroker

from notification_service.config import config
from notification_service.infrastructure.logging import setup_logger
from notification_service.infrastructure.sa.migrations import run_migrations
from notification_service.infrastructure.sa.session import (
    async_session_factory,
    close_db,
    init_db,
)
from notification_service.ioc import MainProvider
from notification_service.presentation.api import routers
from notification_service.presentation.faststream.consumer import (
    register_wallet_transaction_consumer,
)

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    broker: KafkaBroker | None = getattr(app.state, "broker", None)
    logger.info("Starting app")
    try:
        await run_migrations()
        await init_db()
        if broker is not None:
            await broker.connect()
            await broker.start()
        yield
    except Exception as exc:
        logger.error(f"Error in lifespan: {exc}")
        raise
    finally:
        if broker is not None:
            await broker.stop()
        logger.info("Stopping app")
        await close_db()


def create_app(
    container: AsyncContainer | None = None,
    *,
    setup_di: bool = True,
    setup_consumer: bool = True,
    lifespan_context: Any = lifespan,
) -> FastAPI:
    if container is None and setup_di:
        container = make_async_container(
            MainProvider(),
            start_scope=Scope.RUNTIME,
        )
    app = FastAPI(
        title="Notification Service API",
        description="API for notification storage and event consumption",
        version="1.0.0",
        lifespan=lifespan_context,
    )

    for router in routers:
        app.include_router(router)

    if container is not None and setup_di:
        setup_dishka(container=container, app=app)

    if setup_consumer:
        broker = KafkaBroker(bootstrap_servers=config.kafka_bootstrap_servers)
        register_wallet_transaction_consumer(broker, async_session_factory)
        app.state.broker = broker

    return app


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="notification-service",
        description="Run the notification service application.",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("APP_HOST", "0.0.0.0"),
        help="HTTP host to bind.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("APP_PORT", "8001")),
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
        "notification_service:create_app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        use_colors=True,
        factory=True,
    )
