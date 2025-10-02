from fastapi import FastAPI, Request, Depends
from contextlib import asynccontextmanager

from app.core.database import init_db, close_db
from app.api.v1.routes import router
from app.core.logging_config import setup_logger


logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("Starting app")
    try:
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
    lifespan=lifespan
)

app.include_router(router)
