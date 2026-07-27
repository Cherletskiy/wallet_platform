from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from auth_service.domain.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UserNotFoundError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EmailAlreadyExistsError)
    async def email_already_exists_handler(
        request: Request,
        exc: EmailAlreadyExistsError,
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": "Email already exists"})

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request,
        exc: InvalidCredentialsError,
    ) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})

    @app.exception_handler(InvalidRefreshTokenError)
    async def invalid_refresh_token_handler(
        request: Request,
        exc: InvalidRefreshTokenError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401, content={"detail": "Invalid refresh token"}
        )

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(
        request: Request,
        exc: UserNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": "User not found"})
