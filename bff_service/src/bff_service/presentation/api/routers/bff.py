import uuid

import jwt
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from bff_service.application.commands.apply_wallet_operation.interactor import (
    ApplyWalletOperationInteractor,
)
from bff_service.application.commands.create_wallet.interactor import (
    CreateWalletInteractor,
)
from bff_service.application.commands.proxy_auth.interactor import ProxyAuthInteractor
from bff_service.application.common.identity import (
    IdentityService,
    build_identity_headers,
)
from bff_service.application.queries.get_wallet_balance.interactor import (
    GetWalletBalanceInteractor,
)
from bff_service.presentation.api.schemas import (
    HealthResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    WalletOperationRequest,
)

router = APIRouter(prefix="/api/v1", tags=["BFF"], route_class=DishkaRoute)
http_bearer = HTTPBearer()


def to_response(status_code: int, body: object, headers: dict[str, str]) -> Response:
    return JSONResponse(status_code=status_code, content=body, headers=headers)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/auth/register")
async def register(
    request: RegisterRequest,
    interactor: FromDishka[ProxyAuthInteractor],
) -> Response:
    result = await interactor.execute(
        method="POST",
        path="/api/v1/auth/register",
        body=request.model_dump(),
    )
    return to_response(result.status_code, result.body, result.headers)


@router.post("/auth/login")
async def login(
    request: LoginRequest,
    interactor: FromDishka[ProxyAuthInteractor],
) -> Response:
    result = await interactor.execute(
        method="POST",
        path="/api/v1/auth/login",
        body=request.model_dump(),
    )
    return to_response(result.status_code, result.body, result.headers)


@router.post("/auth/refresh")
async def refresh(
    request: RefreshRequest,
    interactor: FromDishka[ProxyAuthInteractor],
) -> Response:
    result = await interactor.execute(
        method="POST",
        path="/api/v1/auth/refresh",
        body=request.model_dump(),
    )
    return to_response(result.status_code, result.body, result.headers)


@router.post("/auth/logout", status_code=204)
async def logout(
    request: LogoutRequest,
    interactor: FromDishka[ProxyAuthInteractor],
) -> Response:
    result = await interactor.execute(
        method="POST",
        path="/api/v1/auth/logout",
        body=request.model_dump(),
    )
    return Response(status_code=result.status_code, headers=result.headers)


@router.get("/auth/me")
async def me(
    interactor: FromDishka[ProxyAuthInteractor],
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> Response:
    result = await interactor.execute(
        method="GET",
        path="/api/v1/auth/me",
        headers={"Authorization": f"Bearer {credentials.credentials}"},
    )
    return to_response(result.status_code, result.body, result.headers)


@router.get("/wallets/{wallet_id}")
async def get_wallet(
    wallet_id: uuid.UUID,
    identity_service: FromDishka[IdentityService],
    interactor: FromDishka[GetWalletBalanceInteractor],
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> Response:
    try:
        current_user = identity_service.get_current_user(credentials.credentials)
    except jwt.PyJWTError:
        return JSONResponse(status_code=401, content={"detail": "Invalid access token"})

    result = await interactor.execute(
        wallet_id=wallet_id,
        identity_headers=build_identity_headers(current_user),
        current_user=current_user,
    )
    return to_response(result.status_code, result.body, result.headers)


@router.post("/wallets")
async def create_wallet(
    identity_service: FromDishka[IdentityService],
    interactor: FromDishka[CreateWalletInteractor],
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> Response:
    try:
        current_user = identity_service.get_current_user(credentials.credentials)
    except jwt.PyJWTError:
        return JSONResponse(status_code=401, content={"detail": "Invalid access token"})

    result = await interactor.execute(
        identity_headers=build_identity_headers(current_user),
        current_user=current_user,
    )
    return to_response(result.status_code, result.body, result.headers)


@router.post("/wallets/{wallet_id}/operation")
async def wallet_operation(
    wallet_id: uuid.UUID,
    request: WalletOperationRequest,
    identity_service: FromDishka[IdentityService],
    interactor: FromDishka[ApplyWalletOperationInteractor],
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> Response:
    try:
        current_user = identity_service.get_current_user(credentials.credentials)
    except jwt.PyJWTError:
        return JSONResponse(status_code=401, content={"detail": "Invalid access token"})

    result = await interactor.execute(
        wallet_id=wallet_id,
        body=request.model_dump(mode="json"),
        identity_headers=build_identity_headers(current_user),
        current_user=current_user,
    )
    return to_response(result.status_code, result.body, result.headers)
