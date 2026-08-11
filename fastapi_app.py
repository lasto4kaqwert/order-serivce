import asyncio
from contextlib import asynccontextmanager

import httpx
from aiokafka import AIOKafkaConsumer
from fastapi import FastAPI

from application.services.order_notification import (
    OrderNotificationService,
)
from application.usecases.handle_shipping_event import (
    HandleShippingEventUseCase,
)
from infrastructure.http.clients.notification import (
    HttpNotificationClient,
)
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

    consumer = AIOKafkaConsumer(
        settings.kafka_shipment_events_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_consumer_group,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(5.0),
        ) as client:
            app.state.http_client = client

            notification_client = HttpNotificationClient(
                client=client,
                base_url=str(settings.notification_base_url),
                api_key=settings.api_token.get_secret_value(),
            )

            notification_service = OrderNotificationService(
                notification_client
            )

            handle_shipping_event = HandleShippingEventUseCase(
                uow=OrderUnitOfWork(async_session_factory),
                notification_service=notification_service,
            )

            shipping_consumer = ShippingKafkaConsumer(
                consumer=consumer,
                usecase=handle_shipping_event,
            )

            consumer_task = asyncio.create_task(
                shipping_consumer.run()
            )

            try:
                yield
            finally:
                consumer_task.cancel()

                await asyncio.gather(
                    consumer_task,
                    return_exceptions=True,
                )
    finally:
        await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(order_router, prefix="/api")

    return app
