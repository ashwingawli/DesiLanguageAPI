"""Add transliteration to story vocabulary

Revision ID: 84afff48834d
Revises: 62be522a4031
Create Date: 2025-08-04 19:31:28.788333

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84afff48834d'
down_revision = '62be522a4031'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add transliteration column to desi_story_vocabulary table
    op.add_column('desi_story_vocabulary', sa.Column('transliteration', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove transliteration column from desi_story_vocabulary table
    op.drop_column('desi_story_vocabulary', 'transliteration')