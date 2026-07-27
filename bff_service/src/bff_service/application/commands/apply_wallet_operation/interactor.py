import uuid

from bff_service.domain.identity import UserContext
from bff_service.infrastructure.http.gateway import DownstreamGateway, ProxyResponse


class ApplyWalletOperationInteractor:
    def __init__(self, gateway: DownstreamGateway) -> None:
        self._gateway = gateway

    async def execute(
        self,
        *,
        wallet_id: uuid.UUID,
        body: dict[str, object],
        identity_headers: dict[str, str],
        current_user: UserContext,
    ) -> ProxyResponse:
        return await self._gateway.apply_wallet_operation(
            wallet_id=wallet_id,
            body=body,
            headers=identity_headers,
        )
