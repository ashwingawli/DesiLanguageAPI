from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from app.utils.database import get_db
from app.api import crud
from app.models.schemas import DesiLessonResponse, DesiLessonDB, DesiLessonFromDB

router = APIRouter()


@router.get("/lessons/{language}/count")
async def get_lesson_count_by_language(
    language: str,
    db: Session = Depends(get_db)
):
    """
    Get the total number of lessons available for a language.
    Used for:
    - Progress indicators
    - Lesson navigation
    - Admin statistics
    """
    try:
        lessons = crud.get_desi_lessons_by_language(db=db, target_language=language)
        count = len(lessons)
        
        return {
            "language": language,
            "total_lessons": count,
            "available_numbers": [lesson.lesson_number for lesson in lessons]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get lesson count: {str(e)}"
        )


@router.get("/lessons/{language}/{lesson_number}")
async def get_lesson_by_language_and_number(
    language: str,
    lesson_number: int,
    include_content: bool = Query(True, description="Include full lesson content (vocabulary, sentences, etc.)"),
    db: Session = Depends(get_db)
):
    """
    Get a specific lesson by language and lesson number.
    Used by lessons page for:
    - Start lesson (regular users)
    - Review lesson (completed lessons)  
    - Launch lesson (admin bypass)
    
    Args:
        language: Target language (e.g., "Hindi", "Telugu", "Tamil")
        lesson_number: Lesson number (1, 2, 3, etc.)
        include_content: Whether to include full content or just metadata
        
    Returns:
        Full lesson data with vocabulary, sentences, story, and quiz
    """
    try:
        
        # Get lesson from database
        lesson = crud.get_desi_lesson_by_language_and_number(
            db=db,
            target_language=language,
            lesson_number=lesson_number
        )
        
        if not lesson:
            raise HTTPException(
                status_code=404,
                detail=f"Lesson {lesson_number} for {language} not found"
            )
        
        if include_content:
            # Return full lesson content using existing conversion function
            lesson_response = crud.convert_db_lesson_to_response_format(lesson)
            return lesson_response
        else:
            # Return just metadata
            lesson_db = DesiLessonDB(
                id=lesson.id,
                title=lesson.title,
                target_language=lesson.target_language,
                difficulty=lesson.difficulty,
                lesson_number=lesson.lesson_number,
                created_at=lesson.created_at
            )
            return lesson_db
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch lesson: {str(e)}"
        )


@router.get("/lessons/{language}")
async def get_lessons_by_language(
    language: str,
    skip: int = Query(0, ge=0, description="Number of lessons to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of lessons to return"),
    db: Session = Depends(get_db)
):
    """
    Get all lessons for a specific language.
    Used for:
    - Lesson selection page
    - Progress tracking
    - Admin lesson management
    
    Args:
        language: Target language
        skip: Pagination offset  
        limit: Maximum results
        
    Returns:
        List of lesson metadata (without full content for performance)
    """
    try:
        
        # Get lessons by language
        lessons = crud.get_desi_lessons_by_language(db=db, target_language=language)
        
        if not lessons:
            return []
        
        # Apply pagination
        paginated_lessons = lessons[skip:skip + limit]
        
        # Convert to response format
        lesson_list = []
        for lesson in paginated_lessons:
            lesson_db = DesiLessonDB(
                id=lesson.id,
                title=lesson.title,
                target_language=lesson.target_language,
                difficulty=lesson.difficulty,
                lesson_number=lesson.lesson_number,
                created_at=lesson.created_at
            )
            lesson_list.append(lesson_db)
        
        return lesson_list
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch lessons: {str(e)}"
        )



@router.get("/lessons/{language}/next")
async def get_next_lesson_number(
    language: str,
    db: Session = Depends(get_db)
):
    """
    Get the next available lesson number for a language.
    Used for:
    - Creating new lessons
    - Admin lesson management
    """
    try:
        # Get existing lessons for the language
        lessons = crud.get_desi_lessons_by_language(db=db, target_language=language)
        
        if not lessons:
            next_number = 1
        else:
            # Find the highest lesson number and add 1
            max_number = max(lesson.lesson_number for lesson in lessons)
            next_number = max_number + 1
        
        
        return {
            "language": language,
            "next_lesson_number": next_number,
            "existing_lessons": len(lessons)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get next lesson number: {str(e)}"
        )