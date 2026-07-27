from wallet_service.application.commands.create_wallet.dto import CreateWalletInput
from wallet_service.application.unit_of_work import WalletUnitOfWork
from wallet_service.domain.wallet import Wallet


class CreateWalletInteractor:
    def __init__(self, uow: WalletUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, data: CreateWalletInput) -> Wallet:
        wallet = await self._uow.wallets.create_wallet(data.owner_user_id)
        await self._uow.commit()
        return wallet
