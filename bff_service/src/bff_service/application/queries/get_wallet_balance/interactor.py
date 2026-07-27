import uuid

from bff_service.domain.identity import UserContext
from bff_service.infrastructure.http.gateway import DownstreamGateway, ProxyResponse


class GetWalletBalanceInteractor:
    def __init__(self, gateway: DownstreamGateway) -> None:
        self._gateway = gateway

    async def execute(
        self,
        *,
        wallet_id: uuid.UUID,
        identity_headers: dict[str, str],
        current_user: UserContext,
    ) -> ProxyResponse:
        return await self._gateway.get_wallet_balance(
            wallet_id=wallet_id,
            headers=identity_headers,
        )
