from abc import ABC, abstractmethod

from application.dto.notification import (
    NotificationItem,
    SendNotificationCommand,
)


class ABCNotificationClient(ABC):
    @abstractmethod
    async def send_notification(
        self,
        notification: SendNotificationCommand,
    ) -> NotificationItem:
        raise NotImplementedError
