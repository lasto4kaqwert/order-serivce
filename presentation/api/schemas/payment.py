import uuid
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from domain.entities import PaymentStatus


class PaymentCallbackRequest(BaseModel):
    payment_id: uuid.UUID
    order_id: uuid.UUID
    status: Literal[
        PaymentStatus.SUCCEEDED,
        PaymentStatus.FAILED,
    ]
    amount: Decimal = Field(gt=0)
    error_message: str | None

    @model_validator(mode="after")
    def validate_error_message(self):
        if (
            self.status is PaymentStatus.SUCCEEDED
            and self.error_message is not None
        ):
            raise ValueError(
                "Successful payment cannot contain error_message"
            )

        return self
