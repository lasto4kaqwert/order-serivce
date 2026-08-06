from typing_extensions import override

from application.dto.order import CreateOrderCommand
from application.dto.payment import CreatePaymentCommand
from application.exceptions.orders import (
    DuplicateIdempotencyKeyError,
    InsufficientStockError,
)
from application.exceptions.payment import (
    PaymentError,
)
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
from application.services.order_notification import (
    OrderNotificationService,
)
from domain.entities import Order


class CreateOrderUseCase(CreateOrderUseCase):
    def __init__(
        self,
        uow: OrderUnitOfWork,
        catalog_client: CatalogClient,
        payment_client: PaymentClient,
        payment_callback_url: str,
        notification_service: OrderNotificationService,
    ) -> None:
        self._uow = uow
        self._catalog_client = catalog_client
        self._payment_client = payment_client
        self._payment_callback_url = payment_callback_url
        self._notification_service = notification_service

    @override
    async def execute(
        self,
        command: CreateOrderCommand,
    ) -> Order:
        item = await self._catalog_client.get_item(command.item_id)

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

        if persisted_order.id != order.id:
            same_request = (
                persisted_order.user_id == command.user_id
                and persisted_order.item_id == command.item_id
                and persisted_order.quantity == command.quantity
            )

            if not same_request:
                raise DuplicateIdempotencyKeyError(
                    command.idempotency_key
                )

            return persisted_order

        await self._notification_service.send(
            persisted_order,
        )

        try:
            await self._payment_client.create_payment(
                CreatePaymentCommand(
                    order_id=persisted_order.id,
                    amount=item.price * persisted_order.quantity,
                    callback_url=self._payment_callback_url,
                    idempotency_key=persisted_order.idempotency_key,
                ),
            )
        except PaymentError as error:
            persisted_order.cancel()

            async with self._uow:
                persisted_order = await self._uow.orders.update(
                    persisted_order
                )
                await self._uow.commit()

            await self._notification_service.send(
                persisted_order,
                reason=str(error),
            )

            raise

        return persisted_order
