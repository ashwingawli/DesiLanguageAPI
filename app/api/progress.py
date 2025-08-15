from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
import json
from typing import List, Optional

from app.utils.database import get_db
from app.models.models import User, UserProgress, UserProfile, LessonCompletion, QuizAttempt
from app.models.user_schemas import (
    UserProgressResponse, ProgressUpdate, LessonCompletionCreate, 
    LessonCompletionResponse, QuizAttemptCreate, QuizAttemptResponse,
    UserProfileUpdate, UserProfileResponse
)
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/progress", tags=["User Progress"])

@router.get("/", response_model=List[UserProgressResponse])
def get_user_progress(
    language: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's progress for all languages or a specific language."""
    query = db.query(UserProgress).filter(UserProgress.user_id == current_user.id)
    
    if language:
        query = query.filter(UserProgress.language == language)
    
    progress = query.all()
    return [UserProgressResponse.from_orm(p) for p in progress]

@router.get("/stats", response_model=dict)
def get_user_stats(
    language: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive user statistics."""
    print(f"🔍 Stats endpoint called for user {current_user.id}, language: {language}")
    
    # Get progress records (exclude stats records)
    query = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.language != 'stats'  # Exclude stats records
    )
    
    # Filter by language if specified
    if language:
        query = query.filter(UserProgress.language == language)
    
    all_progress = query.all()
    
    print(f"📊 Found {len(all_progress)} progress records")
    for p in all_progress:
        print(f"  - {p.language}: {p.total_lessons_completed} lessons, {p.total_words_learned} words")
    
    # Get profile for primary language
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    # Calculate total stats
    total_lessons = sum(p.total_lessons_completed for p in all_progress)
    total_words = sum(p.total_words_learned for p in all_progress)
    total_time = sum(p.total_study_time_minutes for p in all_progress)
    
    print(f"📈 Calculated totals: {total_lessons} lessons, {total_words} words, {total_time} minutes")
    
    # Get current streak for primary language
    current_streak = 0
    primary_language = profile.primary_learning_language if profile else None
    if primary_language:
        primary_progress = next((p for p in all_progress if p.language == primary_language), None)
        if primary_progress:
            current_streak = primary_progress.current_streak
    
    # Get recent completions
    completion_query = db.query(LessonCompletion).filter(
        LessonCompletion.user_id == current_user.id
    )
    
    # Filter completions by language if specified
    if language:
        completion_query = completion_query.filter(LessonCompletion.language == language)
    
    recent_completions = completion_query.order_by(LessonCompletion.completed_at.desc()).limit(5).all()
    
    result = {
        "total_lessons_completed": total_lessons,
        "total_words_learned": total_words,
        "total_study_time_minutes": total_time,
        "current_streak": current_streak,
        "languages_learning": len(all_progress),
        "primary_language": primary_language,
        "recent_completions": [
            {
                "lesson_id": c.lesson_id,
                "language": c.language,
                "completed_at": c.completed_at,
                "score": c.overall_score
            }
            for c in recent_completions
        ],
        "progress_by_language": [
            {
                "language": p.language,
                "lessons_completed": p.total_lessons_completed,
                "words_learned": p.total_words_learned,
                "level": p.level,
                "current_streak": p.current_streak
            }
            for p in all_progress
        ]
    }
    
    print(f"📤 Returning stats: {result}")
    return result

@router.get("/{language}", response_model=UserProgressResponse)
def get_language_progress(
    language: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's progress for a specific language."""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.language == language
    ).first()
    
    if not progress:
        # Create initial progress record for this language
        progress = UserProgress(
            user_id=current_user.id,
            language=language,
            total_lessons_completed=0,
            total_words_learned=0,
            total_quiz_score=0.0,
            current_streak=0,
            longest_streak=0,
            total_study_time_minutes=0,
            level=1,
            experience_points=0,
            last_activity_date=None
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
    
    return UserProgressResponse.from_orm(progress)

@router.put("/{language}", response_model=UserProgressResponse)
def update_language_progress(
    language: str,
    progress_data: ProgressUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user's progress for a specific language."""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.language == language
    ).first()
    
    if not progress:
        # Create initial progress record
        progress = UserProgress(
            user_id=current_user.id,
            language=language,
            total_lessons_completed=0,
            total_words_learned=0,
            total_quiz_score=0.0,
            current_streak=0,
            longest_streak=0,
            total_study_time_minutes=0,
            level=1,
            experience_points=0
        )
        db.add(progress)
    
    # Update progress based on input
    if progress_data.lesson_completed:
        progress.total_lessons_completed += 1
        
        # Update streak - handle timezone-aware/naive datetime comparison
        current_time = datetime.now(timezone.utc)
        if progress.last_activity_date:
            # Make last_activity_date timezone-aware if it's naive
            if progress.last_activity_date.tzinfo is None:
                last_activity = progress.last_activity_date.replace(tzinfo=timezone.utc)
            else:
                last_activity = progress.last_activity_date
            
            # Check if it's been exactly 1 day since last activity
            if (current_time - last_activity).days == 1:
                progress.current_streak += 1
            else:
                progress.current_streak = 1
        else:
            progress.current_streak = 1
        
        if progress.current_streak > progress.longest_streak:
            progress.longest_streak = progress.current_streak
    
    if progress_data.words_learned > 0:
        progress.total_words_learned += progress_data.words_learned
    
    if progress_data.quiz_score is not None:
        # Update average quiz score
        if progress.total_quiz_score == 0:
            progress.total_quiz_score = progress_data.quiz_score
        else:
            progress.total_quiz_score = (progress.total_quiz_score + progress_data.quiz_score) / 2
    
    if progress_data.study_time_minutes > 0:
        progress.total_study_time_minutes += progress_data.study_time_minutes
    
    # Set level based on lessons completed (simple level system)
    if progress.total_lessons_completed <= 10:
        progress.level = 1
    elif progress.total_lessons_completed <= 25:
        progress.level = 2
    elif progress.total_lessons_completed <= 50:
        progress.level = 3
    else:
        progress.level = 4
    
    current_time = datetime.now(timezone.utc)
    progress.last_activity_date = current_time
    progress.updated_at = current_time
    
    db.commit()
    db.refresh(progress)
    
    return UserProgressResponse.from_orm(progress)

@router.post("/lessons", response_model=LessonCompletionResponse)
def complete_lesson(
    completion_data: LessonCompletionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record a lesson completion."""
    # Check if lesson was already completed
    existing_completion = db.query(LessonCompletion).filter(
        LessonCompletion.user_id == current_user.id,
        LessonCompletion.lesson_id == completion_data.lesson_id,
        LessonCompletion.language == completion_data.language
    ).first()
    
    if existing_completion:
        # Update existing completion with better score
        if completion_data.overall_score and (
            not existing_completion.overall_score or 
            completion_data.overall_score > existing_completion.overall_score
        ):
            existing_completion.overall_score = completion_data.overall_score
            existing_completion.time_spent_minutes = completion_data.time_spent_minutes
            existing_completion.sections_completed = completion_data.sections_completed
            existing_completion.completed_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing_completion)
        
        return LessonCompletionResponse.from_orm(existing_completion)
    
    # Create new completion record
    completion = LessonCompletion(
        user_id=current_user.id,
        lesson_id=completion_data.lesson_id,
        language=completion_data.language,
        time_spent_minutes=completion_data.time_spent_minutes,
        sections_completed=completion_data.sections_completed,
        overall_score=completion_data.overall_score
    )
    
    db.add(completion)
    db.commit()
    db.refresh(completion)
    
    # Update user progress
    progress_update = ProgressUpdate(
        lesson_completed=True,
        words_learned=len([s for s in completion_data.sections_completed if s == "vocabulary"]) * 10,
        quiz_score=completion_data.overall_score,
        study_time_minutes=completion_data.time_spent_minutes
    )
    
    # Update progress (this will handle streak calculation)
    update_language_progress(completion_data.language, progress_update, current_user, db)
    
    return LessonCompletionResponse.from_orm(completion)

@router.get("/lessons", response_model=List[LessonCompletionResponse])
def get_lesson_completions(
    language: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's lesson completions."""
    query = db.query(LessonCompletion).filter(LessonCompletion.user_id == current_user.id)
    
    if language:
        query = query.filter(LessonCompletion.language == language)
    
    completions = query.order_by(LessonCompletion.completed_at.desc()).limit(limit).all()
    return [LessonCompletionResponse.from_orm(c) for c in completions]

@router.post("/quiz", response_model=QuizAttemptResponse)
def submit_quiz_attempt(
    attempt_data: QuizAttemptCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record a quiz attempt."""
    # Check if answer is correct (you'd need to implement this logic)
    # For now, we'll assume the frontend validates this
    
    attempt = QuizAttempt(
        user_id=current_user.id,
        lesson_id=attempt_data.lesson_id,
        quiz_question_id=attempt_data.quiz_question_id,
        user_answer=attempt_data.user_answer,
        is_correct=False,  # This should be calculated based on correct answer
        time_taken_seconds=attempt_data.time_taken_seconds
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return QuizAttemptResponse.from_orm(attempt)

@router.put("/language/{language}/select", response_model=UserProfileResponse)
def set_primary_language(
    language: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Set user's primary learning language."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # Update primary language
    profile.primary_learning_language = language
    
    # Add to learning languages list if not already there
    # Handle Oracle CLOB JSON field properly
    
    if not profile.learning_languages:
        profile.learning_languages = json.dumps([language])
    else:
        try:
            # Parse existing JSON string
            current_languages = json.loads(profile.learning_languages) if isinstance(profile.learning_languages, str) else profile.learning_languages
            if not isinstance(current_languages, list):
                current_languages = [language]
            elif language not in current_languages:
                current_languages.append(language)
            profile.learning_languages = json.dumps(current_languages)
        except (json.JSONDecodeError, TypeError):
            # If parsing fails, create new list with just this language
            profile.learning_languages = json.dumps([language])
    
    profile.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(profile)
    
    # Ensure user has progress record for this language
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.language == language
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            language=language,
            total_lessons_completed=0,
            total_words_learned=0,
            total_quiz_score=0.0,
            current_streak=0,
            longest_streak=0,
            total_study_time_minutes=0,
            level=1,
            experience_points=0
        )
        db.add(progress)
        db.commit()
    
    # Convert JSON string back to list for response
    learning_languages_list = []
    if profile.learning_languages:
        try:
            learning_languages_list = json.loads(profile.learning_languages) if isinstance(profile.learning_languages, str) else profile.learning_languages
            if not isinstance(learning_languages_list, list):
                learning_languages_list = []
        except (json.JSONDecodeError, TypeError):
            learning_languages_list = []
    
    # Create response with converted data
    response_data = {
        "id": profile.id,
        "user_id": profile.user_id,
        "avatar_url": profile.avatar_url,
        "bio": profile.bio,
        "birth_date": profile.birth_date,
        "country": profile.country,
        "timezone": profile.timezone,
        "native_language": profile.native_language,
        "learning_languages": learning_languages_list,
        "primary_learning_language": profile.primary_learning_language,
        "learning_goal": profile.learning_goal,
        "daily_goal_minutes": profile.daily_goal_minutes,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at
    }
    
    return UserProfileResponse(**response_data)