import uuid
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import (
    AnyHttpUrl,
    AwareDatetime,
    BaseModel,
    Field,
    StringConstraints,
    UrlConstraints,
)

from domain.entities import PaymentStatus

InternalCallbackUrl = Annotated[
    AnyHttpUrl,
    UrlConstraints(
        allowed_schemes=["http"],
        host_required=True,
    ),
]

IdempotencyKey = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
    ),
]


class PaymentCreateRequest(BaseModel):
    order_id: uuid.UUID
    amount: Decimal = Field(gt=0)
    callback_url: InternalCallbackUrl
    idempotency_key: IdempotencyKey


class PaymentCreateResponse(BaseModel):
    id: uuid.UUID
    user_id: str
    order_id: uuid.UUID
    amount: Decimal = Field(gt=0)
    status: Literal[PaymentStatus.PENDING]
    idempotency_key: IdempotencyKey
    created_at: AwareDatetime


class PaymentCallbackRequest(BaseModel):
    payment_id: uuid.UUID
    order_id: uuid.UUID
    status: PaymentStatus
    amount: Decimal = Field(gt=0)
    error_message: str | None
