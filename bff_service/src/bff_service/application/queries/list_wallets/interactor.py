from bff_service.domain.identity import UserContext
from bff_service.infrastructure.http.gateway import DownstreamGateway, ProxyResponse


class ListWalletsInteractor:
    def __init__(self, gateway: DownstreamGateway) -> None:
        self._gateway = gateway

    async def execute(
        self,
        *,
        identity_headers: dict[str, str],
        current_user: UserContext,
    ) -> ProxyResponse:
        del current_user
        return await self._gateway.list_wallets(headers=identity_headers)
