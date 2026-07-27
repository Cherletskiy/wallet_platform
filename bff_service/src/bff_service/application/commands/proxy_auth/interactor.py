from bff_service.infrastructure.http.gateway import DownstreamGateway, ProxyResponse


class ProxyAuthInteractor:
    def __init__(self, gateway: DownstreamGateway) -> None:
        self._gateway = gateway

    async def execute(
        self,
        *,
        method: str,
        path: str,
        body: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
    ) -> ProxyResponse:
        return await self._gateway.proxy_auth(
            method=method,
            path=path,
            body=body,
            headers=headers,
        )
