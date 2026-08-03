import uuid
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateOrderCommand:
    user_id: uuid.UUID
    quantity: int
    item_id: uuid.UUID
    idempotency_key: str
