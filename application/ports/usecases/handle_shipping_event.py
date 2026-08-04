from abc import ABC, abstractmethod

from application.dto.shipping import (
    HandleShippingEventCommand,
)


class ABCHandleShippingEventUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        command: HandleShippingEventCommand,
    ) -> None:
        raise NotImplementedError
