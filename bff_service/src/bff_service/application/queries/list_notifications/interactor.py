from bff_service.domain.identity import UserContext
from bff_service.infrastructure.http.gateway import DownstreamGateway, ProxyResponse


class ListNotificationsInteractor:
    def __init__(self, gateway: DownstreamGateway) -> None:
        self._gateway = gateway

    async def execute(
        self,
        *,
        identity_headers: dict[str, str],
        current_user: UserContext,
        limit: int,
    ) -> ProxyResponse:
        del current_user
        return await self._gateway.get_notifications(
            headers=identity_headers,
            limit=limit,
        )
