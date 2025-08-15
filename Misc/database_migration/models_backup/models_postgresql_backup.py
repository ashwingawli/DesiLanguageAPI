from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean, Float, Enum, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()

class DesiLesson(Base):
    __tablename__ = "desi_lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    target_language = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    lesson_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vocabulary = relationship("DesiVocabulary", back_populates="lesson", cascade="all, delete-orphan")
    example_sentences = relationship("DesiExampleSentence", back_populates="lesson", cascade="all, delete-orphan")
    short_story = relationship("DesiShortStory", back_populates="lesson", uselist=False, cascade="all, delete-orphan")
    quiz_questions = relationship("DesiQuizQuestion", back_populates="lesson", cascade="all, delete-orphan")

class DesiVocabulary(Base):
    __tablename__ = "desi_vocabulary"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("desi_lessons.id", ondelete="CASCADE"))
    english = Column(String, nullable=False)
    target_language_script = Column(String, nullable=False)
    transliteration = Column(String, nullable=False)
    pronunciation = Column(String, nullable=False)
    
    lesson = relationship("DesiLesson", back_populates="vocabulary")

class DesiExampleSentence(Base):
    __tablename__ = "desi_example_sentences"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("desi_lessons.id", ondelete="CASCADE"))
    english = Column(Text, nullable=False)
    target_language_script = Column(Text, nullable=False)
    transliteration = Column(Text, nullable=False)
    pronunciation = Column(Text, nullable=False)
    
    lesson = relationship("DesiLesson", back_populates="example_sentences")

class DesiShortStory(Base):
    __tablename__ = "desi_short_stories"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("desi_lessons.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    
    lesson = relationship("DesiLesson", back_populates="short_story")
    dialogue = relationship("DesiDialogue", back_populates="short_story", cascade="all, delete-orphan")

class DesiDialogue(Base):
    __tablename__ = "desi_dialogue"
    
    id = Column(Integer, primary_key=True, index=True)
    short_story_id = Column(Integer, ForeignKey("desi_short_stories.id", ondelete="CASCADE"))
    speaker = Column(String, nullable=False)
    target_language_script = Column(Text, nullable=False)
    transliteration = Column(Text, nullable=False)
    english = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    
    short_story = relationship("DesiShortStory", back_populates="dialogue")

class DesiQuizQuestion(Base):
    __tablename__ = "desi_quiz_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("desi_lessons.id", ondelete="CASCADE"))
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    answer = Column(String, nullable=False)
    
    lesson = relationship("DesiLesson", back_populates="quiz_questions")

# User Management Models

class SubscriptionTier(PyEnum):
    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"

class UserRole(PyEnum):
    USER = "user"
    ADMIN = "admin"
    TEACHER = "teacher"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    subscription = relationship("UserSubscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    lesson_completions = relationship("LessonCompletion", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    translations = relationship("UserTranslation", back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    avatar_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    birth_date = Column(DateTime, nullable=True)
    country = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    native_language = Column(String, nullable=True)
    learning_languages = Column(JSON, default=list)  # List of languages user is learning
    primary_learning_language = Column(String, nullable=True)
    learning_goal = Column(String, nullable=True)  # e.g., "travel", "business", "family"
    daily_goal_minutes = Column(Integer, default=15)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="profile")

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    status = Column(String, default="active")  # active, cancelled, expired, suspended
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    trial_end_date = Column(DateTime, nullable=True)
    auto_renew = Column(Boolean, default=True)
    stripe_subscription_id = Column(String, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="subscription")

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    language = Column(String, nullable=False)
    total_lessons_completed = Column(Integer, default=0)
    total_words_learned = Column(Integer, default=0)
    total_quiz_score = Column(Float, default=0.0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_study_time_minutes = Column(Integer, default=0)
    level = Column(Integer, default=1)
    experience_points = Column(Integer, default=0)
    last_activity_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="progress")

class LessonCompletion(Base):
    __tablename__ = "lesson_completions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    lesson_id = Column(Integer, ForeignKey("desi_lessons.id", ondelete="CASCADE"))
    language = Column(String, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    time_spent_minutes = Column(Integer, default=0)
    sections_completed = Column(JSON, default=list)  # ["vocabulary", "sentences", "conversations", "quiz"]
    overall_score = Column(Float, nullable=True)
    
    user = relationship("User", back_populates="lesson_completions")
    lesson = relationship("DesiLesson")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    lesson_id = Column(Integer, ForeignKey("desi_lessons.id", ondelete="CASCADE"))
    quiz_question_id = Column(Integer, ForeignKey("desi_quiz_questions.id", ondelete="CASCADE"))
    user_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken_seconds = Column(Integer, nullable=True)
    attempt_date = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="quiz_attempts")
    lesson = relationship("DesiLesson")
    question = relationship("DesiQuizQuestion")

class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String, nullable=True)
    category = Column(String, nullable=False)  # streak, lessons, words, quiz, milestone
    criteria = Column(JSON, nullable=False)  # Conditions to unlock
    points_reward = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user_achievements = relationship("UserAchievement", back_populates="achievement")

