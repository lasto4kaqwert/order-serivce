import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override

from application.exceptions.orders import DuplicateIdempotencyKeyError
from application.ports import ApplicationOrderRepository
from domain.entities import Order
from infrastructure.persistence.mappers.order import (
    to_domain,
)
from infrastructure.persistence.models import OrderModel


class OrderRepository(ApplicationOrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def add(self, order: Order) -> None:
        statement = (
            insert(OrderModel)
            .values(
                id=order.id,
                user_id=order.user_id,
                quantity=order.quantity,
                item_id=order.item_id,
                idempotency_key=order.idempotency_key,
                status=order.status,
                created_at=order.created_at,
                update_at=order.update_at,
            )
            .on_conflict_do_nothing(
                constraint="uq_order_idempotency_key",
            )
            .returning(OrderModel.id)
        )

        inseted_id = await self._session.scalar(statement)

        if inseted_id is None:
            raise DuplicateIdempotencyKeyError(
                order.idempotency_key,
            )

    @override
    async def get(self, order_id: uuid.UUID) -> Order | None:
        model = await self._session.scalar(
            select(OrderModel).where(
                OrderModel.id == order_id
            )
        )
        return to_domain(model) if model is not None else None
