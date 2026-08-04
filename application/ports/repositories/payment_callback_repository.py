import uuid
from abc import ABC, abstractmethod

from application.dto.payment import ProcessedPaymentCallback


class ABCPaymentCallbackRepository(ABC):
    @abstractmethod
    async def get(
        self,
        payment_id: uuid.UUID
    ) -> ProcessedPaymentCallback | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_order_id(
        self,
        order_id: uuid.UUID,
    ) -> ProcessedPaymentCallback | None:
        raise NotImplementedError

    @abstractmethod
    async def add(
        self,
        callback: ProcessedPaymentCallback,
    ) -> bool:
        raise NotImplementedError
