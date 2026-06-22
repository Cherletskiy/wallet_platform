import uuid
from unittest.mock import AsyncMock

from wallet_service.domain.wallet import OperationType, Wallet

base_url = "/api/v1/wallets"


def test_get_wallet_balance_success(client, mock_wallet_repository):
    wallet_id = uuid.uuid4()
    mock_wallet_repository.get_wallet_balance_cent = AsyncMock(
        return_value=10000
    )

    response = client.get(f"{base_url}/{wallet_id}")

    assert response.status_code == 200
    assert response.json() == {"balance_rub": 100.0}
    mock_wallet_repository.get_wallet_balance_cent.assert_called_once()


def test_get_wallet_balance_not_found(client, mock_wallet_repository):
    wallet_id = uuid.uuid4()
    mock_wallet_repository.get_wallet_balance_cent = AsyncMock(return_value=None)

    response = client.get(f"{base_url}/{wallet_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Wallet not found"


def test_wallet_deposit_success(client, mock_wallet_repository):
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(id=wallet_id, balance_cent=10000)
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)
    mock_wallet_repository.update_wallet_balance_cent = AsyncMock()
    mock_wallet_repository.add_operation = AsyncMock()

    response = client.post(
        f"{base_url}/{wallet_id}/operation",
        json={"amount": 50.0, "operation_type": "DEPOSIT"},
    )

    assert response.status_code == 200
    assert response.json() == {"balance_rub": 150.0}
    mock_wallet_repository.update_wallet_balance_cent.assert_called_once_with(
        wallet_id,
        15000,
    )
    mock_wallet_repository.add_operation.assert_called_once_with(
        wallet_id,
        OperationType.DEPOSIT,
        5000,
    )


def test_wallet_withdrawal_success(client, mock_wallet_repository):
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(id=wallet_id, balance_cent=10000)
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)
    mock_wallet_repository.update_wallet_balance_cent = AsyncMock()
    mock_wallet_repository.add_operation = AsyncMock()

    response = client.post(
        f"{base_url}/{wallet_id}/operation",
        json={"amount": 50.0, "operation_type": "WITHDRAWAL"},
    )

    assert response.status_code == 200
    assert response.json() == {"balance_rub": 50.0}
    mock_wallet_repository.update_wallet_balance_cent.assert_called_once_with(
        wallet_id,
        5000,
    )
    mock_wallet_repository.add_operation.assert_called_once_with(
        wallet_id,
        OperationType.WITHDRAWAL,
        5000,
    )


def test_wallet_withdrawal_insufficient_balance(client, mock_wallet_repository):
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(id=wallet_id, balance_cent=1000)
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)

    response = client.post(
        f"{base_url}/{wallet_id}/operation",
        json={"amount": 50.0, "operation_type": "WITHDRAWAL"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Not enough balance"


def test_wallet_operation_invalid_amount(client, mock_wallet_repository):
    wallet_id = uuid.uuid4()
    response = client.post(
        f"{base_url}/{wallet_id}/operation",
        json={"amount": -10.0, "operation_type": "DEPOSIT"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "greater_than"


def test_wallet_operation_invalid_amount_decimal_places(client, mock_wallet_repository):
    wallet_id = uuid.uuid4()
    response = client.post(
        f"{base_url}/{wallet_id}/operation",
        json={"amount": 10.123, "operation_type": "DEPOSIT"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "decimal_max_places"


def test_wallet_operation_invalid_operation_type(client, mock_wallet_repository):
    wallet_id = uuid.uuid4()
    response = client.post(
        f"{base_url}/{wallet_id}/operation",
        json={"amount": 10.0, "operation_type": "INVALID"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "enum"
