from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from wallet_service.domain.exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    WalletBalanceError,
    WalletNotFoundError,
    WalletOperationError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(WalletNotFoundError)
    async def wallet_not_found_handler(
        request: Request, exc: WalletNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": "Wallet not found"})

    @app.exception_handler(InvalidAmountError)
    async def invalid_amount_handler(
        request: Request, exc: InvalidAmountError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400, content={"detail": "Amount must be greater than 0"}
        )

    @app.exception_handler(InsufficientFundsError)
    async def insufficient_funds_handler(
        request: Request, exc: InsufficientFundsError
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": "Not enough balance"})

    @app.exception_handler(WalletBalanceError)
    async def wallet_balance_error_handler(
        request: Request, exc: WalletBalanceError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400, content={"detail": "Error getting wallet balance"}
        )

    @app.exception_handler(WalletOperationError)
    async def wallet_operation_error_handler(
        request: Request, exc: WalletOperationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400, content={"detail": "Error updating wallet balance"}
        )
