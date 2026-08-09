import logging
import asyncio

from application.dto.notification import (
    SendNotificationCommand,
)
from application.exceptions.notification import (
    NotificationError,
    NotificationUnavailableError,
)
from application.ports.clients.notification_client import (
    ABCNotificationClient,
)
from domain.entities import Order, OrderStatus

logger = logging.getLogger(__name__)


class OrderNotificationService:
    def __init__(
        self,
        client: ABCNotificationClient,
    ) -> None:
        self._client = client

    async def send(
        self,
        order: Order,
        reason: str | None = None,
    ) -> None:
        message = self._build_message(
            status=order.status,
            reason=reason,
        )

        idempotency_key = (
            f"{order.idempotency_key}:"
            "notification:"
            f"{order.status.value.lower()}"
        )

        notification = SendNotificationCommand(
            message=message,
            reference_id=order.id,
            idempotency_key=idempotency_key,
        )

        attempts = 5

        for attempt in range(attempts):
            try:
                await self._client.send_notification(notification)

                return
            except NotificationUnavailableError:
                if attempt == attempts - 1:
                    logger.exception(
                        "Failed to send %s notification for order %s "
                        "after %s attempts",
                        order.status, order.id, attempts
                    )

                    return
                await asyncio.sleep(0.25 * (2**attempt))
            except NotificationError:
                logging.exception(
                    "Failed to send %s notification for order %s",
                    order.status, order.id,
                )
                
                return

    @staticmethod
    def _build_message(
        status: OrderStatus,
        reason: str | None,
    ) -> str:
        if status is OrderStatus.NEW:
            return (
                "Ваш заказ создан и ожидает оплаты"
            )
        if status is OrderStatus.PAID:
            return (
                "Ваш заказ успешно оплачен и готов к отправке"
            )
        if status is OrderStatus.SHIPPED:
            return (
                "Ваш заказ отправлен в доставку"
            )
        if status is OrderStatus.CANCELLED:
            cancellation_reason = reason or "не указана"

            return (
                "Ваш заказ отменен. "
                f"Причина: {cancellation_reason}"
            )

        raise ValueError(
            f"Unsupported order status: {status}"
        )
