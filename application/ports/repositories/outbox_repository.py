from abc import ABC, abstractmethod
from uuid import UUID

from application.dto.outbox import OutboxEvent


class ABCOutboxRepository(ABC):
    @abstractmethod
    async def add(self, event: OutboxEvent) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_pending(self, limit: int) -> list[OutboxEvent]:
        raise NotImplementedError

    @abstractmethod
    async def mark_published(self, event_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def mark_failed(
        self,
        event_id: UUID,
        error_message: str,
    ) -> None:
        raise NotImplementedError
