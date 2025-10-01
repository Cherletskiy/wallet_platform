from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.core.logging_config import setup_logger


logger = setup_logger(__name__)


async def get_async_session() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in async session: {e}")
            raise
        finally:
            await session.close()