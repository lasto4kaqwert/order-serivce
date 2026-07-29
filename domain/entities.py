import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum

from domain.exceptions import InvalidOrderQuantityError


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
        self.user_id = self.user_id.strip()
        self.idempotency_key = self.idempotency_key.strip()

        if self.quantity <= 0:
            raise InvalidOrderQuantityError(self.quantity)
        if not self.user_id:
            raise ValueError("user_id must be not blank")
        if not self.idempotency_key:
            raise ValueError("idempotency_key most be not blank")
