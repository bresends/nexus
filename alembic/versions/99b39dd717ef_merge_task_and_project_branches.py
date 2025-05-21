"""merge_task_and_project_branches

Revision ID: 99b39dd717ef
Revises: 27e5ae956ade, db902881dc40
Create Date: 2025-05-21 16:19:47.302365

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99b39dd717ef'
down_revision: Union[str, None] = ('27e5ae956ade', 'db902881dc40')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
