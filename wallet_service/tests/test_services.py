import uuid
from unittest.mock import AsyncMock

import pytest

from wallet_service.application.commands.apply_wallet_operation import (
    ApplyWalletOperationInput,
    ApplyWalletOperationInteractor,
)
from wallet_service.application.queries.get_wallet_balance import (
    GetWalletBalanceInteractor,
)
from wallet_service.domain.exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    WalletBalanceError,
    WalletNotFoundError,
    WalletOperationError,
)
from wallet_service.domain.wallet import OperationType, Wallet

pytestmark = pytest.mark.asyncio


async def test_get_wallet_balance_rub_success(
    get_wallet_balance_interactor: GetWalletBalanceInteractor,
    mock_wallet_repository,
):
    wallet_id = uuid.uuid4()
    mock_wallet_repository.get_wallet_balance_cent = AsyncMock(
        return_value=10000
    )

    balance = await get_wallet_balance_interactor.execute(wallet_id)

    assert balance == 100.0
    mock_wallet_repository.get_wallet_balance_cent.assert_called_once()


async def test_get_wallet_balance_rub_not_found(
    get_wallet_balance_interactor: GetWalletBalanceInteractor,
    mock_wallet_repository,
):
    wallet_id = uuid.uuid4()
    mock_wallet_repository.get_wallet_balance_cent = AsyncMock(return_value=None)

    with pytest.raises(WalletNotFoundError):
        await get_wallet_balance_interactor.execute(wallet_id)


async def test_update_wallet_balance_deposit_success(
    apply_wallet_operation_interactor: ApplyWalletOperationInteractor,
    mock_wallet_repository,
    mock_wallet_unit_of_work,
):
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(id=wallet_id, balance_cent=10000)
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)
    mock_wallet_repository.update_wallet_balance_cent = AsyncMock(return_value=None)
    mock_wallet_repository.add_operation = AsyncMock(return_value=None)

    balance = await apply_wallet_operation_interactor.execute(
        ApplyWalletOperationInput(wallet_id, 5000, OperationType.DEPOSIT)
    )

    assert balance == 150.0
    mock_wallet_repository.update_wallet_balance_cent.assert_called_once_with(
        wallet_id, 15000
    )
    mock_wallet_repository.add_operation.assert_called_once_with(
        wallet_id, OperationType.DEPOSIT, 5000
    )
    mock_wallet_unit_of_work.commit.assert_called_once()


async def test_update_wallet_balance_withdrawal_success(
    apply_wallet_operation_interactor: ApplyWalletOperationInteractor,
    mock_wallet_repository,
    mock_wallet_unit_of_work,
):
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(id=wallet_id, balance_cent=10000)
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)
    mock_wallet_repository.update_wallet_balance_cent = AsyncMock(return_value=None)
    mock_wallet_repository.add_operation = AsyncMock(return_value=None)

    balance = await apply_wallet_operation_interactor.execute(
        ApplyWalletOperationInput(wallet_id, 5000, OperationType.WITHDRAWAL)
    )

    assert balance == 50.0
    mock_wallet_repository.update_wallet_balance_cent.assert_called_once_with(
        wallet_id, 5000
    )
    mock_wallet_repository.add_operation.assert_called_once_with(
        wallet_id, OperationType.WITHDRAWAL, 5000
    )
    mock_wallet_unit_of_work.commit.assert_called_once()


async def test_update_wallet_balance_withdrawal_insufficient(
    apply_wallet_operation_interactor: ApplyWalletOperationInteractor,
    mock_wallet_repository,
):
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(id=wallet_id, balance_cent=1000)
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)

    with pytest.raises(InsufficientFundsError):
        await apply_wallet_operation_interactor.execute(
            ApplyWalletOperationInput(wallet_id, 5000, OperationType.WITHDRAWAL)
        )


async def test_update_wallet_balance_invalid_amount(
    apply_wallet_operation_interactor: ApplyWalletOperationInteractor,
    mock_wallet_repository,
):
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(id=wallet_id, balance_cent=10000)
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)
    mock_wallet_repository.update_wallet_balance_cent = AsyncMock(return_value=None)
    mock_wallet_repository.add_operation = AsyncMock(return_value=None)

    with pytest.raises(InvalidAmountError):
        await apply_wallet_operation_interactor.execute(
            ApplyWalletOperationInput(wallet_id, -5000, OperationType.DEPOSIT)
        )


async def test_get_wallet_balance_rub_repository_exception(
    get_wallet_balance_interactor: GetWalletBalanceInteractor,
    mock_wallet_repository,
):
    wallet_id = uuid.uuid4()
    mock_wallet_repository.get_wallet_balance_cent = AsyncMock(
        side_effect=Exception("Repository error")
    )

    with pytest.raises(WalletBalanceError):
        await get_wallet_balance_interactor.execute(wallet_id)


async def test_update_wallet_balance_cent_general_exception(
    apply_wallet_operation_interactor: ApplyWalletOperationInteractor,
    mock_wallet_repository,
):
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(id=wallet_id, balance_cent=10000)
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)
    mock_wallet_repository.update_wallet_balance_cent = AsyncMock(
        side_effect=Exception("Database failure")
    )
    mock_wallet_repository.add_operation = AsyncMock(return_value=None)

    with pytest.raises(WalletOperationError):
        await apply_wallet_operation_interactor.execute(
            ApplyWalletOperationInput(wallet_id, 5000, OperationType.DEPOSIT)
        )
