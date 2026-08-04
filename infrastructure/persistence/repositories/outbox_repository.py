from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override

from application.dto.outbox import OutboxEvent
from application.ports.repositories.outbox_repository import (
    ABCOutboxRepository,
)
from infrastructure.persistence.mappers.outbox import (
    to_dto,
)
from infrastructure.persistence.models.outbox import (
    OutboxEventModel,
)


class OutboxRepository(ABCOutboxRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def add(self, event: OutboxEvent) -> bool:
        statement = (
            insert(OutboxEventModel)
            .values(
                id=event.id,
                topic=event.topic,
                event_type=event.event_type,
                aggregate_id=event.aggregate_id,
                deduplication_key=event.deduplication_key,
                payload=event.payload,
                created_at=event.created_at,
                published_at=event.published_at,
                attempts=event.attempts,
                last_error=event.last_error,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    OutboxEventModel.deduplication_key
                ]
            )
            .returning(OutboxEventModel.id)
        )

        inserted_id = await self._session.scalar(statement)

        return inserted_id is not None

    @override
    async def get_pending(self, limit: int) -> list[OutboxEvent]:
        statement = (
            select(OutboxEventModel)
            .where(
                OutboxEventModel.published_at.is_(None)
            )
            .order_by(OutboxEventModel.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        models = await self._session.scalars(statement)

        return [to_dto(model) for model in models.all()]

    @override
    async def mark_published(self, event_id: UUID) -> None:
        statement = (
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event_id)
            .values(
                published_at=datetime.now(timezone.utc),
                last_error=None,
            )
        )

        await self._session.execute(statement)

    @override
    async def mark_failed(
        self,
        event_id: UUID,
        error_message: str,
    ) -> None:
        statement = (
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event_id)
            .values(
                attempts=OutboxEventModel.attempts + 1,
                last_error=error_message,
            )
        )

        await self._session.execute(statement)
