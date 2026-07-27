import uuid

from wallet_service.application.queries.get_wallet_balance.gateway import (
    WalletBalanceGateway,
)
from wallet_service.domain.exceptions import (
    WalletAccessDeniedError,
    WalletBalanceError,
    WalletNotFoundError,
)


class GetWalletBalanceInteractor:
    def __init__(self, gw: WalletBalanceGateway) -> None:
        self._gw = gw

    async def execute(self, wallet_id: uuid.UUID, current_user_id: uuid.UUID) -> float:
        try:
            wallet = await self._gw.get_wallet_by_id(wallet_id)
            if wallet is None:
                raise WalletNotFoundError
            if wallet.owner_user_id != current_user_id:
                raise WalletAccessDeniedError
        except (WalletNotFoundError, WalletAccessDeniedError):
            raise
        except Exception as exc:
            raise WalletBalanceError from exc

        return round(wallet.balance_cent / 100, 2)
