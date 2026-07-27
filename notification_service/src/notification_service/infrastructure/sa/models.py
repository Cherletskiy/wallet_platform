import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Enum, Integer, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from notification_service.domain.notification import WalletOperationType


class Base(DeclarativeBase, AsyncAttrs):
    pass


class NotificationModel(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    source_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
    )
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    operation_type: Mapped[WalletOperationType] = mapped_column(
        Enum(WalletOperationType, name="walletoperationtype"),
        nullable=False,
    )
    amount_cent: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_cent: Mapped[int] = mapped_column(Integer, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    __table_args__ = (
        UniqueConstraint("source_event_id", name="uq_notifications_source_event_id"),
    )
