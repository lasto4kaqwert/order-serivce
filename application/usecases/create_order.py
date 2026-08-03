from typing_extensions import override

from application.dto.order import CreateOrderCommand
from application.dto.payment import CreatePaymentCommand
from application.exceptions.orders import (
    InsufficientStockError,
)
from application.exceptions.payment import PaymentError
from application.ports import (
    ApplicationCreateOrderUseCase as CreateOrderUseCase,
)
from application.ports import (
    ApplicationOrderUnitOfWork as OrderUnitOfWork,
)
from application.ports.clients import (
    ABCCatalogClient as CatalogClient,
)
from application.ports.clients import (
    ABCPaymentClient as PaymentClient,
)
from domain.entities import Order


class CreateOrderUseCase(CreateOrderUseCase):
    def __init__(
        self,
        uow: OrderUnitOfWork,
        order_client: CatalogClient,
        payment_client: PaymentClient,
        payment_callback_url: str,
    ) -> None:
        self._uow = uow
        self._order_client = order_client
        self._payment_client = payment_client
        self._payment_callback_url = payment_callback_url

    @override
    async def execute(
        self,
        command: CreateOrderCommand,
    ) -> Order:
        item = await self._order_client.get_item(command.item_id)

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
            persisted_order = await self._uow.orders.add(order)
            await self._uow.commit()

        try:
            await self._payment_client.create_payment(
                CreatePaymentCommand(
                    order_id=persisted_order.item_id,
                    amount=persisted_order.quantity,
                    callback_url=self._payment_callback_url,
                    idempotency_key=persisted_order.idempotency_key,
                ),
            )
        except PaymentError:
            persisted_order.cancel()

            async with self._uow:
                persisted_order = await self._uow.orders.update(
                    persisted_order
                )
                await self._uow.commit()
            raise

        return persisted_order
