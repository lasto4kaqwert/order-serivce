"""payment callback

Revision ID: a62c236af0db
Revises: 06582d5516ab
Create Date: 2026-08-04 20:35:54.547761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a62c236af0db'
down_revision: Union[str, Sequence[str], None] = '06582d5516ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "order_user_id_is_not_blank",
        "orders",
        type_="check",
    )

    op.alter_column(
        "orders",
        "user_id",
        existing_type=sa.String(length=255),
        type_=sa.UUID(),
        existing_nullable=False,
        postgresql_using="user_id::uuid",
    )

    op.create_table(
        "payment_callback",
        sa.Column(
            "payment_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "order_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
        ),
        sa.Column(
            "amount",
            sa.Numeric(precision=18, scale=2),
            nullable=False,
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "processed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('succeeded', 'failed')",
            name="payment_callback_status_is_valid",
        ),
        sa.CheckConstraint(
            "amount > 0",
            name="payment_callback_amount_is_positive",
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            name="fk_payment_callback_order_id_orders",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "payment_id",
            name="pk_payment_callback",
        ),
        sa.UniqueConstraint(
            "order_id",
            name="uq_payment_callback_order_id",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("payment_callback")
    
    op.alter_column(
        "orders",
        "user_id",
        existing_type=sa.UUID(),
        type_=sa.String(length=255),
        existing_nullable=False,
        postgresql_using="user_id::text",
    )

    op.create_check_constraint(
        "order_user_id_is_not_blank",
        "orders",
        "length(trim(user_id)) > 0",
    )
