"""create outbox and inbox tables

Revision ID: 544b27915d45
Revises: a62c236af0db
Create Date: 2026-08-05 01:29:05.345199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '544b27915d45'
down_revision: Union[str, Sequence[str], None] = 'a62c236af0db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "outbox_events",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "topic",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "event_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "aggregate_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "deduplication_key",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "payload",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "published_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "attempts",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "last_error",
            sa.Text(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_outbox_events",
        ),
        sa.UniqueConstraint(
            "deduplication_key",
            name="uq_outbox_events_deduplication_key",
        ),
    )

    op.create_table(
        "inbox_messages",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "topic",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "partition",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "offset",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "event_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "payload",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "processed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_inbox_messages",
        ),
        sa.UniqueConstraint(
            "topic",
            "partition",
            "offset",
            name="uq_inbox_topic_partition_offset",
        ),
    )


def downgrade() -> None:
    op.drop_table("inbox_messages")
    op.drop_table("outbox_events")
