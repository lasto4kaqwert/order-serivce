import uuid
from datetime import datetime, timezone

from typing_extensions import override

from application.dto.inbox import InboxMessage
from application.dto.shipping import (
    HandleShippingEventCommand,
)
from application.exceptions.orders import OrderNotFoundError
from application.exceptions.shipping import (
    ShippingEventConflictError,
)
from application.ports.uow.order_uow import (
    ApplicationOrderUnitOfWork,
)
from application.ports.usecases.handle_shipping_event import (
    ABCHandleShippingEventUseCase,
)


class HandleShippingEventUseCase(
    ABCHandleShippingEventUseCase
):
    def __init__(
        self,
        uow: ApplicationOrderUnitOfWork,
    ) -> None:
        self._uow = uow

    @override
    async def execute(
        self,
        command: HandleShippingEventCommand,
    ) -> None:
        async with self._uow:
            inserted = await self._uow.inbox.add(
                InboxMessage(
                    id=uuid.uuid4(),
                    topic=command.topic,
                    partition=command.partition,
                    offset=command.offset,
                    event_type=command.event_type,
                    payload=command.payload,
                    processed_at=datetime.now(timezone.utc),
                )
            )

            if not inserted:
                return

            order = await self._uow.orders.get_for_update(
                command.order_id,
            )

            if order is None:
                raise OrderNotFoundError(command.order_id)

            if order.item_id != command.item_id:
                raise ShippingEventConflictError(
                    order_id=order.id,
                    message=(
                        f"expected item_id={order.item_id}, "
                        f"got {command.item_id}"
                    ),
                )

            if order.quantity != command.quantity:
                raise ShippingEventConflictError(
                    order_id=order.id,
                    message=(
                        f"expected quantity={order.quantity}, "
                        f"got {command.quantity}"
                    ),
                )

            if command.event_type == "order.shipped":
                order.ship()
            elif command.event_type == "order.cancelled":
                order.cancel()
            else:
                raise ShippingEventConflictError(
                    order_id=order.id,
                    message=(
                        f"unexpected event_type="
                        f"{command.event_type!r}"
                    ),
                )

            await self._uow.orders.update(order)
            await self._uow.commit()
