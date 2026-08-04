from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from application.ports.repositories.inbox_repository import (
    ABCInboxRepository,
)
from application.ports.repositories.order_repository import (
    ApplicationOrderRepository,
)
from application.ports.repositories.outbox_repository import (
    ABCOutboxRepository,
)
from application.ports.repositories.payment_callback_repository import (
    ABCPaymentCallbackRepository,
)


class ApplicationOrderUnitOfWork(ABC):
    orders: ApplicationOrderRepository
    payment_callbacks: ABCPaymentCallbackRepository
    outbox: ABCOutboxRepository
    inbox: ABCInboxRepository

    @abstractmethod
    async def __aenter__(self) -> Self:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
