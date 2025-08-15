#!/usr/bin/env python3
"""
Create missing Oracle tables
"""

import os
from sqlalchemy import create_engine, text

def create_missing_tables():
    """Create missing Oracle tables"""
    
    # Set up environment
    wallet_location = "/home/ashwin/projects/oracle_conn/desidb_wallet"
    os.environ["TNS_ADMIN"] = wallet_location
    
    # Connection details
    username = "DESIDBUSER"
    password = "g4RJX2sVhRtGFxw"
    wallet_password = "Adbwallet@2025"
    
    print("Creating missing Oracle tables...")
    
    try:
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
            
            # Missing tables to create
            missing_tables = [
                # User progress table
                """CREATE TABLE user_progress (
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
                )""",
                
                # Lesson completions table
                """CREATE TABLE lesson_completions (
                    id NUMBER(10) DEFAULT lesson_completions_id_seq.NEXTVAL PRIMARY KEY,
                    user_id NUMBER(10) REFERENCES users(id) ON DELETE CASCADE,
                    lesson_id NUMBER(10) REFERENCES desi_lessons(id) ON DELETE CASCADE,
                    language VARCHAR2(100) NOT NULL,
                    completed_at DATE DEFAULT SYSDATE,
                    time_spent_minutes NUMBER(10) DEFAULT 0,
                    sections_completed CLOB,
                    overall_score NUMBER(10,2)
                )""",
                
                # Quiz attempts table
                """CREATE TABLE quiz_attempts (
                    id NUMBER(10) DEFAULT quiz_attempts_id_seq.NEXTVAL PRIMARY KEY,
                    user_id NUMBER(10) REFERENCES users(id) ON DELETE CASCADE,
                    lesson_id NUMBER(10) REFERENCES desi_lessons(id) ON DELETE CASCADE,
                    quiz_question_id NUMBER(10) REFERENCES desi_quiz_questions(id) ON DELETE CASCADE,
                    user_answer VARCHAR2(500) NOT NULL,
                    is_correct NUMBER(1) NOT NULL,
                    time_taken_seconds NUMBER(10),
                    attempt_date DATE DEFAULT SYSDATE
                )""",
                
                # User achievements table
                """CREATE TABLE user_achievements (
                    id NUMBER(10) DEFAULT user_achievements_id_seq.NEXTVAL PRIMARY KEY,
                    user_id NUMBER(10) REFERENCES users(id) ON DELETE CASCADE,
                    achievement_id NUMBER(10) REFERENCES achievements(id) ON DELETE CASCADE,
                    earned_at DATE DEFAULT SYSDATE,
                    progress_data CLOB
                )""",
                
                # User settings table
                """CREATE TABLE user_settings (
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
                )""",
                
                # Study sessions table
                """CREATE TABLE study_sessions (
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
                )""",
                
                # User translations table
                """CREATE TABLE user_translations (
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
                )""",
                
                # Desi stories table
                """CREATE TABLE desi_stories (
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
                )""",
                
                # Desi story vocabulary table
                """CREATE TABLE desi_story_vocabulary (
                    id NUMBER(10) DEFAULT desi_story_vocab_id_seq.NEXTVAL PRIMARY KEY,
                    story_id NUMBER(10) REFERENCES desi_stories(id) ON DELETE CASCADE,
                    word VARCHAR2(200) NOT NULL,
                    definition CLOB,
                    transliteration CLOB,
                    order_index NUMBER(10) DEFAULT 0
                )""",
                
                # Desi vocabulary table
                """CREATE TABLE desi_vocabulary (
                    id NUMBER(10) DEFAULT desi_vocabulary_id_seq.NEXTVAL PRIMARY KEY,
                    lesson_id NUMBER(10) REFERENCES desi_lessons(id) ON DELETE CASCADE,
                    english VARCHAR2(200) NOT NULL,
                    target_language_script VARCHAR2(200) NOT NULL,
                    transliteration VARCHAR2(200) NOT NULL,
                    pronunciation VARCHAR2(200) NOT NULL
                )""",
                
                # Desi example sentences table
                """CREATE TABLE desi_example_sentences (
                    id NUMBER(10) DEFAULT desi_example_sentences_id_seq.NEXTVAL PRIMARY KEY,
                    lesson_id NUMBER(10) REFERENCES desi_lessons(id) ON DELETE CASCADE,
                    english CLOB NOT NULL,
                    target_language_script CLOB NOT NULL,
                    transliteration CLOB NOT NULL,
                    pronunciation CLOB NOT NULL
                )""",
                
                # Desi short stories table
                """CREATE TABLE desi_short_stories (
                    id NUMBER(10) DEFAULT desi_short_stories_id_seq.NEXTVAL PRIMARY KEY,
                    lesson_id NUMBER(10) REFERENCES desi_lessons(id) ON DELETE CASCADE,
                    title VARCHAR2(500) NOT NULL
                )""",
                
                # Desi dialogue table
                """CREATE TABLE desi_dialogue (
                    id NUMBER(10) DEFAULT desi_dialogue_id_seq.NEXTVAL PRIMARY KEY,
                    short_story_id NUMBER(10) REFERENCES desi_short_stories(id) ON DELETE CASCADE,
                    speaker VARCHAR2(100) NOT NULL,
                    target_language_script CLOB NOT NULL,
                    transliteration CLOB NOT NULL,
                    english CLOB NOT NULL,
                    order_num NUMBER(10) NOT NULL
                )""",
                
                # Desi quiz questions table
                """CREATE TABLE desi_quiz_questions (
                    id NUMBER(10) DEFAULT desi_quiz_questions_id_seq.NEXTVAL PRIMARY KEY,
                    lesson_id NUMBER(10) REFERENCES desi_lessons(id) ON DELETE CASCADE,
                    question CLOB NOT NULL,
                    options CLOB NOT NULL,
                    answer VARCHAR2(500) NOT NULL
                )"""
            ]
            
            table_names = [
                "user_progress", "lesson_completions", "quiz_attempts", "user_achievements",
                "user_settings", "study_sessions", "user_translations", "desi_stories", 
                "desi_story_vocabulary", "desi_vocabulary", "desi_example_sentences",
                "desi_short_stories", "desi_dialogue", "desi_quiz_questions"
            ]
            
            for i, table_sql in enumerate(missing_tables):
                table_name = table_names[i]
                try:
                    connection.execute(text(table_sql))
                    print(f"✓ Created table: {table_name}")
                except Exception as e:
                    if "already exists" in str(e).lower() or "name is already used" in str(e).lower():
                        print(f"• Table already exists: {table_name}")
                    else:
                        print(f"✗ Failed to create table {table_name}: {e}")
            
            # Commit all changes
            connection.commit()
            print("\n✅ Missing tables creation completed!")
            
            # Verify tables were created
            result = connection.execute(text("SELECT COUNT(*) FROM user_tables"))
            table_count = result.fetchone()[0]
            print(f"✓ Total tables in schema: {table_count}")
            
            # List all tables created
            result = connection.execute(text("SELECT table_name FROM user_tables ORDER BY table_name"))
            tables = [row[0] for row in result.fetchall()]
            print(f"✓ All tables: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Missing tables creation failed: {e}")

if __name__ == "__main__":
    create_missing_tables()