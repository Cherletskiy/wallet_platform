from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.core.logging_config import setup_logger
from app.repositories.wallet_repository import WalletRepository
from app.services.wallet_service import WalletService

logger = setup_logger(__name__)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        except HTTPException as e:
            raise e
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in async session: {e}")
            raise
        finally:
            await session.close()


async def get_wallet_repository() -> WalletRepository:
    return WalletRepository()


async def get_wallet_service(
    repository: WalletRepository = Depends(get_wallet_repository),
) -> WalletService:
    return WalletService(wallet_repository=repository)
