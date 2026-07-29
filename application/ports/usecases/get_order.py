from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities import Order


class ApplicationGetOrderUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        order_id: UUID,
    ) -> Order:
        raise NotImplementedError
