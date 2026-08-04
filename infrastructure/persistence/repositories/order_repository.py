import uuid

from sqlalchemy import (
    select,
)
from sqlalchemy import (
    update as sa_update,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override

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
    async def add(self, order: Order) -> Order:
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

        inserted_id = await self._session.scalar(statement)

        if inserted_id is not None:
            return order

        persisted_order = await self._session.scalar(
            select(OrderModel).where(
                OrderModel.idempotency_key == order.idempotency_key
            )
        )

        if persisted_order is None:
            raise RuntimeError(
                "Failed to retrieve an existing idempotent order"
            )

        return to_domain(persisted_order)

    @override
    async def get(self, order_id: uuid.UUID) -> Order | None:
        model = await self._session.scalar(
            select(OrderModel).where(
                OrderModel.id == order_id
            )
        )
        return to_domain(model) if model is not None else None

    @override
    async def update(self, order: Order) -> Order:
        statement = (
            sa_update(OrderModel)
            .where(OrderModel.id == order.id)
            .values(
                status=order.status,
                update_at=order.update_at,
            )
            .returning(OrderModel)
        )

        model = await self._session.scalar(statement)

        if model is None:
            raise RuntimeError(
                f"Order {order.id} disappeared during update"
            )

        return to_domain(model)

    @override
    async def get_for_update(
        self,
        order_id: uuid.UUID,
    ) -> Order | None:
        statement = (
            select(OrderModel)
            .where(OrderModel.id == order_id)
            .with_for_update()
        )

        model = await self._session.scalar(statement)

        return to_domain(model) if model is not None else None
