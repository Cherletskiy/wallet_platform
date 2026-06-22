import uuid

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from wallet_service.application.commands.apply_wallet_operation import (
    ApplyWalletOperationInput,
    ApplyWalletOperationInteractor,
)
from wallet_service.application.queries.get_wallet_balance import (
    GetWalletBalanceInteractor,
)
from wallet_service.presentation.api.schemas import (
    WalletBalanceResponse,
    WalletOperationRequest,
)

router = APIRouter(prefix="/api/v1", tags=["Wallet"], route_class=DishkaRoute)


@router.get(
    "/wallets/{wallet_id}",
    response_model=WalletBalanceResponse,
    summary="Получение баланса в рублях по UUID",
)
async def get_wallet(
    wallet_id: uuid.UUID,
    interactor: FromDishka[GetWalletBalanceInteractor],
) -> WalletBalanceResponse:
    balance_rub = await interactor.execute(wallet_id)
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
    interactor: FromDishka[ApplyWalletOperationInteractor],
) -> WalletBalanceResponse:
    balance_rub = await interactor.execute(
        ApplyWalletOperationInput(
            wallet_id=wallet_id,
            amount_cent=int((request.amount * 100).to_integral_value()),
            operation_type=request.operation_type,
        )
    )
    return WalletBalanceResponse(balance_rub=balance_rub)
