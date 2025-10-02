import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_async_session, get_wallet_service
from app.services.wallet_service import WalletService
from app.api.v1.schemas import WalletBalanceResponse, WalletOperationRequest


router = APIRouter(prefix="/api/v1", tags=["Wallet"])


@router.get("/wallet/{wallet_id}", response_model=WalletBalanceResponse,
            summary="Получение баланса в рублях по UUID")
async def get_wallet(
        wallet_id: uuid.UUID,
        session: AsyncSession = Depends(get_async_session),
        wallet_service: WalletService = Depends(get_wallet_service)
):
    balance_rub = await wallet_service.get_wallet_balance_rub(session, wallet_id)
    return WalletBalanceResponse(balance_rub=balance_rub)


@router.post("/wallet/{wallet_id}/operation", response_model=WalletBalanceResponse,
             summary="Операция DEPOSIT/WITHDRAWAL с балансом. Возврат баланса в рублях в случае успеха")
async def wallet_operation(
        wallet_id: uuid.UUID,
        request: WalletOperationRequest,
        session: AsyncSession = Depends(get_async_session),
        wallet_service: WalletService = Depends(get_wallet_service)
):
    balance_rub = await wallet_service.update_wallet_balance_cent(session, wallet_id,
                                                                  int(request.amount * 100),
                                                                  request.operation_type)
    return WalletBalanceResponse(balance_rub=balance_rub)