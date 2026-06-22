import uuid

from wallet_service.application.queries.get_wallet_balance.gateway import (
    WalletBalanceGateway,
)
from wallet_service.domain.exceptions import WalletBalanceError, WalletNotFoundError


class GetWalletBalanceInteractor:
    def __init__(self, gw: WalletBalanceGateway) -> None:
        self._gw = gw

    async def execute(self, wallet_id: uuid.UUID) -> float:
        try:
            balance_cent = await self._gw.get_wallet_balance_cent(wallet_id)
            if balance_cent is None:
                raise WalletNotFoundError
        except WalletNotFoundError:
            raise
        except Exception as exc:
            raise WalletBalanceError from exc

        return round(balance_cent / 100, 2)
