"""add username to users

Revision ID: fe8609b4be38
Revises: 56203f9991e5
Create Date: 2026-07-28 22:07:15.403372

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe8609b4be38'
down_revision: Union[str, Sequence[str], None] = '56203f9991e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("username", sa.String(length=255), nullable=True))
    op.execute("UPDATE users SET username = split_part(email, '@', 1) WHERE username IS NULL")
    op.alter_column("users", "username", nullable=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_column("users", "username")
