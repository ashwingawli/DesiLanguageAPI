"""Create user_translations table manually

Revision ID: bf34ec36fc1c
Revises: b7e51e2ea33a
Create Date: 2025-08-05 16:55:37.044361

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf34ec36fc1c'
down_revision = 'b7e51e2ea33a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('user_translations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('from_text', sa.Text(), nullable=False),
    sa.Column('to_text', sa.Text(), nullable=False),
    sa.Column('to_text_transliteration', sa.Text(), nullable=True),
    sa.Column('from_language', sa.String(), nullable=False),
    sa.Column('to_language', sa.String(), nullable=False),
    sa.Column('from_language_name', sa.String(), nullable=False),
    sa.Column('to_language_name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_translations_id'), 'user_translations', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_translations_id'), table_name='user_translations')
    op.drop_table('user_translations')