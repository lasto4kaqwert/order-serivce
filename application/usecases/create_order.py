from typing_extensions import override

from application.dto.order import CreateOrderCommand
from application.exceptions.orders import (
    InsufficientStockError,
)
from application.ports import (
    ApplicationCatalogClient as CatalogClient,
)
from application.ports import (
    ApplicationCreateOrderUseCase as CreateOrderUseCase,
)
from application.ports import (
    ApplicationOrderUnitOfWork as OrderUnitOfWork,
)
from domain.entities import Order


class CreateOrderUseCase(CreateOrderUseCase):
    def __init__(
        self,
        uow: OrderUnitOfWork,
        client: CatalogClient,
    ) -> None:
        self._uow = uow
        self._client = client

    @override
    async def execute(
        self,
        command: CreateOrderCommand,
    ) -> Order:
        item = await self._client.get_item(command.item_id)

        if item.available_qty < command.quantity:
            raise InsufficientStockError(
                item_id=command.item_id,
                requested=command.quantity,
                available=item.available_qty,
            )

        order = Order(
            user_id=command.user_id,
            quantity=command.quantity,
            item_id=command.item_id,
            idempotency_key=command.idempotency_key,
        )

        async with self._uow:
            await self._uow.orders.add(order)
            await self._uow.commit()

        return order
