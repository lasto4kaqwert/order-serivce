import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override

from application.dto.payment import ProcessedPaymentCallback
from application.ports.repositories.payment_callback_repository import (
    ABCPaymentCallbackRepository,
)
from infrastructure.persistence.mappers.payment_callback import (
    to_dto,
)
from infrastructure.persistence.models.payment_callback import (
    PaymentCallbackModel,
)


class PaymentCallbackRepository(ABCPaymentCallbackRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def get(
        self,
        payment_id: uuid.UUID,
    ) -> ProcessedPaymentCallback | None:
        model = await self._session.scalar(
            select(PaymentCallbackModel).where(
                PaymentCallbackModel.payment_id == payment_id
            )
        )

        return to_dto(model) if model is not None else None

    @override
    async def get_by_order_id(
        self,
        order_id: uuid.UUID,
    ) -> ProcessedPaymentCallback | None:
        model = await self._session.scalar(
            select(PaymentCallbackModel).where(
                PaymentCallbackModel.order_id == order_id
            )
        )

        return to_dto(model) if model is not None else None

    @override
    async def add(
        self,
        callback: ProcessedPaymentCallback,
    ) -> bool:
        statement = (
            insert(PaymentCallbackModel)
            .values(
                payment_id=callback.payment_id,
                order_id=callback.order_id,
                status=callback.status.value,
                amount=callback.amount,
                error_message=callback.error_message,
                processed_at=callback.processed_at,
            )
            .on_conflict_do_nothing()
            .returning(PaymentCallbackModel.payment_id)
        )

        inserted_id = await self._session.scalar(statement)

        return inserted_id is not None
