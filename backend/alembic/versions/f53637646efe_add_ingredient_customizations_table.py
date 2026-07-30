"""add ingredient customizations table

Revision ID: f53637646efe
Revises: fe8609b4be38
Create Date: 2026-07-28 23:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f53637646efe'
down_revision: Union[str, Sequence[str], None] = 'fe8609b4be38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'ingredient_customizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('saved_recipe_id', sa.Integer(), nullable=False),
        sa.Column('ingredient_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.Enum('MODIFY', 'REMOVE', 'ADD', name='customization_action'), nullable=False),
        sa.Column('quantity', sa.String(length=50), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ),
        sa.ForeignKeyConstraint(['saved_recipe_id'], ['saved_recipes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'saved_recipe_id', 'ingredient_id', name='uq_ingredient_customizations_saved_recipe_ingredient'
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('ingredient_customizations')
    sa.Enum(name='customization_action').drop(op.get_bind(), checkfirst=True)
