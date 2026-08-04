from dataclasses import dataclass
from typing import ClassVar, Literal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateOrderCommand:
    user_id: str
    quantity: int
    item_id: UUID
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class OrderPaidEvent:
    order_id: UUID
    item_id: UUID
    quantity: int
    idempotency_key: str

    event_type: ClassVar[Literal["order.paid"]] = "order.paid"

    def to_payload(self) -> dict[str, object]:
        return {
            "event_type": self.event_type,
            "order_id": str(self.order_id),
            "item_id": str(self.item_id),
            "quantity": self.quantity,
            "idempotency_key": self.idempotency_key,
        }
