"""add video_log table

Revision ID: 2aa4dcb3f670
Revises: 8a1b2c3d4e5f
Create Date: 2026-02-22 12:29:25.888177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2aa4dcb3f670'
down_revision: Union[str, None] = '8a1b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create video_log table."""
    op.create_table(
        'video_log',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('url', sa.String(500), nullable=False, unique=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('verdict', sa.String(20), nullable=False),
        sa.Column('source', sa.String(20), nullable=False, server_default='pipeline'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('profile_used', sa.String(255), nullable=True),
        sa.Column('resource_id', sa.Integer(), sa.ForeignKey('resources.id'), nullable=True),
        sa.Column('logged_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Drop video_log table."""
    op.drop_table('video_log')
