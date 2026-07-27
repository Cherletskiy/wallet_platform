import argparse
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from dishka import AsyncContainer, Scope, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from bff_service.infrastructure.logging import setup_logger
from bff_service.ioc import MainProvider
from bff_service.presentation.api import routers

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting app")
    try:
        yield
    finally:
        logger.info("Stopping app")


def create_app(
    container: AsyncContainer | None = None,
    *,
    setup_di: bool = True,
    lifespan_context: Any = lifespan,
) -> FastAPI:
    app = FastAPI(
        title="BFF Service API",
        description="Client-facing gateway for auth and wallet flows",
        version="1.0.0",
        lifespan=lifespan_context,
    )

    if container is None and setup_di:
        container = make_async_container(MainProvider(), start_scope=Scope.RUNTIME)

    for router in routers:
        app.include_router(router)

    if container is not None and setup_di:
        setup_dishka(container=container, app=app)
    return app


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="bff-service",
        description="Run the BFF service application.",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("APP_HOST", "0.0.0.0"),
        help="HTTP host to bind.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("APP_PORT", "8003")),
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
        "bff_service:create_app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        use_colors=True,
        factory=True,
    )
