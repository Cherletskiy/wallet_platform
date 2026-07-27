from notification_service.domain.notification import Notification
from notification_service.infrastructure.sa.models import NotificationModel


def map_notification_model(model: NotificationModel) -> Notification:
    return Notification(
        id=model.id,
        source_event_id=model.source_event_id,
        wallet_id=model.wallet_id,
        operation_type=model.operation_type,
        amount_cent=model.amount_cent,
        balance_cent=model.balance_cent,
        message=model.message,
        created_at=model.created_at,
    )
