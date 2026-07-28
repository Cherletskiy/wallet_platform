from fastapi import FastAPI
from fastapi.responses import JSONResponse

from notification_service.domain.exceptions import AuthorizationError


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AuthorizationError)
    async def handle_authorization_error(
        _request: object,
        exc: AuthorizationError,
    ) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": str(exc)})
