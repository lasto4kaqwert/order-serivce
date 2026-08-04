import uuid
from datetime import datetime, timezone

from typing_extensions import override

from application.dto.order import OrderPaidEvent
from application.dto.outbox import OutboxEvent
from application.dto.payment import (
    PaymentCallbackCommand,
    ProcessedPaymentCallback,
)
from application.exceptions.orders import OrderNotFoundError
from application.exceptions.payment import (
    PaymentCallbackConflictError,
)
from application.ports import (
    ABCHandlePaymentCallbackUseCase,
    ApplicationOrderUnitOfWork,
)
from domain.entities import PaymentStatus


class HandlePaymentCallbackUseCase(
    ABCHandlePaymentCallbackUseCase
):
    def __init__(
        self,
        uow: ApplicationOrderUnitOfWork,
        order_events_topic: str,
    ) -> None:
        self._uow = uow
        self._order_events_topic = order_events_topic

    @override
    async def execute(
        self,
        command: PaymentCallbackCommand,
    ) -> None:
        async with self._uow:
            order = await self._uow.orders.get_for_update(
                command.order_id
            )

            if order is None:
                raise OrderNotFoundError(command.order_id)

            existing = await self._uow.payment_callbacks.get(
                command.payment_id
            )

            if existing is not None:
                if self._is_same_callback(existing, command):
                    return

                raise PaymentCallbackConflictError(
                    payment_id=command.payment_id,
                    order_id=command.order_id,
                )

            order_callback = (
                await self._uow.payment_callbacks.get_by_order_id(
                    command.order_id
                )
            )

            if order_callback is not None:
                raise PaymentCallbackConflictError(
                    payment_id=command.payment_id,
                    order_id=command.order_id,
                )

            if command.status is PaymentStatus.SUCCEEDED:
                order.pay()

                paid_event = OrderPaidEvent(
                    order_id=order.id,
                    item_id=order.item_id,
                    quantity=order.quantity,
                    idempotency_key=order.idempotency_key,
                )

                await self._uow.outbox.add(
                    OutboxEvent(
                        id=uuid.uuid4(),
                        topic=self._order_events_topic,
                        event_type=paid_event.event_type,
                        aggregate_id=order.id,
                        deduplication_key=f"order.paid:{order.id}",
                        payload=paid_event.to_payload(),
                        created_at=datetime.now(timezone.utc),
                    )
                )
            elif command.status is PaymentStatus.FAILED:
                order.cancel()
            else:
                raise ValueError(
                    f"Unexpected callback status: "
                    f"{command.status}"
                )

            await self._uow.orders.update(order)

            inserted = await self._uow.payment_callbacks.add(
                ProcessedPaymentCallback(
                    payment_id=command.payment_id,
                    order_id=command.order_id,
                    status=command.status,
                    amount=command.amount,
                    error_message=command.error_message,
                    processed_at=datetime.now(timezone.utc),
                )
            )

            if not inserted:
                raise PaymentCallbackConflictError(
                    payment_id=command.payment_id,
                    order_id=command.order_id,
                )

            await self._uow.commit()

    @staticmethod
    def _is_same_callback(
        existing: ProcessedPaymentCallback,
        command: PaymentCallbackCommand,
    ) -> bool:
        return (
            existing.payment_id == command.payment_id
            and existing.order_id == command.order_id
            and existing.status is command.status
            and existing.amount == command.amount
            and existing.error_message == command.error_message
        )
