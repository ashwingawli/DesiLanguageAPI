"""rename_theme_to_difficulty_in_desi_lessons

Revision ID: 7a771b372585
Revises: 9873b3e5c8de
Create Date: 2025-08-03 12:39:29.372852

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a771b372585'
down_revision = '9873b3e5c8de'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename theme column to difficulty in desi_lessons table
    op.alter_column('desi_lessons', 'theme', new_column_name='difficulty')


def downgrade() -> None:
    # Revert difficulty column back to theme in desi_lessons table
    op.alter_column('desi_lessons', 'difficulty', new_column_name='theme')