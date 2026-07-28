import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
import pytest
import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from bff_service import create_app
from bff_service.application.commands.apply_wallet_operation.interactor import (
    ApplyWalletOperationInteractor,
)
from bff_service.application.commands.create_wallet.interactor import (
    CreateWalletInteractor,
)
from bff_service.application.commands.proxy_auth.interactor import ProxyAuthInteractor
from bff_service.application.common.identity import IdentityService
from bff_service.application.queries.get_wallet_balance.interactor import (
    GetWalletBalanceInteractor,
)
from bff_service.application.queries.list_notifications.interactor import (
    ListNotificationsInteractor,
)
from bff_service.application.queries.list_wallets.interactor import (
    ListWalletsInteractor,
)
from bff_service.config import config
from bff_service.infrastructure.http.gateway import DownstreamGateway, ProxyResponse


class StubGateway(DownstreamGateway):
    def __init__(self) -> None:
        self.last_call: dict[str, object] | None = None

    async def proxy_auth(
        self,
        *,
        method: str,
        path: str,
        body: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
    ) -> ProxyResponse:
        self.last_call = {
            "method": method,
            "path": path,
            "body": body,
            "headers": headers,
        }
        return ProxyResponse(status_code=200, body={"ok": True}, headers={})

    async def get_wallet_balance(
        self,
        *,
        wallet_id: uuid.UUID,
        headers: dict[str, str],
    ) -> ProxyResponse:
        self.last_call = {
            "wallet_id": wallet_id,
            "headers": headers,
        }
        return ProxyResponse(status_code=200, body={"balance_rub": 100.0}, headers={})

    async def list_wallets(
        self,
        *,
        headers: dict[str, str],
    ) -> ProxyResponse:
        self.last_call = {
            "headers": headers,
        }
        return ProxyResponse(
            status_code=200,
            body=[
                {
                    "wallet_id": "11111111-1111-1111-1111-111111111111",
                    "balance_rub": 100.0,
                },
                {
                    "wallet_id": "22222222-2222-2222-2222-222222222222",
                    "balance_rub": 25.0,
                },
            ],
            headers={},
        )

    async def create_wallet(
        self,
        *,
        headers: dict[str, str],
    ) -> ProxyResponse:
        self.last_call = {
            "headers": headers,
        }
        return ProxyResponse(
            status_code=201,
            body={
                "wallet_id": "11111111-1111-1111-1111-111111111111",
                "balance_rub": 0.0,
            },
            headers={},
        )

    async def get_notifications(
        self,
        *,
        headers: dict[str, str],
        limit: int,
    ) -> ProxyResponse:
        self.last_call = {
            "headers": headers,
            "limit": limit,
        }
        return ProxyResponse(
            status_code=200,
            body=[
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "source_event_id": "22222222-2222-2222-2222-222222222222",
                    "user_id": "11111111-1111-1111-1111-111111111111",
                    "wallet_id": "33333333-3333-3333-3333-333333333333",
                    "operation_type": "DEPOSIT",
                    "amount_rub": 100.0,
                    "balance_rub": 100.0,
                    "message": (
                        "Deposit received: 100.00 RUB. Current balance: 100.00 RUB."
                    ),
                    "created_at": None,
                }
            ],
            headers={},
        )

    async def apply_wallet_operation(
        self,
        *,
        wallet_id: uuid.UUID,
        body: dict[str, object],
        headers: dict[str, str],
    ) -> ProxyResponse:
        self.last_call = {
            "wallet_id": wallet_id,
            "body": body,
            "headers": headers,
        }
        return ProxyResponse(status_code=200, body={"balance_rub": 200.0}, headers={})


@pytest.fixture
def downstream_gateway() -> StubGateway:
    return StubGateway()


@pytest.fixture
def identity_service() -> IdentityService:
    return IdentityService(config)


@pytest_asyncio.fixture
async def app(
    downstream_gateway: StubGateway,
    identity_service: IdentityService,
) -> AsyncIterator[FastAPI]:
    class ApiTestProvider(Provider):
        @provide(scope=Scope.REQUEST, provides=DownstreamGateway)
        def gateway(self) -> DownstreamGateway:
            return downstream_gateway

        @provide(scope=Scope.APP, provides=IdentityService)
        def identity(self) -> IdentityService:
            return identity_service

        proxy_auth_interactor = provide(ProxyAuthInteractor, scope=Scope.REQUEST)
        create_wallet_interactor = provide(CreateWalletInteractor, scope=Scope.REQUEST)
        get_wallet_balance_interactor = provide(
            GetWalletBalanceInteractor,
            scope=Scope.REQUEST,
        )
        list_wallets_interactor = provide(
            ListWalletsInteractor,
            scope=Scope.REQUEST,
        )
        list_notifications_interactor = provide(
            ListNotificationsInteractor,
            scope=Scope.REQUEST,
        )
        apply_wallet_operation_interactor = provide(
            ApplyWalletOperationInteractor,
            scope=Scope.REQUEST,
        )

    container = make_async_container(ApiTestProvider(), start_scope=Scope.RUNTIME)
    async with container(scope=Scope.APP) as app_container:

        @asynccontextmanager
        async def test_lifespan(_: object) -> AsyncIterator[None]:
            yield

        app = create_app(setup_di=False, lifespan_context=test_lifespan)
        setup_dishka(app_container, app)
        yield app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as test_client:
        yield test_client
