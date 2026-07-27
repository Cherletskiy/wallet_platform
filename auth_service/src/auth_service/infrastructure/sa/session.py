from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from auth_service.config import config
from auth_service.infrastructure.logging import setup_logger

logger = setup_logger(__name__)

engine = create_async_engine(url=config.dsn, echo=False, pool_size=5, max_overflow=10)
async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)


async def init_db() -> None:
    logger.info("Initializing database")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda conn: conn.execute(text("SELECT 1")))
            logger.info("Database connection OK")
    except Exception as exc:
        logger.error(f"Error initializing database: {exc}")


async def close_db() -> None:
    await engine.dispose()
    logger.info("Database closed")
