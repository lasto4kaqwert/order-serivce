import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from domain.entities import PaymentStatus


@dataclass(frozen=True, slots=True)
class PaymentItem:
    id: uuid.UUID
    user_id: uuid.UUID
    order_id: uuid.UUID
    amount: Decimal
    status: PaymentStatus
    idempotency_key: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class CreatePaymentCommand:
    order_id: uuid.UUID
    amount: Decimal
    callback_url: str
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class PaymentCallbackCommand:
    payment_id: uuid.UUID
    order_id: uuid.UUID
    status: PaymentStatus
    amount: Decimal
    error_message: str | None


@dataclass(frozen=True, slots=True)
class ProcessedPaymentCallback:
    payment_id: uuid.UUID
    order_id: uuid.UUID
    status: PaymentStatus
    amount: Decimal
    error_message: str | None
    processed_at: datetime
