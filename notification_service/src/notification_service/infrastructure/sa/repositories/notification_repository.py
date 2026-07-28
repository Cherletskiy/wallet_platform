import uuid
from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.domain.notification import Notification
from notification_service.infrastructure.sa.mappers import map_notification_model
from notification_service.infrastructure.sa.models import NotificationModel


class SQLAlchemyNotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_source_event_id(
        self,
        source_event_id: uuid.UUID,
    ) -> Notification | None:
        model = cast(
            NotificationModel | None,
            await self._session.scalar(
                select(NotificationModel).where(
                    NotificationModel.source_event_id == source_event_id
                )
            ),
        )
        if model is None:
            return None
        return map_notification_model(model)

    async def add(self, notification: Notification) -> None:
        self._session.add(
            NotificationModel(
                source_event_id=notification.source_event_id,
                user_id=notification.user_id,
                wallet_id=notification.wallet_id,
                operation_type=notification.operation_type,
                amount_cent=notification.amount_cent,
                balance_cent=notification.balance_cent,
                message=notification.message,
            )
        )

    async def list_recent(
        self,
        *,
        user_id: uuid.UUID,
        wallet_id: uuid.UUID | None = None,
        limit: int = 50,
    ) -> list[Notification]:
        stmt = select(NotificationModel).where(NotificationModel.user_id == user_id)
        if wallet_id is not None:
            stmt = stmt.where(NotificationModel.wallet_id == wallet_id)

        rows = await self._session.scalars(
            stmt.order_by(NotificationModel.created_at.desc()).limit(limit)
        )
        return [map_notification_model(item) for item in rows.all()]
