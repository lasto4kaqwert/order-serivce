import uuid
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class CatalogItem:
    id: uuid.UUID
    name: str
    price: Decimal
    available_qty: int
