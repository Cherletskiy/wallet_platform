import uuid

import pytest

from notification_service.application.commands.handle_wallet_transaction.dto import (
    HandleWalletTransactionInput,
)
from notification_service.domain.notification import WalletOperationType
from notification_service.presentation.faststream.consumer import (
    WalletTransactionCreatedMessage,
    process_wallet_transaction_message,
)

pytestmark = pytest.mark.asyncio


async def test_process_wallet_transaction_message_persists_notification(test_db):
    source_event_id = uuid.uuid4()
    user_id = uuid.uuid4()
    wallet_id = uuid.uuid4()

    created = await process_wallet_transaction_message(
        WalletTransactionCreatedMessage(
            user_id=user_id,
            wallet_id=wallet_id,
            operation_type=WalletOperationType.DEPOSIT,
            amount_cent=5000,
            balance_cent=15000,
        ),
        source_event_id,
        test_db,
    )

    assert created is True


async def test_handle_wallet_transaction_input_shape() -> None:
    payload = HandleWalletTransactionInput(
        source_event_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        wallet_id=uuid.uuid4(),
        operation_type=WalletOperationType.WITHDRAWAL,
        amount_cent=1000,
        balance_cent=9000,
    )

    assert payload.amount_cent == 1000
