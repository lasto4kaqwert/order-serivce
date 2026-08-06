from typing import Annotated
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, StringConstraints

NonBlankString = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
    ),
]


class NotificationCreateRequest(BaseModel):
    message: NonBlankString
    reference_id: UUID
    idempotency_key: NonBlankString


class NotificationCreateResponse(BaseModel):
    id: UUID
    user_id: str
    message: str
    reference_id: UUID
    created_at: AwareDatetime
