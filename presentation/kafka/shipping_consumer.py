import asyncio
import logging

from aiokafka import AIOKafkaConsumer, TopicPartition
from aiokafka.errors import CommitFailedError
from pydantic import ValidationError

from application.dto.shipping import (
    HandleShippingEventCommand,
)
from application.exceptions.orders import OrderNotFoundError
from application.exceptions.shipping import ShippingEventError
from application.ports.usecases.handle_shipping_event import (
    ABCHandleShippingEventUseCase,
)
from domain.exceptions import InvalidOrderStatusTransitionError
from presentation.kafka.schemas.shipping import (
    shipping_event_adapter,
)

logger = logging.getLogger(__name__)


class ShippingKafkaConsumer:
    def __init__(
        self,
        consumer: AIOKafkaConsumer,
        usecase: ABCHandleShippingEventUseCase,
    ) -> None:
        self._consumer = consumer
        self._usecase = usecase

    async def run(self) -> None:
        await self._consumer.start()

        try:
            async for message in self._consumer:
                await self._process(message)
        finally:
            await self._consumer.stop()

    async def _process(self, message) -> None:
        topic_partition = TopicPartition(
            message.topic,
            message.partition,
        )

        try:
            event = shipping_event_adapter.validate_json(
                message.value
            )

            payload = event.model_dump(mode="json")

            await self._usecase.execute(
                HandleShippingEventCommand(
                    topic=message.topic,
                    partition=message.partition,
                    offset=message.offset,
                    event_type=event.event_type,
                    order_id=event.order_id,
                    item_id=event.item_id,
                    quantity=event.quantity,
                    payload=payload,
                )
            )
        except ValidationError:
            logger.exception(
                "Invalid Shipping event at %s:%s:%s",
                message.topic,
                message.partition,
                message.offset,
            )
        except asyncio.CancelledError:
            raise
        except (
            OrderNotFoundError,
            ShippingEventError,
            InvalidOrderStatusTransitionError,
        ):
            logging.exception(
                "Failed to process Shipping event"
            )

        try:
            await self._consumer.commit({
                topic_partition: message.offset + 1,
            })
        except asyncio.CancelledError:
            raise
        except CommitFailedError:
            logger.exception(
                "Kafka rebalance prevented offset commit %s:%s:%s",
                message.topic,
                message.partition,
                message.offset,
            )
        except Exception:
            logger.exception(
                "Failed to commit Kafka offset %s:%s:%s",
                message.topic,
                message.partition,
                message.offset,
            )
            raise
