"""add_context_field_to_tasks

Revision ID: a4541dbb67a1
Revises: ea95bc30586d
Create Date: 2025-05-21 17:48:59.731111

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a4541dbb67a1"
down_revision: Union[str, None] = "ea95bc30586d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add context column to tasks table
    op.add_column("tasks", sa.Column("context", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove context column from tasks table
    op.drop_column("tasks", "context")
