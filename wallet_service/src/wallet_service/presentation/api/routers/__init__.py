from wallet_service.presentation.api.routers.wallets import router as wallets_router

routers = [wallets_router]

__all__ = ["routers", "wallets_router"]
