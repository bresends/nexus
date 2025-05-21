"""change purpose fields in projects

Revision ID: 8c2d32238ae9
Revises: 1c4fad790925
Create Date: 2025-05-20 14:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c2d32238ae9'
down_revision = '1c4fad790925'
branch_labels = None
depends_on = None


def upgrade():
    # This migration fixes the typo in the 'purpose' field that was referred to as 'purpuse' in templates
    op.alter_column('projects', 'purpuse', new_column_name='purpose')


def downgrade():
    # Revert the column name change back to the original with typo
    op.alter_column('projects', 'purpose', new_column_name='purpuse')
