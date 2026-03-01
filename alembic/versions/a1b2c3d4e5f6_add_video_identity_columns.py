"""add video_id and video_type columns to video_log

Revision ID: a1b2c3d4e5f6
Revises: 2aa4dcb3f670
Create Date: 2026-03-01 10:47:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '2aa4dcb3f670'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add video_id and video_type columns, drop url column."""
    op.add_column('video_log', sa.Column('video_id', sa.String(50), nullable=True))
    op.add_column('video_log', sa.Column('video_type', sa.String(20), nullable=True))

    op.execute("""
        DELETE FROM video_log
        WHERE url NOT LIKE '%/shorts/%'
          AND url NOT LIKE '%/live/%'
          AND url NOT LIKE '%watch?v=%'
          AND url NOT LIKE '%youtu.be/%'
    """)

    op.execute("""
        UPDATE video_log SET
            video_type = CASE
                WHEN url LIKE '%/shorts/%' THEN 'shorts'
                WHEN url LIKE '%/live/%' THEN 'live'
                ELSE 'video'
            END,
            video_id = CASE
                WHEN url LIKE '%/shorts/%' THEN split_part(split_part(url, '/shorts/', 2), '?', 1)
                WHEN url LIKE '%/live/%' THEN split_part(split_part(url, '/live/', 2), '?', 1)
                WHEN url LIKE '%watch?v=%' THEN split_part(split_part(url, 'v=', 2), '&', 1)
                WHEN url LIKE '%youtu.be/%' THEN split_part(split_part(url, 'youtu.be/', 2), '?', 1)
            END
    """)

    op.execute("""
        DELETE FROM video_log
        WHERE id NOT IN (
            SELECT MIN(id) FROM video_log GROUP BY video_id, video_type
        )
    """)

    op.alter_column('video_log', 'video_id', nullable=False)
    op.alter_column('video_log', 'video_type', nullable=False)

    op.drop_constraint('video_log_url_key', 'video_log', type_='unique')
    op.drop_column('video_log', 'url')

    op.create_unique_constraint('video_log_video_id_video_type_key', 'video_log', ['video_id', 'video_type'])


def downgrade() -> None:
    """Revert to url column."""
    op.drop_constraint('video_log_video_id_video_type_key', 'video_log', type_='unique')
    op.add_column('video_log', sa.Column('url', sa.String(500), nullable=False, unique=True))
    op.execute("""
        UPDATE video_log SET
            url = CASE video_type
                WHEN 'shorts' THEN 'https://www.youtube.com/shorts/' || video_id
                WHEN 'live' THEN 'https://www.youtube.com/live/' || video_id
                ELSE 'https://www.youtube.com/watch?v=' || video_id
            END
    """)
    op.drop_column('video_log', 'video_id')
    op.drop_column('video_log', 'video_type')
