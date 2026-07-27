import uuid
from dataclasses import dataclass
from typing import Any

import httpx

from bff_service.config import Config


@dataclass(slots=True)
class ProxyResponse:
    status_code: int
    body: Any
    headers: dict[str, str]


class DownstreamGateway:
    def __init__(self, cfg: Config) -> None:
        self._cfg = cfg

    async def proxy_auth(
        self,
        *,
        method: str,
        path: str,
        body: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
    ) -> ProxyResponse:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method=method,
                url=f"{self._cfg.auth_service_url}{path}",
                json=body,
                headers=headers,
            )
        return self._build_proxy_response(response)

    async def get_wallet_balance(
        self,
        *,
        wallet_id: uuid.UUID,
        headers: dict[str, str],
    ) -> ProxyResponse:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self._cfg.wallet_service_url}/api/v1/wallets/{wallet_id}",
                headers=headers,
            )
        return self._build_proxy_response(response)

    async def apply_wallet_operation(
        self,
        *,
        wallet_id: uuid.UUID,
        body: dict[str, object],
        headers: dict[str, str],
    ) -> ProxyResponse:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{self._cfg.wallet_service_url}/api/v1/wallets/{wallet_id}/operation",
                json=body,
                headers=headers,
            )
        return self._build_proxy_response(response)

    @staticmethod
    def _build_proxy_response(response: httpx.Response) -> ProxyResponse:
        try:
            body: Any = response.json()
        except ValueError:
            body = response.text

        forwarded_headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() in {"content-type"}
        }
        return ProxyResponse(
            status_code=response.status_code,
            body=body,
            headers=forwarded_headers,
        )
