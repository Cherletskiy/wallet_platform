import uuid

import jwt
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth_service.application.commands.login.dto import LoginInput
from auth_service.application.commands.login.interactor import LoginInteractor
from auth_service.application.commands.logout.dto import LogoutInput
from auth_service.application.commands.logout.interactor import LogoutInteractor
from auth_service.application.commands.refresh.dto import RefreshInput
from auth_service.application.commands.refresh.interactor import RefreshInteractor
from auth_service.application.commands.register.dto import (
    RegisterInput,
)
from auth_service.application.commands.register.interactor import RegisterInteractor
from auth_service.application.common.security import JWTService
from auth_service.application.queries.me.interactor import MeInteractor
from auth_service.domain.exceptions import InvalidCredentialsError
from auth_service.presentation.api.schemas import (
    HealthResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPairResponse,
    UserResponse,
)

router = APIRouter(prefix="/api/v1", tags=["Auth"], route_class=DishkaRoute)
http_bearer = HTTPBearer()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/auth/register", response_model=UserResponse, status_code=201)
async def register(
    request: RegisterRequest,
    interactor: FromDishka[RegisterInteractor],
) -> UserResponse:
    user = await interactor.execute(
        RegisterInput(email=request.email, password=request.password)
    )
    return UserResponse.model_validate(user, from_attributes=True)


@router.post("/auth/login", response_model=TokenPairResponse)
async def login(
    request: LoginRequest,
    interactor: FromDishka[LoginInteractor],
) -> TokenPairResponse:
    token_pair = await interactor.execute(
        LoginInput(email=request.email, password=request.password)
    )
    return TokenPairResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
    )


@router.post("/auth/refresh", response_model=TokenPairResponse)
async def refresh(
    request: RefreshRequest,
    interactor: FromDishka[RefreshInteractor],
) -> TokenPairResponse:
    token_pair = await interactor.execute(
        RefreshInput(refresh_token=request.refresh_token)
    )
    return TokenPairResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
    )


@router.post("/auth/logout", status_code=204)
async def logout(
    request: LogoutRequest,
    interactor: FromDishka[LogoutInteractor],
) -> None:
    await interactor.execute(LogoutInput(refresh_token=request.refresh_token))


@router.get("/auth/me", response_model=UserResponse)
async def me(
    jwt_service: FromDishka[JWTService],
    interactor: FromDishka[MeInteractor],
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> UserResponse:
    try:
        payload = jwt_service.decode_token(
            credentials.credentials,
            expected_type="access",
        )
    except jwt.PyJWTError as exc:
        raise InvalidCredentialsError from exc

    user = await interactor.execute(uuid.UUID(payload["sub"]))
    return UserResponse.model_validate(user, from_attributes=True)
