import uuid

from decimal import Decimal
from pydantic import AwareDatetime, BaseModel


class CatalogServiceResponseModel(BaseModel):
    id: uuid.UUID
    name: str
    price: Decimal
    available_qty: int
    created_at: AwareDatetime
