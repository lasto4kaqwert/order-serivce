import uuid
from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter


class OrderShippedEvent(BaseModel):
    event_type: Literal["order.shipped"]
    order_id: uuid.UUID
    item_id: uuid.UUID
    quantity: int = Field(gt=0)
    shipment_id: uuid.UUID


class OrderCancelledEvent(BaseModel):
    event_type: Literal["order.cancelled"]
    order_id: uuid.UUID
    item_id: uuid.UUID
    quantity: int = Field(gt=0)
    reason: str


ShippingEvent = Annotated[
    OrderShippedEvent | OrderCancelledEvent,
    Field(discriminator="event_type"),
]

shipping_event_adapter = TypeAdapter(ShippingEvent)
