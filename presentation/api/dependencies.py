import httpx
from fastapi import Depends, Request

from application.ports.clients.catalog_client import (
    ApplicationCatalogClient,
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
from application.usecases.create_order import CreateOrderUseCase
from application.usecases.get_order import GetOrderUseCase
from infrastructure.http.clients.catalog import HttpCatalogClient
from infrastructure.persistence.database import async_session_factory
from infrastructure.persistence.uow.order import OrderUnitOfWork
from settings import Settings

settings = Settings()


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def build_catalog_client(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> ApplicationCatalogClient:
    return HttpCatalogClient(
        client=client,
        base_url=str(settings.catalog_base_url),
        api_key=settings.api_token.get_secret_value(),
    )


def build_order_uow() -> ApplicationOrderUnitOfWork:
    return OrderUnitOfWork(async_session_factory)


def build_create_order_usecase(
    uow: ApplicationOrderUnitOfWork = Depends(build_order_uow),
    catalog_client: ApplicationCatalogClient = Depends(
        build_catalog_client
    ),
) -> ApplicationCreateOrderUseCase:
    return CreateOrderUseCase(
        uow=uow,
        client=catalog_client,
    )


def build_get_order_usecase(
    uow: ApplicationOrderUnitOfWork = Depends(build_order_uow),
) -> ApplicationGetOrderUseCase:
    return GetOrderUseCase(uow=uow)
