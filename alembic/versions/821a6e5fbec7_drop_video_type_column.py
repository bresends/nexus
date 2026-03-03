"""Drop video_type column, make video_id unique

Revision ID: 821a6e5fbec7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-03 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '821a6e5fbec7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop video_type column, make video_id unique."""
    op.execute("""
        DELETE FROM video_log
        WHERE id NOT IN (
            SELECT MIN(id) FROM video_log GROUP BY video_id
        )
    """)

    op.drop_constraint('video_log_video_id_video_type_key', 'video_log', type_='unique')

    op.drop_column('video_log', 'video_type')

    op.create_unique_constraint('video_log_video_id_key', 'video_log', ['video_id'])


def downgrade() -> None:
    """Re-add video_type column with composite unique constraint."""
    op.drop_constraint('video_log_video_id_key', 'video_log', type_='unique')

    op.add_column('video_log', sa.Column('video_type', sa.String(20), nullable=True))

    op.execute("UPDATE video_log SET video_type = 'video'")

    op.alter_column('video_log', 'video_type', nullable=False)

    op.create_unique_constraint('video_log_video_id_video_type_key', 'video_log', ['video_id', 'video_type'])
