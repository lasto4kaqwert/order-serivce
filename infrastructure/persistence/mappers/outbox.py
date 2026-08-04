from application.dto.outbox import OutboxEvent
from infrastructure.persistence.models.outbox import (
    OutboxEventModel,
)


def to_dto(model: OutboxEventModel) -> OutboxEvent:
    return OutboxEvent(
        id=model.id,
        topic=model.topic,
        event_type=model.event_type,
        aggregate_id=model.aggregate_id,
        deduplication_key=model.deduplication_key,
        payload=model.payload,
        created_at=model.created_at,
        published_at=model.published_at,
        attempts=model.attempts,
        last_error=model.last_error,
    )
