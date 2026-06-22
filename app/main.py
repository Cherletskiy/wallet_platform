from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.v1.routes import router
from app.core.database import close_db, init_db
from app.core.logging_config import setup_logger
from app.core.migrations import run_migrations

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


app = FastAPI(
    title="Wallet Service API",
    description="API для работы с кошельками",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(router)
