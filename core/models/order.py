from decimal import Decimal
from enum import StrEnum
from pydantic import BaseModel


class OrderStatusEnum(StrEnum):
    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


class Item(BaseModel):
    """Value Object - товар"""
    id: str
    name: str
    price: Decimal


class Order(BaseModel):
    """Entity - заказ"""
