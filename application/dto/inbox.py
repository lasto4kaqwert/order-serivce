from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class InboxMessage:
    id: UUID
    topic: str
    partition: int
    offset: int
    event_type: str
    payload: dict[str, object]
    processed_at: datetime
