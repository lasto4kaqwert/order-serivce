from abc import ABC, abstractmethod


class ABCPublishOutboxUseCase(ABC):
    @abstractmethod
    async def execute(self) -> int:
        raise NotImplementedError
