"""Add indexes for User model performance optimization

Revision ID: user_indexes_perf
Revises: 01cb66b0fa8f
Create Date: 2025-01-12 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'user_indexes_perf'
down_revision = '01cb66b0fa8f'
branch_labels = None
depends_on = None


def upgrade():
    # Add indexes to commonly queried User fields for admin dashboard performance
    
    # Index for created_at (used in ORDER BY for pagination)
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # Index for is_active (used in WHERE clauses for filtering)
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    
    # Index for role (used in WHERE clauses for role filtering)
    op.create_index('idx_users_role', 'users', ['role'])
    
    # Index for last_login (used in WHERE clauses for activity filtering)
    op.create_index('idx_users_last_login', 'users', ['last_login'])
    
    # Composite index for common filter combinations (is_active + role)
    op.create_index('idx_users_active_role', 'users', ['is_active', 'role'])
    
    # Composite index for activity queries (last_login + is_active)
    op.create_index('idx_users_login_active', 'users', ['last_login', 'is_active'])


def downgrade():
    # Remove the indexes
    op.drop_index('idx_users_login_active', 'users')
    op.drop_index('idx_users_active_role', 'users')
    op.drop_index('idx_users_last_login', 'users')
    op.drop_index('idx_users_role', 'users')
    op.drop_index('idx_users_is_active', 'users')
    op.drop_index('idx_users_created_at', 'users')