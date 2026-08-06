from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SendNotificationCommand:
    message: str
    reference_id: UUID
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class NotificationItem:
    id: UUID
    user_id: str
    message: str
    reference_id: UUID
    created_at: datetime
