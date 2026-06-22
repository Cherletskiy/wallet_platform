from wallet_service.application.commands.apply_wallet_operation.dto import (
    ApplyWalletOperationInput,
)
from wallet_service.application.unit_of_work import WalletUnitOfWork
from wallet_service.domain.exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    WalletNotFoundError,
    WalletOperationError,
)
from wallet_service.domain.wallet import OperationType


class ApplyWalletOperationInteractor:
    def __init__(
        self,
        uow: WalletUnitOfWork,
    ) -> None:
        self._uow = uow

    async def execute(self, data: ApplyWalletOperationInput) -> float:
        if data.amount_cent <= 0:
            raise InvalidAmountError

        wallet = await self._uow.wallets.get_wallet_by_id(data.wallet_id)
        if wallet is None:
            raise WalletNotFoundError

        if (
            data.operation_type == OperationType.WITHDRAWAL
            and wallet.balance_cent < data.amount_cent
        ):
            raise InsufficientFundsError

        new_balance_cent = (
            wallet.balance_cent - data.amount_cent
            if data.operation_type == OperationType.WITHDRAWAL
            else wallet.balance_cent + data.amount_cent
        )

        try:
            await self._uow.wallets.update_wallet_balance_cent(
                data.wallet_id,
                new_balance_cent,
            )
            await self._uow.wallets.add_operation(
                data.wallet_id,
                data.operation_type,
                data.amount_cent,
            )
            await self._uow.commit()
        except ValueError as exc:
            raise WalletNotFoundError from exc
        except Exception as exc:
            raise WalletOperationError from exc

        return round(new_balance_cent / 100, 2)
