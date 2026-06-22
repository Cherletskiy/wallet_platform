import uuid

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import WalletBalanceResponse, WalletOperationRequest
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/api/v1", tags=["Wallet"], route_class=DishkaRoute)


@router.get(
    "/wallets/{wallet_id}",
    response_model=WalletBalanceResponse,
    summary="Получение баланса в рублях по UUID",
)
async def get_wallet(
    wallet_id: uuid.UUID,
    session: FromDishka[AsyncSession],
    wallet_service: FromDishka[WalletService],
) -> WalletBalanceResponse:
    balance_rub = await wallet_service.get_wallet_balance_rub(session, wallet_id)
    return WalletBalanceResponse(balance_rub=balance_rub)


@router.post(
    "/wallets/{wallet_id}/operation",
    response_model=WalletBalanceResponse,
    summary="Операция DEPOSIT/WITHDRAWAL с балансом. "
    "Возврат баланса в рублях в случае успеха",
)
async def wallet_operation(
    wallet_id: uuid.UUID,
    request: WalletOperationRequest,
    session: FromDishka[AsyncSession],
    wallet_service: FromDishka[WalletService],
) -> WalletBalanceResponse:
    balance_rub = await wallet_service.update_wallet_balance_cent(
        session,
        wallet_id,
        int((request.amount * 100).to_integral_value()),
        request.operation_type,
    )
    return WalletBalanceResponse(balance_rub=balance_rub)
