import uuid
from unittest.mock import AsyncMock

import pytest

from notification_service.application.commands.handle_wallet_transaction import (
    HandleWalletTransactionInput,
    HandleWalletTransactionInteractor,
)
from notification_service.application.queries.list_notifications.interactor import (
    ListNotificationsInteractor,
)
from notification_service.domain.exceptions import (
    InvalidNotificationAmountError,
    NotificationProcessingError,
)
from notification_service.domain.notification import Notification, WalletOperationType

pytestmark = pytest.mark.asyncio


async def test_handle_wallet_transaction_creates_notification(
    handle_wallet_transaction_interactor: HandleWalletTransactionInteractor,
    mock_notification_repository,
    mock_notification_unit_of_work,
):
    source_event_id = uuid.uuid4()
    user_id = uuid.uuid4()
    wallet_id = uuid.uuid4()
    mock_notification_repository.get_by_source_event_id = AsyncMock(return_value=None)
    mock_notification_repository.add = AsyncMock(return_value=None)

    created = await handle_wallet_transaction_interactor.execute(
        HandleWalletTransactionInput(
            source_event_id=source_event_id,
            user_id=user_id,
            wallet_id=wallet_id,
            operation_type=WalletOperationType.DEPOSIT,
            amount_cent=5000,
            balance_cent=15000,
        )
    )

    assert created is True
    mock_notification_repository.add.assert_awaited_once()
    stored = mock_notification_repository.add.await_args.args[0]
    assert stored.source_event_id == source_event_id
    assert stored.user_id == user_id
    assert stored.wallet_id == wallet_id
    assert stored.operation_type == WalletOperationType.DEPOSIT
    assert stored.message == "Deposit received: 50.00 RUB. Current balance: 150.00 RUB."
    mock_notification_unit_of_work.commit.assert_awaited_once()


async def test_handle_wallet_transaction_is_idempotent(
    handle_wallet_transaction_interactor: HandleWalletTransactionInteractor,
    mock_notification_repository,
):
    mock_notification_repository.get_by_source_event_id = AsyncMock(
        return_value=Notification(
            source_event_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            wallet_id=uuid.uuid4(),
            operation_type=WalletOperationType.DEPOSIT,
            amount_cent=1000,
            balance_cent=1000,
            message="existing",
        )
    )

    created = await handle_wallet_transaction_interactor.execute(
        HandleWalletTransactionInput(
            source_event_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            wallet_id=uuid.uuid4(),
            operation_type=WalletOperationType.DEPOSIT,
            amount_cent=5000,
            balance_cent=15000,
        )
    )

    assert created is False


async def test_handle_wallet_transaction_invalid_amount(
    handle_wallet_transaction_interactor: HandleWalletTransactionInteractor,
):
    with pytest.raises(InvalidNotificationAmountError):
        await handle_wallet_transaction_interactor.execute(
            HandleWalletTransactionInput(
                source_event_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                wallet_id=uuid.uuid4(),
                operation_type=WalletOperationType.WITHDRAWAL,
                amount_cent=0,
                balance_cent=5000,
            )
        )


async def test_handle_wallet_transaction_rolls_back_on_error(
    handle_wallet_transaction_interactor: HandleWalletTransactionInteractor,
    mock_notification_repository,
    mock_notification_unit_of_work,
):
    mock_notification_repository.get_by_source_event_id = AsyncMock(return_value=None)
    mock_notification_repository.add = AsyncMock(side_effect=RuntimeError("db error"))

    with pytest.raises(NotificationProcessingError):
        await handle_wallet_transaction_interactor.execute(
            HandleWalletTransactionInput(
                source_event_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                wallet_id=uuid.uuid4(),
                operation_type=WalletOperationType.WITHDRAWAL,
                amount_cent=1000,
                balance_cent=9000,
            )
        )

    mock_notification_unit_of_work.rollback.assert_awaited_once()


async def test_list_notifications_returns_gateway_result(
    list_notifications_interactor: ListNotificationsInteractor,
    mock_notification_repository,
):
    notification = Notification(
        source_event_id=uuid.uuid4(),
        user_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        wallet_id=uuid.uuid4(),
        operation_type=WalletOperationType.DEPOSIT,
        amount_cent=1000,
        balance_cent=1000,
        message="Deposit received",
    )
    mock_notification_repository.list_recent = AsyncMock(return_value=[notification])

    result = await list_notifications_interactor.execute(
        uuid.UUID("11111111-1111-1111-1111-111111111111"),
        None,
        limit=10,
    )

    assert result == [notification]
    mock_notification_repository.list_recent.assert_awaited_once_with(
        user_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        wallet_id=None,
        limit=10,
    )
