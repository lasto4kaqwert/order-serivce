import uuid
from decimal import Decimal
from typing import Annotated

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    StringConstraints,
    UrlConstraints,
    field_validator,
)

IdempotencyKey = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
    ),
]

InternalCallbackUrl = Annotated[
    AnyHttpUrl,
    UrlConstraints(
        allowed_schemes=["http"],
        host_required=True,
    ),
]


class PaymentServiceRequestModel(BaseModel):
    order_id: uuid.UUID
    amount: Decimal
    callback_url: InternalCallbackUrl
    idempotency_key: IdempotencyKey

    @field_validator("callback_url")
    @classmethod
    def validate_internal_kubernetes_url(
        cls,
        value: AnyHttpUrl,
    ) -> AnyHttpUrl:
        host_parts = (value.host or "").split(".")

        if len(host_parts) < 3 or host_parts[2] != "svc":
            raise ValueError(
                "callback_url must contain an internal Kubernetes service hostname"
            )

        if value.path != "/api/orders/payment-callback":
            raise ValueError(
                "invalid payments callback path"
            )

        return value


class PaymentServiceResponseModel(BaseModel):
    pass
