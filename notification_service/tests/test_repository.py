import uuid

import pytest

from notification_service.domain.notification import Notification, WalletOperationType
from notification_service.infrastructure.sa.repositories import (
    notification_repository as notification_repository_module,
)

pytestmark = pytest.mark.asyncio


async def test_get_by_source_event_id_success(test_db, notification_event):
    async with test_db() as session:
        repository = notification_repository_module.SQLAlchemyNotificationRepository(
            session
        )

        notification = await repository.get_by_source_event_id(notification_event)

        assert notification is not None
        assert notification.source_event_id == notification_event


async def test_get_by_source_event_id_not_found(test_db):
    async with test_db() as session:
        repository = notification_repository_module.SQLAlchemyNotificationRepository(
            session
        )

        notification = await repository.get_by_source_event_id(uuid.uuid4())

        assert notification is None


async def test_add_notification_success(test_db):
    source_event_id = uuid.uuid4()
    user_id = uuid.uuid4()
    wallet_id = uuid.uuid4()

    async with test_db() as session:
        repository = notification_repository_module.SQLAlchemyNotificationRepository(
            session
        )
        await repository.add(
            Notification(
                source_event_id=source_event_id,
                user_id=user_id,
                wallet_id=wallet_id,
                operation_type=WalletOperationType.DEPOSIT,
                amount_cent=5000,
                balance_cent=15000,
                message="Deposit received: 50.00 RUB. Current balance: 150.00 RUB.",
            )
        )
        await session.commit()

        stored = await repository.get_by_source_event_id(source_event_id)

        assert stored is not None
        assert stored.user_id == user_id
        assert stored.wallet_id == wallet_id


async def test_list_recent_returns_notifications(test_db, notification_event):
    async with test_db() as session:
        repository = notification_repository_module.SQLAlchemyNotificationRepository(
            session
        )

        notifications = await repository.list_recent(
            user_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            limit=10,
        )

        assert len(notifications) == 1
        assert notifications[0].source_event_id == notification_event


async def test_list_recent_filters_by_wallet_id(test_db):
    owner_user_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    target_wallet_id = uuid.uuid4()
    other_wallet_id = uuid.uuid4()

    async with test_db() as session:
        repository = notification_repository_module.SQLAlchemyNotificationRepository(
            session
        )
        await repository.add(
            Notification(
                source_event_id=uuid.uuid4(),
                user_id=owner_user_id,
                wallet_id=target_wallet_id,
                operation_type=WalletOperationType.DEPOSIT,
                amount_cent=1000,
                balance_cent=1000,
                message="target",
            )
        )
        await repository.add(
            Notification(
                source_event_id=uuid.uuid4(),
                user_id=owner_user_id,
                wallet_id=other_wallet_id,
                operation_type=WalletOperationType.DEPOSIT,
                amount_cent=2000,
                balance_cent=3000,
                message="other",
            )
        )
        await session.commit()

        notifications = await repository.list_recent(
            user_id=owner_user_id,
            wallet_id=target_wallet_id,
            limit=10,
        )

        assert len(notifications) == 1
        assert notifications[0].wallet_id == target_wallet_id
