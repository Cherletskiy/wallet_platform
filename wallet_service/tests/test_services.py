import uuid
from unittest.mock import AsyncMock

import pytest

from wallet_service.application.commands.apply_wallet_operation import (
    ApplyWalletOperationInput,
    ApplyWalletOperationInteractor,
)
from wallet_service.application.commands.create_wallet import (
    CreateWalletInput,
    CreateWalletInteractor,
)
from wallet_service.application.queries.get_wallet_balance import (
    GetWalletBalanceInteractor,
)
from wallet_service.domain.exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    WalletAccessDeniedError,
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
    mock_wallet_repository.get_wallet_by_id = AsyncMock(
        return_value=Wallet(
            id=wallet_id,
            owner_user_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            balance_cent=10000,
        )
    )

    balance = await get_wallet_balance_interactor.execute(
        wallet_id,
        uuid.UUID("11111111-1111-1111-1111-111111111111"),
    )

    assert balance == 100.0
    mock_wallet_repository.get_wallet_by_id.assert_called_once()


async def test_get_wallet_balance_rub_not_found(
    get_wallet_balance_interactor: GetWalletBalanceInteractor,
    mock_wallet_repository,
):
    wallet_id = uuid.uuid4()
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=None)

    with pytest.raises(WalletNotFoundError):
        await get_wallet_balance_interactor.execute(wallet_id, uuid.uuid4())


async def test_update_wallet_balance_deposit_success(
    apply_wallet_operation_interactor: ApplyWalletOperationInteractor,
    mock_wallet_repository,
    mock_outbox_repository,
    mock_wallet_unit_of_work,
):
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(
        id=wallet_id,
        owner_user_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        balance_cent=10000,
    )
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)
    mock_wallet_repository.update_wallet_balance_cent = AsyncMock(return_value=None)
    mock_wallet_repository.add_operation = AsyncMock(return_value=None)
    mock_outbox_repository.add = AsyncMock(return_value=None)

    balance = await apply_wallet_operation_interactor.execute(
        ApplyWalletOperationInput(wallet_id, 5000, OperationType.DEPOSIT),
        uuid.UUID("11111111-1111-1111-1111-111111111111"),
    )

    assert balance == 150.0
    mock_wallet_repository.update_wallet_balance_cent.assert_called_once_with(
        wallet_id, 15000
    )
    mock_wallet_repository.add_operation.assert_called_once_with(
        wallet_id, OperationType.DEPOSIT, 5000
    )
    mock_outbox_repository.add.assert_awaited_once()
    outbox_event = mock_outbox_repository.add.await_args.args[0]
    assert outbox_event.aggregate_type == "wallet"
    assert outbox_event.aggregate_id == wallet_id
    assert outbox_event.event_type == "wallet.transaction.created"
    assert outbox_event.status.value == "PENDING"
    assert outbox_event.retry_count == 0
    assert outbox_event.payload == {
        "wallet_id": str(wallet_id),
        "operation_type": "DEPOSIT",
        "amount_cent": 5000,
        "balance_cent": 15000,
    }
    mock_wallet_unit_of_work.commit.assert_called_once()


async def test_update_wallet_balance_withdrawal_success(
    apply_wallet_operation_interactor: ApplyWalletOperationInteractor,
    mock_wallet_repository,
    mock_outbox_repository,
    mock_wallet_unit_of_work,
):
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(
        id=wallet_id,
        owner_user_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        balance_cent=10000,
    )
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)
    mock_wallet_repository.update_wallet_balance_cent = AsyncMock(return_value=None)
    mock_wallet_repository.add_operation = AsyncMock(return_value=None)
    mock_outbox_repository.add = AsyncMock(return_value=None)

    balance = await apply_wallet_operation_interactor.execute(
        ApplyWalletOperationInput(wallet_id, 5000, OperationType.WITHDRAWAL),
        uuid.UUID("11111111-1111-1111-1111-111111111111"),
    )

    assert balance == 50.0
    mock_wallet_repository.update_wallet_balance_cent.assert_called_once_with(
        wallet_id, 5000
    )
    mock_wallet_repository.add_operation.assert_called_once_with(
        wallet_id, OperationType.WITHDRAWAL, 5000
    )
    mock_outbox_repository.add.assert_awaited_once()
    mock_wallet_unit_of_work.commit.assert_called_once()


async def test_update_wallet_balance_withdrawal_insufficient(
    apply_wallet_operation_interactor: ApplyWalletOperationInteractor,
    mock_wallet_repository,
):
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(
        id=wallet_id,
        owner_user_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        balance_cent=1000,
    )
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)

    with pytest.raises(InsufficientFundsError):
        await apply_wallet_operation_interactor.execute(
            ApplyWalletOperationInput(wallet_id, 5000, OperationType.WITHDRAWAL),
            uuid.UUID("11111111-1111-1111-1111-111111111111"),
        )


