from typing_extensions import override

from application.ports.message_broker import ABCEventPublisher
from application.ports.uow.order_uow import (
    ApplicationOrderUnitOfWork,
)
from application.ports.usecases.publish_outbox import (
    ABCPublishOutboxUseCase,
)


class PublishOutboxUseCase(ABCPublishOutboxUseCase):
    def __init__(
        self,
        uow: ApplicationOrderUnitOfWork,
        publisher: ABCEventPublisher,
    ) -> None:
        self._uow = uow
        self._publisher = publisher

    @override
    async def execute(self) -> int:
        published_count = 0

        async with self._uow:
            events = await self._uow.outbox.get_pending(limit=100)

            for event in events:
                try:
                    await self._publisher.publish(
                        topic=event.topic,
                        key=str(event.aggregate_id),
                        payload=event.payload,
                        event_id=event.id,
                    )
                except Exception as error:
                    await self._uow.outbox.mark_failed(
                        event.id,
                        str(error),
                    )
                else:
                    await self._uow.outbox.mark_published(
                        event.id
                    )
                    published_count += 1

            await self._uow.commit()

        return published_count
