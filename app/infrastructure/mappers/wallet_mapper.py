from app.domain.wallet import Operation, Wallet
from app.infrastructure.db.models import OperationModel, WalletModel


def map_operation_model(model: OperationModel) -> Operation:
    return Operation(
        id=model.id,
        wallet_id=model.wallet_id,
        operation_type=model.operation_type,
        amount_cent=model.amount_cent,
        created_at=model.created_at,
    )


def map_wallet_model(model: WalletModel) -> Wallet:
    return Wallet(
        id=model.id,
        balance_cent=model.balance_cent,
        created_at=model.created_at,
        operations=[],
    )
