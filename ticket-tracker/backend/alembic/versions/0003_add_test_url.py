"""add test_url to tickets

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, Sequence[str], None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('tickets', sa.Column('test_url', sa.String(length=1000), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('tickets', 'test_url')
