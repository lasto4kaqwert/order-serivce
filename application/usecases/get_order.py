import uuid

from typing_extensions import override

from application.exceptions.orders import OrderNotFoundError
from application.ports import (
    ApplicationGetOrderUseCase,
    ApplicationOrderUnitOfWork,
)
from domain.entities import Order


class GetOrderUseCase(ApplicationGetOrderUseCase):
    def __init__(
        self,
        uow: ApplicationOrderUnitOfWork,
    ) -> None:
        self._uow = uow

    @override
    async def execute(self, order_id: uuid.UUID) -> Order:
        async with self._uow:
            order = await self._uow.orders.get(order_id)

        if order is None:
            raise OrderNotFoundError(order_id)
        return order
