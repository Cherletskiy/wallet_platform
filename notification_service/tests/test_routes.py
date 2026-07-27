import uuid
from unittest.mock import AsyncMock

import pytest

from notification_service.domain.notification import Notification, WalletOperationType

pytestmark = pytest.mark.asyncio


async def test_health_route(client):
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_list_notifications_route(client, mock_notification_repository):
    notification = Notification(
        id=uuid.uuid4(),
        source_event_id=uuid.uuid4(),
        wallet_id=uuid.uuid4(),
        operation_type=WalletOperationType.DEPOSIT,
        amount_cent=5000,
        balance_cent=15000,
        message="Deposit received: 50.00 RUB. Current balance: 150.00 RUB.",
    )
    mock_notification_repository.list_recent = AsyncMock(return_value=[notification])

    response = await client.get("/api/v1/notifications?limit=10")

    assert response.status_code == 200
    assert response.json()[0]["operation_type"] == "DEPOSIT"
    assert response.json()[0]["amount_rub"] == 50.0
    assert response.json()[0]["balance_rub"] == 150.0
