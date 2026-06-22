import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import OperationType, Wallet
from app.services.wallet_service import WalletService

pytestmark = pytest.mark.asyncio


async def test_get_wallet_balance_rub_success(
    wallet_service: WalletService, mock_wallet_repository
):
    """Тест успешного получения баланса в рублях."""
    wallet_id = uuid.uuid4()
    mock_wallet_repository.get_wallet_balance_cent = AsyncMock(
        return_value=10000
    )  # 100 рублей

    balance = await wallet_service.get_wallet_balance_rub(None, wallet_id)

    assert balance == 100.0
    mock_wallet_repository.get_wallet_balance_cent.assert_called_once()


async def test_get_wallet_balance_rub_not_found(
    wallet_service: WalletService, mock_wallet_repository
):
    """Тест ошибки при отсутствии кошелька."""
    wallet_id = uuid.uuid4()
    mock_wallet_repository.get_wallet_balance_cent = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await wallet_service.get_wallet_balance_rub(None, wallet_id)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Wallet not found"


async def test_update_wallet_balance_deposit_success(
    wallet_service: WalletService, mock_wallet_repository
):
    """Тест успешной операции DEPOSIT."""
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(id=wallet_id, balance_cent=10000)  # 100 рублей
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)
    mock_wallet_repository.update_wallet_balance_cent = AsyncMock(return_value=None)
    mock_wallet_repository.add_operation = AsyncMock(return_value=None)

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.commit = AsyncMock(return_value=None)

    balance = await wallet_service.update_wallet_balance_cent(
        mock_session, wallet_id, 5000, OperationType.DEPOSIT
    )

    assert balance == 150.0
    mock_wallet_repository.update_wallet_balance_cent.assert_called_once_with(
        mock_session, wallet_id, 15000
    )
    mock_wallet_repository.add_operation.assert_called_once_with(
        mock_session, wallet_id, OperationType.DEPOSIT, 5000
    )
    mock_session.commit.assert_called_once()


async def test_update_wallet_balance_withdrawal_success(
    wallet_service: WalletService, mock_wallet_repository
):
    """Тест успешной операции WITHDRAWAL."""
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(id=wallet_id, balance_cent=10000)  # 100 рублей
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)
    mock_wallet_repository.update_wallet_balance_cent = AsyncMock(return_value=None)
    mock_wallet_repository.add_operation = AsyncMock(return_value=None)

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.commit = AsyncMock(return_value=None)

    balance = await wallet_service.update_wallet_balance_cent(
        mock_session, wallet_id, 5000, OperationType.WITHDRAWAL
    )

    assert balance == 50.0
    mock_wallet_repository.update_wallet_balance_cent.assert_called_once_with(
        mock_session, wallet_id, 5000
    )
    mock_wallet_repository.add_operation.assert_called_once_with(
        mock_session, wallet_id, OperationType.WITHDRAWAL, 5000
    )
    mock_session.commit.assert_called_once()


async def test_update_wallet_balance_withdrawal_insufficient(
    wallet_service: WalletService, mock_wallet_repository
):
    """Тест ошибки при недостаточном балансе для WITHDRAWAL."""
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(id=wallet_id, balance_cent=1000)  # 10 рублей
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.commit = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await wallet_service.update_wallet_balance_cent(
            mock_session, wallet_id, 5000, OperationType.WITHDRAWAL
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Not enough balance"


async def test_update_wallet_balance_invalid_amount(
    wallet_service: WalletService, mock_wallet_repository
):
    """Тест ошибки при отрицательной сумме."""
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(id=wallet_id, balance_cent=10000)
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)
    mock_wallet_repository.update_wallet_balance_cent = AsyncMock(return_value=None)
    mock_wallet_repository.add_operation = AsyncMock(return_value=None)

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.commit = AsyncMock(return_value=None)

    # Проверяем, что отрицательная сумма вызывает HTTPException
    with pytest.raises(HTTPException) as exc:
        await wallet_service.update_wallet_balance_cent(
            mock_session, wallet_id, -5000, OperationType.DEPOSIT
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Amount must be greater than 0"


async def test_get_wallet_balance_rub_repository_exception(
    wallet_service: WalletService, mock_wallet_repository
):
    """Тест обработки HTTPException из репозитория в get_wallet_balance_rub."""
    wallet_id = uuid.uuid4()
    mock_wallet_repository.get_wallet_balance_cent = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Repository error"
        )
    )

    with pytest.raises(HTTPException) as exc:
        await wallet_service.get_wallet_balance_rub(None, wallet_id)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Repository error"


async def test_update_wallet_balance_cent_general_exception(
    wallet_service: WalletService, mock_wallet_repository
):
    """Тест обработки общей ошибки в update_wallet_balance_cent."""
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(id=wallet_id, balance_cent=10000)
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)
    mock_wallet_repository.update_wallet_balance_cent = AsyncMock(
        side_effect=Exception("Database failure")
    )
    mock_wallet_repository.add_operation = AsyncMock(return_value=None)

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.commit = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await wallet_service.update_wallet_balance_cent(
            mock_session, wallet_id, 5000, OperationType.DEPOSIT
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Error updating wallet balance"
