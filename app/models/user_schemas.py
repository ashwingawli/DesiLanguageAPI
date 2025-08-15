from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    TEACHER = "teacher"

# User Authentication Schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthRequest(BaseModel):
    email: str
    name: str
    google_id: str
    picture: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

# User Profile Schemas
class UserProfileCreate(BaseModel):
    bio: Optional[str] = None
    birth_date: Optional[datetime] = None
    country: Optional[str] = None
    timezone: str = "UTC"
    native_language: Optional[str] = None
    learning_languages: List[str] = []
    primary_learning_language: Optional[str] = None
    learning_goal: Optional[str] = None
    daily_goal_minutes: int = 15

class UserProfileUpdate(BaseModel):
    bio: Optional[str] = None
    birth_date: Optional[datetime] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    native_language: Optional[str] = None
    learning_languages: Optional[List[str]] = None
    primary_learning_language: Optional[str] = None
    learning_goal: Optional[str] = None
    daily_goal_minutes: Optional[int] = None

class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    avatar_url: Optional[str]
    bio: Optional[str]
    birth_date: Optional[datetime]
    country: Optional[str]
    timezone: str
    native_language: Optional[str]
    learning_languages: List[str]
    primary_learning_language: Optional[str]
    learning_goal: Optional[str]
    daily_goal_minutes: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Subscription Schemas
class UserSubscriptionResponse(BaseModel):
    id: int
    user_id: int
    tier: SubscriptionTier
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    trial_end_date: Optional[datetime]
    auto_renew: bool

    class Config:
        from_attributes = True

class SubscriptionUpdate(BaseModel):
    tier: Optional[SubscriptionTier] = None
    auto_renew: Optional[bool] = None

# Progress Schemas
class UserProgressResponse(BaseModel):
    id: int
    user_id: int
    language: str
    total_lessons_completed: int
    total_words_learned: int
    total_quiz_score: float
    current_streak: int
    longest_streak: int
    total_study_time_minutes: int
    level: int
    experience_points: int
    last_activity_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProgressUpdate(BaseModel):
    lesson_completed: bool = False
    words_learned: int = 0
    quiz_score: Optional[float] = None
    study_time_minutes: int = 0

# Lesson Completion Schemas
class LessonCompletionCreate(BaseModel):
    lesson_id: int
    language: str
    time_spent_minutes: int = 0
    sections_completed: List[str] = []
    overall_score: Optional[float] = None

class LessonCompletionResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    language: str
    completed_at: datetime
    time_spent_minutes: int
    sections_completed: List[str]
    overall_score: Optional[float]

    class Config:
        from_attributes = True

# Quiz Attempt Schemas
class QuizAttemptCreate(BaseModel):
    lesson_id: int
    quiz_question_id: int
    user_answer: str
    time_taken_seconds: Optional[int] = None

class QuizAttemptResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    quiz_question_id: int
    user_answer: str
    is_correct: bool
    time_taken_seconds: Optional[int]
    attempt_date: datetime

    class Config:
        from_attributes = True

# Achievement Schemas
class AchievementResponse(BaseModel):
    id: int
    name: str
    title: str
    description: str
    icon: Optional[str]
    category: str
    points_reward: int

    class Config:
        from_attributes = True

class UserAchievementResponse(BaseModel):
    id: int
    user_id: int
    achievement: AchievementResponse
    earned_at: datetime
    progress_data: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True

# Settings Schemas
class UserSettingsUpdate(BaseModel):
    # Notification settings
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    reminder_notifications: Optional[bool] = None
    achievement_notifications: Optional[bool] = None
    
    # Learning settings
    audio_enabled: Optional[bool] = None
    auto_play_audio: Optional[bool] = None
    show_transliteration: Optional[bool] = None
    show_pronunciation: Optional[bool] = None
    difficulty_preference: Optional[str] = None
    
    # Privacy settings
    profile_public: Optional[bool] = None
    show_progress_to_friends: Optional[bool] = None
    
    # Theme and UI
    theme: Optional[str] = None
    language_display_script: Optional[bool] = None

class UserSettingsResponse(BaseModel):
    id: int
    user_id: int
    # Notification settings
    email_notifications: bool
    push_notifications: bool
    reminder_notifications: bool
    achievement_notifications: bool
    # Learning settings
    audio_enabled: bool
    auto_play_audio: bool
    show_transliteration: bool
    show_pronunciation: bool
    difficulty_preference: str
    # Privacy settings
    profile_public: bool
    show_progress_to_friends: bool
    # Theme and UI
    theme: str
    language_display_script: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Study Session Schemas
class StudySessionCreate(BaseModel):
    language: str

class StudySessionUpdate(BaseModel):
    lessons_completed: Optional[int] = None
    words_learned: Optional[int] = None
    quiz_score: Optional[float] = None
    activities: Optional[List[Dict[str, Any]]] = None

class StudySessionResponse(BaseModel):
    id: int
    user_id: int
    language: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: Optional[int]
    lessons_completed: int
    words_learned: int
    quiz_score: Optional[float]
    activities: List[Dict[str, Any]]

    class Config:
        from_attributes = True

# Complete User Profile (for dashboard)
class CompleteUserProfile(BaseModel):
    user: UserResponse
    profile: UserProfileResponse
    subscription: UserSubscriptionResponse
    progress: List[UserProgressResponse]
    recent_achievements: List[UserAchievementResponse]
    settings: UserSettingsResponse
    active_study_session: Optional[StudySessionResponse]

    class Config:
        from_attributes = True

# Dashboard Statistics
class DashboardStats(BaseModel):
    total_users: int
    active_users_today: int
    active_users_week: int
    total_lessons_completed: int
    total_study_time_hours: float
    top_languages: List[Dict[str, Any]]
    subscription_breakdown: Dict[str, int]