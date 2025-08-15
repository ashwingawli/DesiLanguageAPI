#!/usr/bin/env python3
"""
Manual Oracle schema creation script
This creates the DesiLanguage database schema directly
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def create_oracle_schema():
    """Create Oracle schema manually"""
    
    # Set up environment
    wallet_location = "/home/ashwin/projects/oracle_conn/desidb_wallet"
    os.environ["TNS_ADMIN"] = wallet_location
    
    # Connection details
    username = "DESIDBUSER"
    password = "g4RJX2sVhRtGFxw"
    wallet_password = "Adbwallet@2025"
    
    print("Manual Oracle Schema Creation")
    print("=" * 50)
    
    try:
        # Create engine
        engine = create_engine(
            f"oracle+oracledb://{username}:{password}@desidb_high",
            connect_args={
                "config_dir": wallet_location,
                "wallet_location": wallet_location,
                "wallet_password": wallet_password
            }
        )
        
        with engine.connect() as connection:
            print("✓ Connected to Oracle database")
            
            # Create sequences first
            sequences = [
                "desi_lessons_id_seq",
                "desi_vocabulary_id_seq", 
                "desi_example_sentences_id_seq",
                "desi_short_stories_id_seq",
                "desi_dialogue_id_seq",
                "desi_quiz_questions_id_seq",
                "users_id_seq",
                "user_profiles_id_seq",
                "user_subscriptions_id_seq", 
                "user_progress_id_seq",
                "lesson_completions_id_seq",
                "quiz_attempts_id_seq",
                "achievements_id_seq",
                "user_achievements_id_seq",
                "user_settings_id_seq",
                "study_sessions_id_seq",
                "user_translations_id_seq",
                "desi_stories_id_seq",
                "desi_story_vocab_id_seq"
            ]
            
            print("\n--- Creating Sequences ---")
            for seq in sequences:
                try:
                    connection.execute(text(f"CREATE SEQUENCE {seq} START WITH 1 INCREMENT BY 1"))
                    print(f"✓ Created sequence: {seq}")
                except SQLAlchemyError as e:
                    if "already exists" in str(e).lower():
                        print(f"• Sequence already exists: {seq}")
                    else:
                        print(f"✗ Failed to create sequence {seq}: {e}")
            
            # Create main tables
            print("\n--- Creating Tables ---")
            
            # 1. Achievements table (skip if exists)
            try:
                connection.execute(text("""
                    CREATE TABLE achievements (
                    id NUMBER(10) DEFAULT achievements_id_seq.NEXTVAL PRIMARY KEY,
                    name VARCHAR2(100) NOT NULL UNIQUE,
                    title VARCHAR2(200) NOT NULL,
                    description CLOB NOT NULL,
                    icon VARCHAR2(100),
                    category VARCHAR2(50) NOT NULL,
                    criteria CLOB NOT NULL,
                    points_reward NUMBER(10) DEFAULT 0,
                    is_active NUMBER(1) DEFAULT 1,
                    created_at DATE DEFAULT SYSDATE
                )
            """))
            print("✓ Created table: achievements")
            
            # 2. Desi Lessons table  
            connection.execute(text("""
                CREATE TABLE desi_lessons (
                    id NUMBER(10) DEFAULT desi_lessons_id_seq.NEXTVAL PRIMARY KEY,
                    title VARCHAR2(500) NOT NULL,
                    target_language VARCHAR2(100) NOT NULL,
                    difficulty VARCHAR2(50) NOT NULL,
                    lesson_number NUMBER(10) NOT NULL,
                    created_at DATE DEFAULT SYSDATE
                )
            """))
            print("✓ Created table: desi_lessons")
            
            # 3. Users table
            connection.execute(text("""
                CREATE TABLE users (
                    id NUMBER(10) DEFAULT users_id_seq.NEXTVAL PRIMARY KEY,
                    email VARCHAR2(255) NOT NULL UNIQUE,
                    username VARCHAR2(50) NOT NULL UNIQUE,
                    full_name VARCHAR2(200),
                    hashed_password VARCHAR2(255) NOT NULL,
                    is_active NUMBER(1) DEFAULT 1,
                    is_verified NUMBER(1) DEFAULT 0,
                    role VARCHAR2(20) DEFAULT 'USER',
                    created_at DATE DEFAULT SYSDATE,
                    updated_at DATE DEFAULT SYSDATE,
                    last_login DATE
                )
            """))
            print("✓ Created table: users")
            
            # 4. User profiles table
            connection.execute(text("""
                CREATE TABLE user_profiles (
                    id NUMBER(10) DEFAULT user_profiles_id_seq.NEXTVAL PRIMARY KEY,
                    user_id NUMBER(10) UNIQUE REFERENCES users(id),
                    avatar_url VARCHAR2(500),
                    bio CLOB,
                    birth_date DATE,
                    country VARCHAR2(100),
                    timezone VARCHAR2(50) DEFAULT 'UTC',
                    native_language VARCHAR2(100),
                    learning_languages CLOB,
                    primary_learning_language VARCHAR2(100),
                    learning_goal VARCHAR2(100),
                    daily_goal_minutes NUMBER(10) DEFAULT 15,
                    created_at DATE DEFAULT SYSDATE,
                    updated_at DATE DEFAULT SYSDATE
                )
            """))
            print("✓ Created table: user_profiles")
            
            # 5. User subscriptions table
            connection.execute(text("""
                CREATE TABLE user_subscriptions (
                    id NUMBER(10) DEFAULT user_subscriptions_id_seq.NEXTVAL PRIMARY KEY,
                    user_id NUMBER(10) UNIQUE REFERENCES users(id),
                    tier VARCHAR2(20) DEFAULT 'FREE',
                    status VARCHAR2(20) DEFAULT 'active',
                    start_date DATE DEFAULT SYSDATE,
                    end_date DATE,
                    trial_end_date DATE,
                    auto_renew NUMBER(1) DEFAULT 1,
                    stripe_subscription_id VARCHAR2(100),
                    stripe_customer_id VARCHAR2(100),
                    created_at DATE DEFAULT SYSDATE,
                    updated_at DATE DEFAULT SYSDATE
                )
            """))
            print("✓ Created table: user_subscriptions")
            
            # 6. User progress table
            connection.execute(text("""
                CREATE TABLE user_progress (
                    id NUMBER(10) DEFAULT user_progress_id_seq.NEXTVAL PRIMARY KEY,
                    user_id NUMBER(10) REFERENCES users(id) ON DELETE CASCADE,
                    language VARCHAR2(100) NOT NULL,
                    total_lessons_completed NUMBER(10) DEFAULT 0,
                    total_words_learned NUMBER(10) DEFAULT 0,
                    total_quiz_score NUMBER(10,2) DEFAULT 0.0,
                    current_streak NUMBER(10) DEFAULT 0,
                    longest_streak NUMBER(10) DEFAULT 0,
                    total_study_time_minutes NUMBER(10) DEFAULT 0,
                    user_level NUMBER(10) DEFAULT 1,
                    experience_points NUMBER(10) DEFAULT 0,
                    last_activity_date DATE,
                    created_at DATE DEFAULT SYSDATE,
                    updated_at DATE DEFAULT SYSDATE
                )
            """))
            print("✓ Created table: user_progress")
            
            # 7. Lesson completions table
            connection.execute(text("""
                CREATE TABLE lesson_completions (
                    id NUMBER(10) DEFAULT lesson_completions_id_seq.NEXTVAL PRIMARY KEY,
                    user_id NUMBER(10) REFERENCES users(id) ON DELETE CASCADE,
                    lesson_id NUMBER(10) REFERENCES desi_lessons(id) ON DELETE CASCADE,
                    language VARCHAR2(100) NOT NULL,
                    completed_at DATE DEFAULT SYSDATE,
                    time_spent_minutes NUMBER(10) DEFAULT 0,
                    sections_completed CLOB,
                    overall_score NUMBER(10,2)
                )
            """))
            print("✓ Created table: lesson_completions")
            
            # 8. Quiz attempts table
            connection.execute(text("""
                CREATE TABLE quiz_attempts (
                    id NUMBER(10) DEFAULT quiz_attempts_id_seq.NEXTVAL PRIMARY KEY,
                    user_id NUMBER(10) REFERENCES users(id) ON DELETE CASCADE,
                    lesson_id NUMBER(10) REFERENCES desi_lessons(id) ON DELETE CASCADE,
                    quiz_question_id NUMBER(10) REFERENCES desi_quiz_questions(id) ON DELETE CASCADE,
                    user_answer VARCHAR2(500) NOT NULL,
                    is_correct NUMBER(1) NOT NULL,
                    time_taken_seconds NUMBER(10),
                    attempt_date DATE DEFAULT SYSDATE
                )
            """))
            print("✓ Created table: quiz_attempts")
            
            # 9. User achievements table
            connection.execute(text("""
                CREATE TABLE user_achievements (
                    id NUMBER(10) DEFAULT user_achievements_id_seq.NEXTVAL PRIMARY KEY,
                    user_id NUMBER(10) REFERENCES users(id) ON DELETE CASCADE,
                    achievement_id NUMBER(10) REFERENCES achievements(id) ON DELETE CASCADE,
                    earned_at DATE DEFAULT SYSDATE,
                    progress_data CLOB
                )
            """))
            print("✓ Created table: user_achievements")
            
            # 10. User settings table
            connection.execute(text("""
                CREATE TABLE user_settings (
                    id NUMBER(10) DEFAULT user_settings_id_seq.NEXTVAL PRIMARY KEY,
                    user_id NUMBER(10) UNIQUE REFERENCES users(id),
                    email_notifications NUMBER(1) DEFAULT 1,
                    push_notifications NUMBER(1) DEFAULT 1,
                    reminder_notifications NUMBER(1) DEFAULT 1,
                    achievement_notifications NUMBER(1) DEFAULT 1,
                    audio_enabled NUMBER(1) DEFAULT 1,
                    auto_play_audio NUMBER(1) DEFAULT 0,
                    show_transliteration NUMBER(1) DEFAULT 1,
                    show_pronunciation NUMBER(1) DEFAULT 1,
                    difficulty_preference VARCHAR2(20) DEFAULT 'adaptive',
                    profile_public NUMBER(1) DEFAULT 0,
                    show_progress_to_friends NUMBER(1) DEFAULT 1,
                    theme VARCHAR2(10) DEFAULT 'light',
                    language_display_script NUMBER(1) DEFAULT 1,
                    created_at DATE DEFAULT SYSDATE,
                    updated_at DATE DEFAULT SYSDATE
                )
            """))
            print("✓ Created table: user_settings")
            
            # 11. Study sessions table
            connection.execute(text("""
                CREATE TABLE study_sessions (
                    id NUMBER(10) DEFAULT study_sessions_id_seq.NEXTVAL PRIMARY KEY,
                    user_id NUMBER(10) REFERENCES users(id) ON DELETE CASCADE,
                    language VARCHAR2(100) NOT NULL,
                    start_time DATE DEFAULT SYSDATE,
                    end_time DATE,
                    duration_minutes NUMBER(10),
                    lessons_completed NUMBER(10) DEFAULT 0,
                    words_learned NUMBER(10) DEFAULT 0,
                    quiz_score NUMBER(10,2),
                    activities CLOB
                )
            """))
            print("✓ Created table: study_sessions")
            
            # 12. User translations table
            connection.execute(text("""
                CREATE TABLE user_translations (
                    id NUMBER(10) DEFAULT user_translations_id_seq.NEXTVAL PRIMARY KEY,
                    user_id NUMBER(10) REFERENCES users(id) ON DELETE CASCADE,
                    from_text CLOB NOT NULL,
                    to_text CLOB NOT NULL,
                    to_text_transliteration CLOB,
                    from_language VARCHAR2(10) NOT NULL,
                    to_language VARCHAR2(10) NOT NULL,
                    from_language_name VARCHAR2(50) NOT NULL,
                    to_language_name VARCHAR2(50) NOT NULL,
                    created_at DATE DEFAULT SYSDATE
                )
            """))
            print("✓ Created table: user_translations")
            
            # 13. Desi stories table
            connection.execute(text("""
                CREATE TABLE desi_stories (
                    id NUMBER(10) DEFAULT desi_stories_id_seq.NEXTVAL PRIMARY KEY,
                    title VARCHAR2(500),
                    target_language VARCHAR2(100) NOT NULL,
                    cefr_level VARCHAR2(5) NOT NULL,
                    scenario VARCHAR2(500),
                    english_text CLOB NOT NULL,
                    translated_text CLOB NOT NULL,
                    transliteration CLOB,
                    generated_at DATE DEFAULT SYSDATE,
                    user_id NUMBER(10) REFERENCES users(id) ON DELETE SET NULL,
                    is_custom NUMBER(1) DEFAULT 0,
                    generation_prompt CLOB
                )
            """))
            print("✓ Created table: desi_stories")
            
            # 14. Desi story vocabulary table
            connection.execute(text("""
                CREATE TABLE desi_story_vocabulary (
                    id NUMBER(10) DEFAULT desi_story_vocab_id_seq.NEXTVAL PRIMARY KEY,
                    story_id NUMBER(10) REFERENCES desi_stories(id) ON DELETE CASCADE,
                    word VARCHAR2(200) NOT NULL,
                    definition CLOB,
                    transliteration CLOB,
                    order_index NUMBER(10) DEFAULT 0
                )
            """))
            print("✓ Created table: desi_story_vocabulary")
            
            # 15. Desi vocabulary table
            connection.execute(text("""
                CREATE TABLE desi_vocabulary (
                    id NUMBER(10) DEFAULT desi_vocabulary_id_seq.NEXTVAL PRIMARY KEY,
                    lesson_id NUMBER(10) REFERENCES desi_lessons(id) ON DELETE CASCADE,
                    english VARCHAR2(200) NOT NULL,
                    target_language_script VARCHAR2(200) NOT NULL,
                    transliteration VARCHAR2(200) NOT NULL,
                    pronunciation VARCHAR2(200) NOT NULL
                )
            """))
            print("✓ Created table: desi_vocabulary")
            
            # 16. Desi example sentences table
            connection.execute(text("""
                CREATE TABLE desi_example_sentences (
                    id NUMBER(10) DEFAULT desi_example_sentences_id_seq.NEXTVAL PRIMARY KEY,
                    lesson_id NUMBER(10) REFERENCES desi_lessons(id) ON DELETE CASCADE,
                    english CLOB NOT NULL,
                    target_language_script CLOB NOT NULL,
                    transliteration CLOB NOT NULL,
                    pronunciation CLOB NOT NULL
                )
            """))
            print("✓ Created table: desi_example_sentences")
            
            # 17. Desi short stories table
            connection.execute(text("""
                CREATE TABLE desi_short_stories (
                    id NUMBER(10) DEFAULT desi_short_stories_id_seq.NEXTVAL PRIMARY KEY,
                    lesson_id NUMBER(10) REFERENCES desi_lessons(id) ON DELETE CASCADE,
                    title VARCHAR2(500) NOT NULL
                )
            """))
            print("✓ Created table: desi_short_stories")
            
            # 18. Desi dialogue table
            connection.execute(text("""
                CREATE TABLE desi_dialogue (
                    id NUMBER(10) DEFAULT desi_dialogue_id_seq.NEXTVAL PRIMARY KEY,
                    short_story_id NUMBER(10) REFERENCES desi_short_stories(id) ON DELETE CASCADE,
                    speaker VARCHAR2(100) NOT NULL,
                    target_language_script CLOB NOT NULL,
                    transliteration CLOB NOT NULL,
                    english CLOB NOT NULL,
                    order_num NUMBER(10) NOT NULL
                )
            """))
            print("✓ Created table: desi_dialogue")
            
            # 19. Desi quiz questions table
            connection.execute(text("""
                CREATE TABLE desi_quiz_questions (
                    id NUMBER(10) DEFAULT desi_quiz_questions_id_seq.NEXTVAL PRIMARY KEY,
                    lesson_id NUMBER(10) REFERENCES desi_lessons(id) ON DELETE CASCADE,
                    question CLOB NOT NULL,
                    options CLOB NOT NULL,
                    answer VARCHAR2(500) NOT NULL
                )
            """))
            print("✓ Created table: desi_quiz_questions")
            
            # Create Alembic version table
            connection.execute(text("""
                CREATE TABLE alembic_version (
                    version_num VARCHAR2(32) NOT NULL PRIMARY KEY
                )
            """))
            print("✓ Created table: alembic_version")
            
            # Insert current migration version
            connection.execute(text("""
                INSERT INTO alembic_version (version_num) VALUES ('oracle_001')
            """))
            print("✓ Set Alembic version to oracle_001")
            
            # Commit all changes
            connection.commit()
            print("\n✅ Schema creation completed successfully!")
            
            # Verify tables were created
            result = connection.execute(text("SELECT COUNT(*) FROM user_tables"))
            table_count = result.fetchone()[0]
            print(f"✓ Total tables in schema: {table_count}")
            
            # List all tables created
            result = connection.execute(text("SELECT table_name FROM user_tables ORDER BY table_name"))
            tables = [row[0] for row in result.fetchall()]
            print(f"✓ Tables created: {', '.join(tables)}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Schema creation failed: {e}")
        return False

if __name__ == "__main__":
    print("DesiLanguage Manual Oracle Schema Creation\n")
    
    success = create_oracle_schema()
    
    if success:
        print("\n🎉 Database schema created successfully!")
        print("\nYou can now:")
        print("1. Start the application: python run.py")
        print("2. Access the API at: http://localhost:8000")
        print("3. View API docs at: http://localhost:8000/docs")
    else:
        print("\n❌ Schema creation failed. Check the error messages above.")