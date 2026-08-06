import httpx
from fastapi import Depends, Request

from application.ports.clients import (
    ABCCatalogClient,
    ABCNotificationClient,
    ABCPaymentClient,
)
from application.ports.uow.order_uow import (
    ApplicationOrderUnitOfWork,
)
from application.ports.usecases.create_order import (
    ApplicationCreateOrderUseCase,
)
from application.ports.usecases.get_order import (
    ApplicationGetOrderUseCase,
)
from application.ports.usecases.handle_payment_callback import (
    ABCHandlePaymentCallbackUseCase,
)
from application.services.order_notification import (
    OrderNotificationService,
)
from application.usecases.create_order import CreateOrderUseCase
from application.usecases.get_order import GetOrderUseCase
from application.usecases.handle_payment_callback import HandlePaymentCallbackUseCase
from infrastructure.http.clients.catalog import HttpCatalogClient
from infrastructure.http.clients.notification import (
    HttpNotificationClient,
)
from infrastructure.http.clients.payment import HttpPaymentClient
from infrastructure.persistence.database import async_session_factory
from infrastructure.persistence.uow.order import OrderUnitOfWork
from settings import Settings

settings = Settings()


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def build_catalog_client(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> ABCCatalogClient:
    return HttpCatalogClient(
        client=client,
        base_url=str(settings.catalog_base_url),
        api_key=settings.api_token.get_secret_value(),
    )


def build_payment_client(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> ABCPaymentClient:
    return HttpPaymentClient(
        client=client,
        base_url=str(settings.payment_base_url),
        api_key=settings.api_token.get_secret_value(),
    )


def build_notification_client(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> ABCNotificationClient:
    return HttpNotificationClient(
        client=client,
        base_url=str(settings.notification_base_url),
        api_key=settings.api_token.get_secret_value(),
    )


def build_order_notification_service(
    client: ABCNotificationClient = Depends(
        build_notification_client
    ),
) -> OrderNotificationService:
    return OrderNotificationService(client)


def build_order_uow() -> ApplicationOrderUnitOfWork:
    return OrderUnitOfWork(async_session_factory)


def build_create_order_usecase(
    uow: ApplicationOrderUnitOfWork = Depends(build_order_uow),
    catalog_client: ABCCatalogClient = Depends(
        build_catalog_client
    ),
    payment_client: ABCPaymentClient = Depends(
        build_payment_client
    ),
    notification_service: OrderNotificationService = Depends(
        build_order_notification_service,
    ),
) -> ApplicationCreateOrderUseCase:
    return CreateOrderUseCase(
        uow=uow,
        catalog_client=catalog_client,
        payment_client=payment_client,
        payment_callback_url=str(
            settings.payment_callback_url
        ),
        notification_service=notification_service,
    )


def build_get_order_usecase(
    uow: ApplicationOrderUnitOfWork = Depends(build_order_uow),
) -> ApplicationGetOrderUseCase:
    return GetOrderUseCase(uow=uow)


def build_handle_payment_callback_usecase(
    uow: ApplicationOrderUnitOfWork = Depends(
        build_order_uow
    ),
    notification_service: OrderNotificationService = Depends(
        build_order_notification_service,
    ),
) -> ABCHandlePaymentCallbackUseCase:
    return HandlePaymentCallbackUseCase(
        uow=uow,
        order_events_topic=settings.kafka_order_events_topic,
        notification_service=notification_service,
    )
