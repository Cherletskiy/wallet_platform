from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import AsyncContainer, Scope, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.v1.routes import router
from app.core.database import close_db, init_db
from app.core.logging_config import setup_logger
from app.core.migrations import run_migrations
from app.ioc import MainProvider

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting app")
    try:
        await run_migrations()
        await init_db()
        yield
    except Exception as e:
        logger.error(f"Error in lifespan: {e}")
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
    app.include_router(router)
    setup_dishka(container=container, app=app)
    return app


app = create_app()
