from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.persistence.models.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class InboxMessageModel(Base):
    __tablename__ = "inbox_messages"

    __table_args__ = (
        UniqueConstraint(
            "topic",
            "partition",
            "offset",
            name="uq_inbox_topic_partition_offset",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )

    topic: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    partition: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    offset: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        server_default=func.now(),
    )
