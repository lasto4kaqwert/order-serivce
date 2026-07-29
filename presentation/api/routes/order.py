import uuid

from fastapi import APIRouter, Depends, status

from application.dto.order import CreateOrderCommand
from application.usecases import CreateOrderUseCase, GetOrderUseCase
from presentation.api.dependencies import (
    build_create_order_usecase as _create_order,
)
from presentation.api.dependencies import (
    build_get_order_usecase as _get_order,
)
from presentation.api.schemas import CreateOrderSchema, OrderResponse

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
