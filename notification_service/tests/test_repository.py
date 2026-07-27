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
    wallet_id = uuid.uuid4()

    async with test_db() as session:
        repository = notification_repository_module.SQLAlchemyNotificationRepository(
            session
        )
        await repository.add(
            Notification(
                source_event_id=source_event_id,
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
        assert stored.wallet_id == wallet_id


async def test_list_recent_returns_notifications(test_db, notification_event):
    async with test_db() as session:
        repository = notification_repository_module.SQLAlchemyNotificationRepository(
            session
        )

        notifications = await repository.list_recent(limit=10)

        assert len(notifications) == 1
        assert notifications[0].source_event_id == notification_event
