from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class HandleShippingEventCommand:
    topic: str
    partition: int
    offset: int

    event_type: str
    order_id: UUID
    item_id: UUID
    quantity: int

    payload: dict[str, object]
