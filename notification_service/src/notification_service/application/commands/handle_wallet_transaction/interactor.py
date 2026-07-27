from notification_service.application.commands.handle_wallet_transaction.dto import (
    HandleWalletTransactionInput,
)
from notification_service.application.unit_of_work import NotificationUnitOfWork
from notification_service.domain.exceptions import (
    InvalidNotificationAmountError,
    NotificationProcessingError,
)
from notification_service.domain.notification import Notification, WalletOperationType


def format_rubles(amount_cent: int) -> str:
    return f"{amount_cent / 100:.2f}"


class HandleWalletTransactionInteractor:
    def __init__(self, uow: NotificationUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, data: HandleWalletTransactionInput) -> bool:
        if data.amount_cent <= 0:
            raise InvalidNotificationAmountError

        existing = await self._uow.notifications.get_by_source_event_id(
            data.source_event_id
        )
        if existing is not None:
            return False

        message = self._build_message(
            data.operation_type,
            data.amount_cent,
            data.balance_cent,
        )

        try:
            await self._uow.notifications.add(
                Notification(
                    source_event_id=data.source_event_id,
                    wallet_id=data.wallet_id,
                    operation_type=data.operation_type,
                    amount_cent=data.amount_cent,
                    balance_cent=data.balance_cent,
                    message=message,
                )
            )
            await self._uow.commit()
        except Exception as exc:
            await self._uow.rollback()
            raise NotificationProcessingError from exc

        return True

    @staticmethod
    def _build_message(
        operation_type: WalletOperationType,
        amount_cent: int,
        balance_cent: int,
    ) -> str:
        action = (
            "Deposit received"
            if operation_type == WalletOperationType.DEPOSIT
            else "Withdrawal completed"
        )
        return (
            f"{action}: {format_rubles(amount_cent)} RUB. "
            f"Current balance: {format_rubles(balance_cent)} RUB."
        )
