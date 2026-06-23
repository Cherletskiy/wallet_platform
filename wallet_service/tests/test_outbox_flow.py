import pytest
from sqlalchemy import select

from wallet_service.application.commands.apply_wallet_operation import (
    ApplyWalletOperationInput,
    ApplyWalletOperationInteractor,
)
from wallet_service.domain.exceptions import WalletOperationError
from wallet_service.domain.wallet import OperationType
from wallet_service.infrastructure.sa.models import OperationModel, OutboxEventModel
from wallet_service.infrastructure.sa.repositories.outbox_repository import (
    SQLAlchemyOutboxRepository,
)
from wallet_service.infrastructure.sa.repositories.wallet_repository import (
    SQLAlchemyWalletRepository,
)
from wallet_service.infrastructure.sa.unit_of_work import (
    SQLAlchemyWalletUnitOfWork,
)

pytestmark = pytest.mark.asyncio


async def test_wallet_operation_creates_outbox_event(test_db, wallet):
    wallet_id = wallet

    async with test_db() as session:
        interactor = ApplyWalletOperationInteractor(SQLAlchemyWalletUnitOfWork(session))

        balance = await interactor.execute(
            ApplyWalletOperationInput(wallet_id, 5000, OperationType.DEPOSIT)
        )
        outbox_events = await SQLAlchemyOutboxRepository(session).get_waiting(limit=10)
        outbox_event = await session.get(
            OutboxEventModel,
            outbox_events[0].id,
        )

        assert balance == 150.0
        assert len(outbox_events) == 1
        assert outbox_event is not None
        assert outbox_event.aggregate_type == "wallet"
        assert outbox_event.aggregate_id == wallet_id
        assert outbox_event.event_type == "wallet.transaction.created"
        assert outbox_event.payload == {
            "wallet_id": str(wallet_id),
            "operation_type": "DEPOSIT",
            "amount_cent": 5000,
            "balance_cent": 15000,
        }


async def test_wallet_operation_rolls_back_if_outbox_write_fails(test_db, wallet):
    wallet_id = wallet

    class FailingOutboxRepository(SQLAlchemyOutboxRepository):
        async def add(self, event):  # type: ignore[override]
            raise RuntimeError("Outbox insert failed")

    class FailingOutboxUnitOfWork(SQLAlchemyWalletUnitOfWork):
        def __init__(self, session):
            super().__init__(session)
            self.outbox = FailingOutboxRepository(session)

    async with test_db() as session:
        interactor = ApplyWalletOperationInteractor(FailingOutboxUnitOfWork(session))

        with pytest.raises(WalletOperationError):
            await interactor.execute(
                ApplyWalletOperationInput(wallet_id, 5000, OperationType.DEPOSIT)
            )

        wallet_repository = SQLAlchemyWalletRepository(session)
        persisted_wallet = await wallet_repository.get_wallet_by_id(wallet_id)
        operation_count = len((await session.scalars(select(OperationModel))).all())
        outbox_count = len((await session.scalars(select(OutboxEventModel))).all())

        assert persisted_wallet is not None
        assert persisted_wallet.balance_cent == 10000
        assert operation_count == 0
        assert outbox_count == 0
