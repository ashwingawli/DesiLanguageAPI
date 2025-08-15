from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.utils.database import get_db
from app.services.enhanced_gemini_service import enhanced_gemini_service, EnhancedLearningData
from app.api import crud
from app.models.schemas import DesiLessonDB
from pydantic import BaseModel


class EnhancedLessonRequest(BaseModel):
    topic: str
    language: str
    difficulty: Optional[str] = "beginner"
    save_to_database: Optional[bool] = True


class EnhancedLessonResponse(BaseModel):
    success: bool
    data: Optional[EnhancedLearningData] = None
    lesson_db_info: Optional[DesiLessonDB] = None
    message: str


router = APIRouter()


@router.post("/enhanced-lesson", response_model=EnhancedLessonResponse)
async def generate_enhanced_lesson(
    request: EnhancedLessonRequest,
    db: Session = Depends(get_db)
):
    """
    Generate enhanced language learning materials equivalent to TypeScript desi_lesson_generate_GeminiService
    
    Returns:
    - 12 vocabulary words with translations and transliterations
    - 7 example sentences
    - 9 conversation lines between two speakers
    - 5 multiple-choice quiz questions
    
    Optionally saves transformed data to database using existing schema
    """
    try:
        # Validate inputs
        if not request.topic.strip():
            raise HTTPException(status_code=400, detail="Topic cannot be empty")
        
        if not request.language.strip():
            raise HTTPException(status_code=400, detail="Language cannot be empty")
        
        # Generate enhanced learning data
        learning_data = await enhanced_gemini_service.fetch_learning_data(
            topic=request.topic.strip(),
            language=request.language.strip()
        )
        
        
        lesson_db_info = None
        
        # Save to database if requested (default: True)
        if request.save_to_database:
            try:
                # Transform enhanced data to existing database format
                transformed_lesson = enhanced_gemini_service.transform_to_desi_lesson_format(
                    enhanced_data=learning_data,
                    topic=request.topic.strip(),
                    language=request.language.strip(),
                    difficulty=request.difficulty or "beginner"
                )
                
                # Save using existing CRUD function
                db_lesson = crud.create_desi_lesson(
                    db=db,
                    lesson_data=transformed_lesson,
                    difficulty=request.difficulty or "beginner"
                )
                
                lesson_db_info = DesiLessonDB(
                    id=db_lesson.id,
                    title=db_lesson.title,
                    target_language=db_lesson.target_language,
                    difficulty=db_lesson.difficulty,
                    lesson_number=db_lesson.lesson_number,
                    created_at=db_lesson.created_at
                )
                
                
            except Exception as db_error:
                # Log the database error for debugging
                print(f"Database insertion error: {str(db_error)}")
                import traceback
                traceback.print_exc()
                # Continue without failing the entire request
        
        success_message = f"Successfully generated enhanced lesson for '{request.topic}' in {request.language}"
        if lesson_db_info:
            success_message += f" and saved to database (ID: {lesson_db_info.id})"
        
        return EnhancedLessonResponse(
            success=True,
            data=learning_data,
            lesson_db_info=lesson_db_info,
            message=success_message
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate enhanced lesson: {str(e)}"
        )


@router.get("/enhanced-lesson/test")
async def test_enhanced_lesson_generation():
    """
    Test endpoint to verify enhanced lesson generation is working
    """
    try:
        # Test with a simple topic
        learning_data = await enhanced_gemini_service.fetch_learning_data(
            topic="Basic Greetings",
            language="Hindi"
        )
        
        return {
            "success": True,
            "message": "Enhanced lesson generation test successful",
            "data_summary": {
                "vocabulary_count": len(learning_data.vocabulary),
                "sentences_count": len(learning_data.sentences),
                "conversations_count": len(learning_data.conversations),
                "quiz_count": len(learning_data.quiz)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Test failed: {str(e)}"
        )


@router.post("/enhanced-lesson/validate")
async def validate_enhanced_lesson_structure(data: EnhancedLearningData):
    """
    Validate that enhanced lesson data matches the expected structure
    """
    try:
        # Basic validation through Pydantic model
        validation_results = {
            "vocabulary_valid": len(data.vocabulary) == 12,
            "sentences_valid": len(data.sentences) == 7,
            "conversations_valid": len(data.conversations) == 9,
            "quiz_valid": len(data.quiz) == 5,
            "quiz_options_valid": all(len(q.options) == 4 for q in data.quiz)
        }
        
        all_valid = all(validation_results.values())
        
        return {
            "success": all_valid,
            "validation_results": validation_results,
            "message": "Structure validation completed" if all_valid else "Structure validation failed"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )