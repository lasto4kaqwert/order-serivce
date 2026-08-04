import uuid

from fastapi import APIRouter, Depends, Response, status

from application.dto.order import CreateOrderCommand
from application.dto.payment import PaymentCallbackCommand
from application.ports.usecases.handle_payment_callback import (
    ABCHandlePaymentCallbackUseCase,
)
from application.usecases import CreateOrderUseCase, GetOrderUseCase
from presentation.api.dependencies import (
    build_create_order_usecase as _create_order,
)
from presentation.api.dependencies import (
    build_get_order_usecase as _get_order,
)
from presentation.api.dependencies import (
    build_handle_payment_callback_usecase as _handle_payment_callback,
)
from presentation.api.schemas import CreateOrderSchema, OrderResponse
from presentation.api.schemas.payment import (
    PaymentCallbackRequest,
)

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_order(
    payload: CreateOrderSchema,
    usecase: CreateOrderUseCase = Depends(_create_order),
) -> OrderResponse:
    order = await usecase.execute(
        CreateOrderCommand(
            user_id=payload.user_id,
            quantity=payload.quantity,
            item_id=payload.item_id,
            idempotency_key=payload.idempotency_key,
        )
    )

    return OrderResponse.model_validate(order, from_attributes=True)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    usecase: GetOrderUseCase = Depends(_get_order),
) -> OrderResponse:
    order = await usecase.execute(order_id)

    return OrderResponse.model_validate(order, from_attributes=True)


@router.post(
    "/payment-callback",
    status_code=status.HTTP_200_OK,
    response_class=Response,
)
async def handle_payment_callback(
    payload: PaymentCallbackRequest,
    usecase: ABCHandlePaymentCallbackUseCase = Depends(
        _handle_payment_callback
    ),
) -> Response:
    await usecase.execute(
        PaymentCallbackCommand(
            payment_id=payload.payment_id,
            order_id=payload.order_id,
            status=payload.status,
            amount=payload.amount,
            error_message=payload.error_message,
        )
    )

    return Response(status_code=status.HTTP_200_OK)