class UserAchievement(Base):
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"))
    earned_at = Column(DateTime, default=datetime.utcnow)
    progress_data = Column(JSON, nullable=True)  # Track progress towards achievement
    
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Notification settings
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    reminder_notifications = Column(Boolean, default=True)
    achievement_notifications = Column(Boolean, default=True)
    
    # Learning settings
    audio_enabled = Column(Boolean, default=True)
    auto_play_audio = Column(Boolean, default=False)
    show_transliteration = Column(Boolean, default=True)
    show_pronunciation = Column(Boolean, default=True)
    difficulty_preference = Column(String, default="adaptive")  # beginner, intermediate, advanced, adaptive
    
    # Privacy settings
    profile_public = Column(Boolean, default=False)
    show_progress_to_friends = Column(Boolean, default=True)
    
    # Theme and UI
    theme = Column(String, default="light")  # light, dark, auto
    language_display_script = Column(Boolean, default=True)  # Show native script or transliteration
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="settings")

class StudySession(Base):
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    language = Column(String, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    lessons_completed = Column(Integer, default=0)
    words_learned = Column(Integer, default=0)
    quiz_score = Column(Float, nullable=True)
    activities = Column(JSON, default=list)  # Track what user did in session
    
    user = relationship("User")


class UserTranslation(Base):
    __tablename__ = "user_translations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    from_text = Column(Text, nullable=False)
    to_text = Column(Text, nullable=False)
    to_text_transliteration = Column(Text, nullable=True)
    from_language = Column(String, nullable=False)  # Language code (e.g., "en", "hi")
    to_language = Column(String, nullable=False)    # Language code (e.g., "en", "hi")
    from_language_name = Column(String, nullable=False)  # Full language name (e.g., "English", "Hindi")
    to_language_name = Column(String, nullable=False)    # Full language name (e.g., "English", "Hindi")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="translations")

# Generated Stories Models

class DesiStory(Base):
    __tablename__ = "desi_stories"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)  # Optional title for the story
    target_language = Column(String, nullable=False)
    cefr_level = Column(String, nullable=False)  # A1, A2, B1, B2
    scenario = Column(String, nullable=True)  # Custom scenario if provided
    english_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    transliteration = Column(Text, nullable=True)  # For non-Latin scripts
    generated_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # Track who generated it
    is_custom = Column(Boolean, default=False)  # True if generated with custom scenario
    generation_prompt = Column(Text, nullable=True)  # Store the prompt used for generation
    
    # Relationships
    vocabulary = relationship("DesiStoryVocabulary", back_populates="story", cascade="all, delete-orphan")
    user = relationship("User")

class DesiStoryVocabulary(Base):
    __tablename__ = "desi_story_vocabulary"
    
    id = Column(Integer, primary_key=True, index=True) 
    story_id = Column(Integer, ForeignKey("desi_stories.id", ondelete="CASCADE"))
    word = Column(String, nullable=False)
    definition = Column(Text, nullable=True)
    transliteration = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)  # To maintain vocabulary order
    
    story = relationship("DesiStory", back_populates="vocabulary")