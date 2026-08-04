import json
from uuid import UUID

from aiokafka import AIOKafkaProducer
from typing_extensions import override

from application.ports.message_broker import (
    ABCEventPublisher,
)


class KafkaEventPublisher(ABCEventPublisher):
    def __init__(self, producer: AIOKafkaProducer) -> None:
        self._producer = producer

    @override
    async def publish(
        self,
        topic: str,
        key: str,
        payload: dict[str, object],
        event_id: UUID,
    ) -> None:
        await self._producer.send_and_wait(
            topic,
            key=key.encode("utf-8"),
            value=json.dumps(payload).encode("utf-8"),
            headers=[
                ("event_id", str(event_id).encode("utf-8")),
            ],
        )
