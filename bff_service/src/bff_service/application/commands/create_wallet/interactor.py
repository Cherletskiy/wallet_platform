from bff_service.domain.identity import UserContext
from bff_service.infrastructure.http.gateway import DownstreamGateway, ProxyResponse


class CreateWalletInteractor:
    def __init__(self, gateway: DownstreamGateway) -> None:
        self._gateway = gateway

    async def execute(
        self,
        *,
        identity_headers: dict[str, str],
        current_user: UserContext,
    ) -> ProxyResponse:
        return await self._gateway.create_wallet(headers=identity_headers)
