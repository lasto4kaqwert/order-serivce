import uuid
from decimal import Decimal

from pydantic import AwareDatetime, BaseModel, Field


class CatalogItemResponse(BaseModel):
    id: uuid.UUID
    name: str
    price: Decimal
    available_qty: int = Field(ge=0)
    created_at: AwareDatetime
