from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities import Order


class ApplicationOrderRepository(ABC):
    @abstractmethod
    async def add(self, order: Order) -> Order:
        raise NotImplementedError

    @abstractmethod
    async def get(self, order_id: UUID) -> Order | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, order: Order) -> Order:
        raise NotImplementedError

    @abstractmethod
    async def get_for_update(self, order: UUID) -> Order | None:
        raise NotImplementedError