async def test_update_wallet_balance_invalid_amount(
    apply_wallet_operation_interactor: ApplyWalletOperationInteractor,
    mock_wallet_repository,
):
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(
        id=wallet_id,
        owner_user_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        balance_cent=10000,
    )
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)
    mock_wallet_repository.update_wallet_balance_cent = AsyncMock(return_value=None)
    mock_wallet_repository.add_operation = AsyncMock(return_value=None)

    with pytest.raises(InvalidAmountError):
        await apply_wallet_operation_interactor.execute(
            ApplyWalletOperationInput(wallet_id, -5000, OperationType.DEPOSIT),
            uuid.UUID("11111111-1111-1111-1111-111111111111"),
        )


async def test_get_wallet_balance_rub_repository_exception(
    get_wallet_balance_interactor: GetWalletBalanceInteractor,
    mock_wallet_repository,
):
    wallet_id = uuid.uuid4()
    mock_wallet_repository.get_wallet_by_id = AsyncMock(
        side_effect=Exception("Repository error")
    )

    with pytest.raises(WalletBalanceError):
        await get_wallet_balance_interactor.execute(wallet_id, uuid.uuid4())


async def test_update_wallet_balance_cent_general_exception(
    apply_wallet_operation_interactor: ApplyWalletOperationInteractor,
    mock_wallet_repository,
    mock_outbox_repository,
    mock_wallet_unit_of_work,
):
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(
        id=wallet_id,
        owner_user_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        balance_cent=10000,
    )
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)
    mock_wallet_repository.update_wallet_balance_cent = AsyncMock(
        side_effect=Exception("Database failure")
    )
    mock_wallet_repository.add_operation = AsyncMock(return_value=None)
    mock_outbox_repository.add = AsyncMock(return_value=None)

    with pytest.raises(WalletOperationError):
        await apply_wallet_operation_interactor.execute(
            ApplyWalletOperationInput(wallet_id, 5000, OperationType.DEPOSIT),
            uuid.UUID("11111111-1111-1111-1111-111111111111"),
        )
    mock_wallet_unit_of_work.rollback.assert_called_once()


async def test_update_wallet_balance_outbox_exception_rolls_back(
    apply_wallet_operation_interactor: ApplyWalletOperationInteractor,
    mock_wallet_repository,
    mock_outbox_repository,
    mock_wallet_unit_of_work,
):
    wallet_id = uuid.uuid4()
    mock_wallet = Wallet(
        id=wallet_id,
        owner_user_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        balance_cent=10000,
    )
    mock_wallet_repository.get_wallet_by_id = AsyncMock(return_value=mock_wallet)
    mock_wallet_repository.update_wallet_balance_cent = AsyncMock(return_value=None)
    mock_wallet_repository.add_operation = AsyncMock(return_value=None)
    mock_outbox_repository.add = AsyncMock(side_effect=RuntimeError("Outbox failure"))

    with pytest.raises(WalletOperationError):
        await apply_wallet_operation_interactor.execute(
            ApplyWalletOperationInput(wallet_id, 5000, OperationType.DEPOSIT),
            uuid.UUID("11111111-1111-1111-1111-111111111111"),
        )

    mock_wallet_unit_of_work.rollback.assert_called_once()


async def test_get_wallet_balance_access_denied(
    get_wallet_balance_interactor: GetWalletBalanceInteractor,
    mock_wallet_repository,
):
    wallet_id = uuid.uuid4()
    mock_wallet_repository.get_wallet_by_id = AsyncMock(
        return_value=Wallet(
            id=wallet_id,
            owner_user_id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
            balance_cent=10000,
        )
    )

    with pytest.raises(WalletAccessDeniedError):
        await get_wallet_balance_interactor.execute(
            wallet_id,
            uuid.UUID("11111111-1111-1111-1111-111111111111"),
        )


async def test_create_wallet_success(
    create_wallet_interactor: CreateWalletInteractor,
    mock_wallet_repository,
    mock_wallet_unit_of_work,
):
    owner_user_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    created_wallet = Wallet(
        id=uuid.uuid4(), owner_user_id=owner_user_id, balance_cent=0
    )
    mock_wallet_repository.create_wallet = AsyncMock(return_value=created_wallet)

    wallet = await create_wallet_interactor.execute(CreateWalletInput(owner_user_id))

    assert wallet == created_wallet
    mock_wallet_repository.create_wallet.assert_awaited_once_with(owner_user_id)
    mock_wallet_unit_of_work.commit.assert_called_once()
