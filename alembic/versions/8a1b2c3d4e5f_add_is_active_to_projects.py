"""Add is_active to projects

Revision ID: 8a1b2c3d4e5f
Revises: 7be45efa8101
Create Date: 2026-01-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a1b2c3d4e5f'
down_revision: Union[str, None] = '7be45efa8101'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add is_active column (nullable initially for existing rows)
    op.add_column('projects', sa.Column('is_active', sa.Boolean(), nullable=True))

    # Set 2 most recently updated projects as active, rest as inactive
    op.execute("""
        UPDATE projects
        SET is_active = CASE
            WHEN id IN (
                SELECT id FROM projects
                ORDER BY updated_at DESC
                LIMIT 2
            ) THEN TRUE
            ELSE FALSE
        END
    """)

    # Make column non-nullable after setting values
    op.alter_column('projects', 'is_active', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('projects', 'is_active')
