from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from application.exceptions.catalog import (
    CatalogItemNotFoundError,
    CatalogUnavailableError,
    InvalidCatalogResponseError,
)
from application.exceptions.orders import (
    DuplicateIdempotencyKeyError,
    InsufficientStockError,
    OrderNotFoundError,
)
from application.exceptions.payment import (
    PaymentCallbackConflictError,
)


def register_exception_handlers(app: FastAPI) -> None:
    # 4xx

    @app.exception_handler(CatalogItemNotFoundError)
    async def handle_catalog_item_not_found(
        _: Request,
        error: CatalogItemNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(error)}
        )

    @app.exception_handler(InsufficientStockError)
    async def handle_insufficient_stock(
        _: Request,
        error: InsufficientStockError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(error)}
        )

    @app.exception_handler(OrderNotFoundError)
    async def handle_order_not_found(
        _: Request,
        error: OrderNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(error)}
        )

    @app.exception_handler(DuplicateIdempotencyKeyError)
    async def handle_duplicate_idempotency_key(
        _: Request,
        error: DuplicateIdempotencyKeyError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(error)}
        )

    # 5xx

    @app.exception_handler(InvalidCatalogResponseError)
    async def handle_invalid_catalog_response(
        _: Request,
        error: InvalidCatalogResponseError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": str(error)}
        )

    @app.exception_handler(CatalogUnavailableError)
    async def handle_catalog_unavailable(
        _: Request,
        error: CatalogUnavailableError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": str(error)}
        )

    @app.exception_handler(PaymentCallbackConflictError)
    async def handle_payment_callback_conflict(
        _: Request,
        error: PaymentCallbackConflictError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(error)},
        )
