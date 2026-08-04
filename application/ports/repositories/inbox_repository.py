from abc import ABC, abstractmethod

from application.dto.inbox import InboxMessage


class ABCInboxRepository(ABC):
    @abstractmethod
    async def add(self, message: InboxMessage) -> bool:
        raise NotImplementedError
