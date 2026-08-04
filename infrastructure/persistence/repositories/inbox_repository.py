from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override

from application.dto.inbox import InboxMessage
from application.ports.repositories.inbox_repository import (
    ABCInboxRepository,
)
from infrastructure.persistence.models.inbox import (
    InboxMessageModel,
)


class InboxRepository(ABCInboxRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @override
    async def add(self, message: InboxMessage) -> bool:
        statement = (
            insert(InboxMessageModel)
            .values(
                id=message.id,
                topic=message.topic,
                partition=message.partition,
                offset=message.offset,
                event_type=message.event_type,
                payload=message.payload,
                processed_at=message.processed_at,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    InboxMessageModel.topic,
                    InboxMessageModel.partition,
                    InboxMessageModel.offset,
                ]
            )
            .returning(InboxMessageModel.id)
        )

        inserted_id = await self._session.scalar(statement)

        return inserted_id is not None
