import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum

from domain.exceptions import (
    InvalidOrderQuantityError,
    InvalidOrderStatusTransitionError,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class OrderStatus(StrEnum):
    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


@dataclass(slots=True, kw_only=True)
class Order:
    user_id: str
    quantity: int
    item_id: uuid.UUID
    idempotency_key: str

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: OrderStatus = OrderStatus.NEW
    created_at: datetime = field( default_factory=utc_now)
    update_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.idempotency_key = self.idempotency_key.strip()

        if self.quantity <= 0:
            raise InvalidOrderQuantityError(self.quantity)
        if not self.idempotency_key:
            raise ValueError("idempotency_key most be not blank")

    def cancel(self) -> None:
        if self.status is OrderStatus.CANCELLED:
            return
        if self.status is OrderStatus.SHIPPED:
            raise InvalidOrderStatusTransitionError(
                self.status,
                OrderStatus.CANCELLED,
            )

        self.status = OrderStatus.CANCELLED
        self.update_at = utc_now()

    def mark_paid(self) -> None:
        if self.status is OrderStatus.PAID:
            return
        if self.status is not OrderStatus.NEW:
            raise InvalidOrderStatusTransitionError(
                self.status,
                OrderStatus.PAID,
            )

        self.status = OrderStatus.PAID
        self.update_at = utc_now()

class PaymentStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
