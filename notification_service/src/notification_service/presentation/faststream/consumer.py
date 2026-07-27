import uuid
from collections.abc import Awaitable, Callable

from faststream.kafka import KafkaBroker
from faststream.kafka.message import KafkaMessage
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from notification_service.application.commands.handle_wallet_transaction import (
    HandleWalletTransactionInput,
    HandleWalletTransactionInteractor,
)
from notification_service.domain.notification import WalletOperationType
from notification_service.infrastructure.logging import setup_logger
from notification_service.infrastructure.sa.unit_of_work import (
    SQLAlchemyNotificationUnitOfWork,
)

logger = setup_logger(__name__)


class WalletTransactionCreatedMessage(BaseModel):
    wallet_id: uuid.UUID
    operation_type: WalletOperationType
    amount_cent: int
    balance_cent: int


async def process_wallet_transaction_message(
    message: WalletTransactionCreatedMessage,
    source_event_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
) -> bool:
    async with session_factory() as session:
        interactor = HandleWalletTransactionInteractor(
            SQLAlchemyNotificationUnitOfWork(session)
        )
        return await interactor.execute(
            HandleWalletTransactionInput(
                source_event_id=source_event_id,
                wallet_id=message.wallet_id,
                operation_type=message.operation_type,
                amount_cent=message.amount_cent,
                balance_cent=message.balance_cent,
            )
        )


def register_wallet_transaction_consumer(
    broker: KafkaBroker,
    session_factory: async_sessionmaker[AsyncSession],
) -> Callable[[WalletTransactionCreatedMessage, KafkaMessage], Awaitable[None]]:
    @broker.subscriber(
        "wallet.transaction.created",
        group_id="notification-service",
    )
    async def wallet_transaction_created(
        message: WalletTransactionCreatedMessage,
        kafka_message: KafkaMessage,
    ) -> None:
        event_id = uuid.UUID(kafka_message.correlation_id)
        created = await process_wallet_transaction_message(
            message,
            event_id,
            session_factory,
        )
        logger.info(
            "Processed wallet transaction notification: event_id=%s created=%s",
            event_id,
            created,
        )

    return wallet_transaction_created
