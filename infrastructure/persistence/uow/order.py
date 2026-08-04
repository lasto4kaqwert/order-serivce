from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing_extensions import override

from application.ports import ApplicationOrderUnitOfWork
from infrastructure.persistence.repositories.order_repository import (
    OrderRepository,
)
from infrastructure.persistence.repositories.payment_callback_repository import (
    PaymentCallbackRepository,
)


class OrderUnitOfWork(ApplicationOrderUnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    @override
    async def __aenter__(self) -> Self:
        self._session = self._session_factory()

        self.orders = OrderRepository(self._session)
        self.payment_callbacks = PaymentCallbackRepository(
            self._session
        )

        return self

    @override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is None:
            return

        try:
            if self._session.in_transaction():
                await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None

    @override
    async def commit(self) -> None:
        if self._session is None:
            raise RuntimeError(
                "Unit of Work is not active"
            )
        await self._session.commit()

    @override
    async def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError(
                "Unit of Work is not active"
            )
        await self._session.rollback()
