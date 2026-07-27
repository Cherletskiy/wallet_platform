from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query

from notification_service.application.queries.list_notifications import (
    ListNotificationsInteractor,
)
from notification_service.presentation.api.schemas import (
    HealthResponse,
    NotificationResponse,
)

router = APIRouter(prefix="/api/v1", tags=["Notifications"], route_class=DishkaRoute)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/notifications", response_model=list[NotificationResponse])
async def list_notifications(
    interactor: FromDishka[ListNotificationsInteractor],
    limit: int = Query(default=50, ge=1, le=100),
) -> list[NotificationResponse]:
    notifications = await interactor.execute(limit)
    responses: list[NotificationResponse] = []
    for item in notifications:
        if item.id is None:
            continue
        responses.append(
            NotificationResponse(
                id=item.id,
                source_event_id=item.source_event_id,
                wallet_id=item.wallet_id,
                operation_type=item.operation_type,
                amount_rub=round(item.amount_cent / 100, 2),
                balance_rub=round(item.balance_cent / 100, 2),
                message=item.message,
                created_at=item.created_at,
            )
        )
    return responses
