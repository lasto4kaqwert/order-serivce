from abc import ABC, abstractmethod
from uuid import UUID


class ABCEventPublisher(ABC):
    @abstractmethod
    async def publish(
        self,
        topic: str,
        key: str,
        payload: dict[str, object],
        event_id: UUID,
    ) -> None:
        raise NotImplementedError
