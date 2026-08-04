from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class OutboxEvent:
    id: UUID
    topic: str
    event_type: str
    aggregate_id: UUID
    deduplication_key: str
    payload: dict[str, object]
    created_at: datetime
    published_at: datetime | None = None
    attempts: int = 0
    last_error: str | None = None
