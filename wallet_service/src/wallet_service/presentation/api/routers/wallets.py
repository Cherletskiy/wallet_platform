import uuid

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request

from wallet_service.application.commands.apply_wallet_operation import (
    ApplyWalletOperationInput,
    ApplyWalletOperationInteractor,
)
from wallet_service.application.commands.create_wallet import (
    CreateWalletInput,
    CreateWalletInteractor,
)
from wallet_service.application.queries.get_wallet_balance import (
    GetWalletBalanceInteractor,
)
from wallet_service.application.queries.list_wallets import ListWalletsInteractor
from wallet_service.presentation.api.identity import HTTPIdentityProvider
from wallet_service.presentation.api.schemas import (
    WalletBalanceResponse,
    WalletListItemResponse,
    WalletOperationRequest,
    WalletResponse,
)

router = APIRouter(prefix="/api/v1", tags=["Wallet"], route_class=DishkaRoute)


@router.get(
    "/wallets",
    response_model=list[WalletListItemResponse],
    summary="Получение всех кошельков текущего пользователя",
)
async def list_wallets(
    request: Request,
    interactor: FromDishka[ListWalletsInteractor],
) -> list[WalletListItemResponse]:
    current_user = await HTTPIdentityProvider(request).get_current_user()
    wallets = await interactor.execute(current_user.user_id)
    return [
        WalletListItemResponse(
            wallet_id=str(wallet.id),
            balance_rub=round(wallet.balance_cent / 100, 2),
        )
        for wallet in wallets
    ]


@router.post(
    "/wallets",
    response_model=WalletResponse,
    status_code=201,
    summary="Создание нового кошелька для текущего пользователя",
)
async def create_wallet(
    request: Request,
    interactor: FromDishka[CreateWalletInteractor],
) -> WalletResponse:
    current_user = await HTTPIdentityProvider(request).get_current_user()
    wallet = await interactor.execute(CreateWalletInput(current_user.user_id))
    return WalletResponse(wallet_id=str(wallet.id), balance_rub=0.0)


@router.get(
    "/wallets/{wallet_id}",
    response_model=WalletBalanceResponse,
    summary="Получение баланса в рублях по UUID",
)
async def get_wallet(
    wallet_id: uuid.UUID,
    request: Request,
    interactor: FromDishka[GetWalletBalanceInteractor],
) -> WalletBalanceResponse:
    current_user = await HTTPIdentityProvider(request).get_current_user()
    balance_rub = await interactor.execute(wallet_id, current_user.user_id)
    return WalletBalanceResponse(balance_rub=balance_rub)


@router.post(
    "/wallets/{wallet_id}/operation",
    response_model=WalletBalanceResponse,
    summary="Операция DEPOSIT/WITHDRAWAL с балансом. "
    "Возврат баланса в рублях в случае успеха",
)
async def wallet_operation(
    wallet_id: uuid.UUID,
    http_request: Request,
    request: WalletOperationRequest,
    interactor: FromDishka[ApplyWalletOperationInteractor],
) -> WalletBalanceResponse:
    current_user = await HTTPIdentityProvider(http_request).get_current_user()
    balance_rub = await interactor.execute(
        ApplyWalletOperationInput(
            wallet_id=wallet_id,
            amount_cent=int((request.amount * 100).to_integral_value()),
            operation_type=request.operation_type,
        ),
        current_user.user_id,
    )
    return WalletBalanceResponse(balance_rub=balance_rub)
