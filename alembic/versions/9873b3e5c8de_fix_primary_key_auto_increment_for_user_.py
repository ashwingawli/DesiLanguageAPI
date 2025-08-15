"""Fix primary key auto-increment for user tables

Revision ID: 9873b3e5c8de
Revises: 01cb66b0fa8f
Create Date: 2025-07-28 16:16:46.875390

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9873b3e5c8de'
down_revision = '01cb66b0fa8f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add SERIAL properties to primary key columns that are missing them
    # Skip users and user_progress as they already have sequences
    op.execute("CREATE SEQUENCE IF NOT EXISTS user_profiles_id_seq")
    op.execute("ALTER TABLE user_profiles ALTER COLUMN id SET DEFAULT nextval('user_profiles_id_seq')")
    op.execute("ALTER SEQUENCE user_profiles_id_seq OWNED BY user_profiles.id")
    
    op.execute("CREATE SEQUENCE IF NOT EXISTS user_subscriptions_id_seq")
    op.execute("ALTER TABLE user_subscriptions ALTER COLUMN id SET DEFAULT nextval('user_subscriptions_id_seq')")
    op.execute("ALTER SEQUENCE user_subscriptions_id_seq OWNED BY user_subscriptions.id")
    
    op.execute("CREATE SEQUENCE IF NOT EXISTS lesson_completions_id_seq")
    op.execute("ALTER TABLE lesson_completions ALTER COLUMN id SET DEFAULT nextval('lesson_completions_id_seq')")
    op.execute("ALTER SEQUENCE lesson_completions_id_seq OWNED BY lesson_completions.id")
    
    op.execute("CREATE SEQUENCE IF NOT EXISTS quiz_attempts_id_seq")
    op.execute("ALTER TABLE quiz_attempts ALTER COLUMN id SET DEFAULT nextval('quiz_attempts_id_seq')")
    op.execute("ALTER SEQUENCE quiz_attempts_id_seq OWNED BY quiz_attempts.id")
    
    op.execute("CREATE SEQUENCE IF NOT EXISTS achievements_id_seq")
    op.execute("ALTER TABLE achievements ALTER COLUMN id SET DEFAULT nextval('achievements_id_seq')")
    op.execute("ALTER SEQUENCE achievements_id_seq OWNED BY achievements.id")
    
    op.execute("CREATE SEQUENCE IF NOT EXISTS user_achievements_id_seq")
    op.execute("ALTER TABLE user_achievements ALTER COLUMN id SET DEFAULT nextval('user_achievements_id_seq')")
    op.execute("ALTER SEQUENCE user_achievements_id_seq OWNED BY user_achievements.id")
    
    op.execute("CREATE SEQUENCE IF NOT EXISTS user_settings_id_seq")
    op.execute("ALTER TABLE user_settings ALTER COLUMN id SET DEFAULT nextval('user_settings_id_seq')")
    op.execute("ALTER SEQUENCE user_settings_id_seq OWNED BY user_settings.id")
    
    op.execute("CREATE SEQUENCE IF NOT EXISTS study_sessions_id_seq")
    op.execute("ALTER TABLE study_sessions ALTER COLUMN id SET DEFAULT nextval('study_sessions_id_seq')")
    op.execute("ALTER SEQUENCE study_sessions_id_seq OWNED BY study_sessions.id")


def downgrade() -> None:
    # Remove sequences and defaults
    op.execute("ALTER TABLE user_profiles ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS user_profiles_id_seq")
    op.execute("ALTER TABLE user_subscriptions ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS user_subscriptions_id_seq")
    op.execute("ALTER TABLE lesson_completions ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS lesson_completions_id_seq")
    op.execute("ALTER TABLE quiz_attempts ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS quiz_attempts_id_seq")
    op.execute("ALTER TABLE achievements ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS achievements_id_seq")
    op.execute("ALTER TABLE user_achievements ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS user_achievements_id_seq")
    op.execute("ALTER TABLE user_settings ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS user_settings_id_seq")
    op.execute("ALTER TABLE study_sessions ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS study_sessions_id_seq")