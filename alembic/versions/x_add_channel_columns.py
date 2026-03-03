"""Add channel_name and channel_url columns to video_log

Revision ID: x_add_channel_columns
Revises: 821a6e5fbec7
Create Date: 2026-03-03 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'x_add_channel_columns'
down_revision: Union[str, None] = '821a6e5fbec7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add channel_name and channel_url columns."""
    op.add_column('video_log', sa.Column('channel_name', sa.Text(), nullable=True))
    op.add_column('video_log', sa.Column('channel_url', sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove channel_name and channel_url columns."""
    op.drop_column('video_log', 'channel_url')
    op.drop_column('video_log', 'channel_name')
