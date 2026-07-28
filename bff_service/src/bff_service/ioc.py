from dishka import Provider, Scope, provide

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
from bff_service.infrastructure.http.gateway import DownstreamGateway


class MainProvider(Provider):
    @provide(scope=Scope.APP)
    def get_identity_service(self) -> IdentityService:
        return IdentityService(config)

    @provide(scope=Scope.REQUEST)
    def get_downstream_gateway(self) -> DownstreamGateway:
        return DownstreamGateway(config)

    proxy_auth_interactor = provide(ProxyAuthInteractor, scope=Scope.REQUEST)
    get_wallet_balance_interactor = provide(
        GetWalletBalanceInteractor,
        scope=Scope.REQUEST,
    )
    list_wallets_interactor = provide(
        ListWalletsInteractor,
        scope=Scope.REQUEST,
    )
    apply_wallet_operation_interactor = provide(
        ApplyWalletOperationInteractor,
        scope=Scope.REQUEST,
    )
    create_wallet_interactor = provide(
        CreateWalletInteractor,
        scope=Scope.REQUEST,
    )
    list_notifications_interactor = provide(
        ListNotificationsInteractor,
        scope=Scope.REQUEST,
    )
