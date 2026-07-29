from abc import ABC, abstractmethod

from application.dto.order import CreateOrderCommand
from domain.entities import Order


class ApplicationCreateOrderUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        command: CreateOrderCommand,
    ) -> Order:
        raise NotImplementedError
