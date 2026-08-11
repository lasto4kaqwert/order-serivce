import asyncio
import logging

from aiokafka import AIOKafkaProducer

from application.usecases.publish_outbox import PublishOutboxUseCase
from infrastructure.kafka.outbox_worker import OutboxWorker
from infrastructure.kafka.producer import KafkaEventPublisher
from infrastructure.persistence.database import (
    async_session_factory,
    engine,
)
from infrastructure.persistence.uow.order import OrderUnitOfWork
from settings import Settings


async def main() -> None:
    settings = Settings()

    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        enable_idempotence=True,
    )

    publisher = KafkaEventPublisher(producer)

    usecase = PublishOutboxUseCase(
        uow=OrderUnitOfWork(async_session_factory),
        publisher=publisher,
    )

    worker = OutboxWorker(usecase)

    await producer.start()

    try:
        await worker.run()
    finally:
        await producer.stop()
        await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
