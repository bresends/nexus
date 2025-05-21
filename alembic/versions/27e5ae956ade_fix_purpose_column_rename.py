"""fix_purpose_column_rename

Revision ID: 27e5ae956ade
Revises: 8c2d32238ae9
Create Date: 2025-05-20 21:04:09.855133

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27e5ae956ade'
down_revision: Union[str, None] = '8c2d32238ae9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - rename purpuse column to purpose."""
    op.alter_column('projects', 'purpuse', new_column_name='purpose')


def downgrade() -> None:
    """Downgrade schema - rename purpose column back to purpuse."""
    op.alter_column('projects', 'purpose', new_column_name='purpuse')
