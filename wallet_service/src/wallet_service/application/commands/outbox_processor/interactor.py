from wallet_service.application.commands.outbox_processor.dto import (
    OutboxProcessorResult,
)
from wallet_service.application.commands.outbox_processor.publisher import (
    OutboxPublisher,
)
from wallet_service.application.outbox.unit_of_work import OutboxUnitOfWork
from wallet_service.domain.outbox import OutboxStatus
from wallet_service.infrastructure.logging import setup_logger

logger = setup_logger(__name__)


class OutboxProcessorInteractor:
    def __init__(
        self,
        uow: OutboxUnitOfWork,
        publisher: OutboxPublisher,
    ) -> None:
        self._uow = uow
        self._publisher = publisher

    async def execute(self, limit: int = 100) -> OutboxProcessorResult:
        events = await self._uow.outbox.get_waiting(limit=limit)

        published = 0
        retried = 0
        dead_lettered = 0

        for event in events:
            try:
                await self._publisher.publish(event)
                event.mark_published()
            except Exception as exc:
                event.mark_failed(str(exc))
                if event.status == OutboxStatus.FAILED:
                    retried += 1
                if event.status == OutboxStatus.DEAD_LETTER:
                    dead_lettered += 1
            finally:
                await self._uow.outbox.update(event)
                await self._uow.commit()

            if event.status == OutboxStatus.PUBLISHED:
                published += 1

        result = OutboxProcessorResult(
            fetched=len(events),
            published=published,
            retried=retried,
            dead_lettered=dead_lettered,
        )
        if result.has_activity():
            logger.info(
                "Outbox processor iteration finished: "
                "fetched=%s published=%s retried=%s dead_lettered=%s",
                result.fetched,
                result.published,
                result.retried,
                result.dead_lettered,
            )
        return result
