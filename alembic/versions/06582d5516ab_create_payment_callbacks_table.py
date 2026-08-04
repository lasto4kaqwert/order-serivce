"""create payment callbacks table

Revision ID: 06582d5516ab
Revises: 3f8059d93009
Create Date: 2026-08-03 06:19:29.403690

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06582d5516ab'
down_revision: Union[str, Sequence[str], None] = '3f8059d93009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
