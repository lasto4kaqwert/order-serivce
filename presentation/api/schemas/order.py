import uuid
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field, StringConstraints

from domain.entities import OrderStatus

IdempotencyKey = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
    ),
]


class CreateOrderSchema(BaseModel):
    user_id: str
    quantity: int = Field(gt=0)
    item_id: uuid.UUID
    idempotency_key: IdempotencyKey


class OrderResponse(BaseModel):
    id: uuid.UUID
    user_id: str
    quantity: int
    item_id: uuid.UUID
    status: OrderStatus
    created_at: AwareDatetime
    update_at: AwareDatetime
