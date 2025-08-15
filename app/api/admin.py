from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.utils.database import get_db
from app.models.models import User, UserProfile, UserSubscription, UserProgress, DesiLesson
from app.models.user_schemas import (
    UserResponse, 
    DashboardStats, 
    UserRole, 
    SubscriptionTier,
    CompleteUserProfile
)
from app.auth.dependencies import get_admin_user
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload, selectinload

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_admin_dashboard_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get admin dashboard statistics."""
    
    # Total users
    total_users = db.query(User).count()
    
    # Active users today
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    active_users_today = db.query(User).filter(
        User.last_login >= today_start,
        User.last_login <= today_end
    ).count()
    
    # Active users this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_users_week = db.query(User).filter(
        User.last_login >= week_ago
    ).count()
    
    # Total lessons completed
    total_lessons_completed = db.query(func.sum(UserProgress.total_lessons_completed)).scalar() or 0
    
    # Total study time
    total_study_minutes = db.query(func.sum(UserProgress.total_study_time_minutes)).scalar() or 0
    total_study_time_hours = round(total_study_minutes / 60, 2) if total_study_minutes else 0
    
    # Top languages
    top_languages = db.query(
        UserProgress.language,
        func.count(UserProgress.id).label('user_count'),
        func.sum(UserProgress.total_lessons_completed).label('total_lessons')
    ).group_by(UserProgress.language).order_by(desc('user_count')).limit(5).all()
    
    top_languages_list = [
        {
            "language": lang[0],
            "user_count": lang[1],
            "total_lessons": lang[2] or 0
        }
        for lang in top_languages
    ]
    
    # Subscription breakdown
    subscription_counts = db.query(
        UserSubscription.tier,
        func.count(UserSubscription.id).label('count')
    ).group_by(UserSubscription.tier).all()
    
    subscription_breakdown = {tier.value: 0 for tier in SubscriptionTier}
    for tier, count in subscription_counts:
        subscription_breakdown[tier.value] = count
    
    # Add users without subscriptions as free
    users_without_subscription = total_users - sum(subscription_breakdown.values())
    subscription_breakdown["free"] += users_without_subscription
    
    return DashboardStats(
        total_users=total_users,
        active_users_today=active_users_today,
        active_users_week=active_users_week,
        total_lessons_completed=total_lessons_completed,
        total_study_time_hours=total_study_time_hours,
        top_languages=top_languages_list,
        subscription_breakdown=subscription_breakdown
    )

@router.get("/users")
async def get_all_users(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by email, username, or full name"),
    role: Optional[str] = Query(None, description="Filter by user role"),
    status: Optional[str] = Query(None, description="Filter by status (active/inactive)"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get all users with filtering and pagination."""
    
    query = db.query(User)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_filter)) |
            (User.username.ilike(search_filter)) |
            (User.full_name.ilike(search_filter))
        )
    
    if role and role != 'all':
        try:
            role_enum = UserRole(role)
            query = query.filter(User.role == role_enum)
        except ValueError:
            pass  # Invalid role, ignore filter
    
    if status and status != 'all':
        if status == 'active':
            query = query.filter(User.is_active == True)
        elif status == 'inactive':
            query = query.filter(User.is_active == False)
    
    # Get total count for pagination
    total_count = query.count()
    
    # Calculate pagination
    offset = (page - 1) * page_size
    total_pages = (total_count + page_size - 1) // page_size
    has_next = page < total_pages
    has_previous = page > 1
    
    # Apply pagination and get results with optimized loading
    # Use selectinload for one-to-many relationships to avoid N+1 queries
    users = query.options(
        selectinload(User.profile),
        selectinload(User.subscription),
        selectinload(User.progress)
    ).order_by(desc(User.created_at)).offset(offset).limit(page_size).all()
    
    # Convert users to UserResponse format
    user_responses = [UserResponse.from_orm(user) for user in users]
    
    return {
        "users": user_responses,
        "pagination": {
            "current_page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    }

@router.get("/users/{user_id}", response_model=CompleteUserProfile)
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get complete user profile details."""
    
    user = db.query(User).options(
        selectinload(User.profile),
        selectinload(User.subscription), 
        selectinload(User.progress),
        selectinload(User.achievements),
        selectinload(User.settings)
    ).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get related data
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
    
    # Note: These would need to be implemented if the models exist
    recent_achievements = []  # db.query(UserAchievement).filter(...).limit(5).all()
    settings = None  # db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    active_study_session = None  # db.query(StudySession).filter(...).first()
    
    return CompleteUserProfile(
        user=user,
        profile=profile,
        subscription=subscription,
        progress=progress,
        recent_achievements=recent_achievements,
        settings=settings,
        active_study_session=active_study_session
    )

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: UserRole,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Update a user's role."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from demoting themselves
    if user.id == admin_user.id and new_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin role"
        )
    
    user.role = new_role
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return {"message": f"User role updated to {new_role.value}", "user": user}

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Activate or deactivate a user."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deactivating themselves
    if user.id == admin_user.id and not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user.is_active = is_active
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    status_text = "activated" if is_active else "deactivated"
    return {"message": f"User {status_text} successfully", "user": user}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Delete a user account."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deleting themselves
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@router.get("/lessons")
async def get_lessons_admin(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(15, ge=1, le=100, description="Number of lessons per page"),
    language: Optional[str] = Query(None, description="Filter by target language"),
    search: Optional[str] = Query(None, description="Search in title, language, or difficulty"),
    sort_by: Optional[str] = Query("newest", description="Sort by: newest, oldest, title, language, lesson_number"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get paginated lessons with admin details."""
    
    query = db.query(DesiLesson)
    
    # Apply filters
    if language:
        query = query.filter(DesiLesson.target_language.ilike(f"%{language}%"))
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (DesiLesson.title.ilike(search_filter)) |
            (DesiLesson.target_language.ilike(search_filter)) |
            (DesiLesson.difficulty.ilike(search_filter))
        )
    
    # Apply sorting
    if sort_by == "newest":
        query = query.order_by(desc(DesiLesson.created_at))
    elif sort_by == "oldest":
        query = query.order_by(DesiLesson.created_at)
    elif sort_by == "title":
        query = query.order_by(DesiLesson.title)
    elif sort_by == "language":
        query = query.order_by(DesiLesson.target_language)
    elif sort_by == "lesson_number":
        query = query.order_by(DesiLesson.lesson_number)
    else:
        query = query.order_by(desc(DesiLesson.created_at))
    
    # Get total count for pagination
    total_count = query.count()
    
    # Calculate pagination
    skip = (page - 1) * page_size
    total_pages = (total_count + page_size - 1) // page_size
    
    # Get paginated results with optimized loading
    lessons = query.options(
        selectinload(DesiLesson.vocabulary),
        selectinload(DesiLesson.example_sentences),
        selectinload(DesiLesson.quiz_questions),
        selectinload(DesiLesson.short_story)
    ).offset(skip).limit(page_size).all()
    
    # Add admin-specific information
    lesson_data = []
    for lesson in lessons:
        lesson_info = {
            "id": lesson.id,
            "title": lesson.title,
            "target_language": lesson.target_language,
            "difficulty": lesson.difficulty,
            "lesson_number": lesson.lesson_number,
            "created_at": lesson.created_at,
            "vocabulary_count": len(lesson.vocabulary),
            "example_sentences_count": len(lesson.example_sentences),
            "quiz_questions_count": len(lesson.quiz_questions),
            "has_story": lesson.short_story is not None
        }
        lesson_data.append(lesson_info)
    
    return {
        "lessons": lesson_data,
        "pagination": {
            "current_page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    }

@router.delete("/lessons/{lesson_id}")
async def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Delete a lesson."""
    
    lesson = db.query(DesiLesson).filter(DesiLesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    db.delete(lesson)
    db.commit()
    
    return {"message": "Lesson deleted successfully"}

@router.get("/users/{user_id}/progress")
async def get_user_progress(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get detailed progress for a specific user."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
    
    return {
        "user": user,
        "progress": progress,
        "total_languages": len(progress),
        "total_lessons_completed": sum(p.total_lessons_completed for p in progress),
        "total_study_time_hours": round(sum(p.total_study_time_minutes for p in progress) / 60, 2) if progress else 0
    }