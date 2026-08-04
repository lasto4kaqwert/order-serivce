import asyncio
from contextlib import asynccontextmanager

import httpx
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import FastAPI

from application.usecases.handle_shipping_event import (
    HandleShippingEventUseCase,
)
from application.usecases.publish_outbox import (
    PublishOutboxUseCase,
)
from infrastructure.kafka.outbox_worker import OutboxWorker
from infrastructure.kafka.producer import KafkaEventPublisher
from infrastructure.persistence.database import (
    async_session_factory,
    engine,
)
from infrastructure.persistence.uow.order import OrderUnitOfWork
from presentation.api.exception_handlers import (
    register_exception_handlers,
)
from presentation.api.routes.health import (
    router as health_router,
)
from presentation.api.routes.order import (
    router as order_router,
)
from presentation.kafka.shipping_consumer import (
    ShippingKafkaConsumer,
)
from settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()

    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        enable_idempotence=True,
    )

    consumer = AIOKafkaConsumer(
        settings.kafka_shipment_events_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_consumer_group,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )

    await producer.start()

    publisher = KafkaEventPublisher(producer)

    publish_outbox = PublishOutboxUseCase(
        uow=OrderUnitOfWork(async_session_factory),
        publisher=publisher,
    )

    handle_shipping_event = HandleShippingEventUseCase(
        uow=OrderUnitOfWork(async_session_factory),
    )

    outbox_worker = OutboxWorker(publish_outbox)
    shipping_consumer = ShippingKafkaConsumer(
        consumer=consumer,
        usecase=handle_shipping_event,
    )

    outbox_task = asyncio.create_task(
        outbox_worker.run()
    )
    consumer_task = asyncio.create_task(
        shipping_consumer.run()
    )

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(5.0),
        ) as client:
            app.state.http_client = client
            yield
    finally:
        outbox_task.cancel()
        consumer_task.cancel()

        await asyncio.gather(
            outbox_task,
            consumer_task,
            return_exceptions=True,
        )

        await producer.stop()
        await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(order_router, prefix="/api")

    return app
