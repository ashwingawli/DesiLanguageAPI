from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from typing import List
import random

from app.utils.database import get_db, get_pool_status, init_db, close_db, check_db_health
from app.utils.config import settings
from app.models import models, schemas
from app.api import crud
from app.api.auth import router as auth_router
from app.api.tts import router as tts_router
from app.api.admin import router as admin_router
from app.api.progress import router as progress_router
from app.api.stories import router as stories_router
from app.api.translations import router as translations_router
from app.api.enhanced_lessons import router as enhanced_lessons_router
from app.api.lessons import router as lessons_router
from app.services.gemini_service import gemini_service
from app.services.lesson_parser import lesson_parser

app = FastAPI(title="DesiLanguage API", description="Language Learning Lesson Generator")

# Add session middleware for Google OAuth session management
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    max_age=86400  # 24 hours
)

# Include authentication routes
app.include_router(auth_router, prefix="/api")

# Include TTS routes
app.include_router(tts_router, prefix="/api")

# Include admin routes (admin router already has /admin prefix)
app.include_router(admin_router)

# Include progress routes
app.include_router(progress_router, prefix="/api")

# Include stories routes
app.include_router(stories_router, prefix="/api")

# Include translation history routes
app.include_router(translations_router, prefix="/api")

# Include enhanced lessons routes
app.include_router(enhanced_lessons_router, prefix="/api")

# Include lessons routes
app.include_router(lessons_router, prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:5173",
        "http://localhost:5174", 
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """Initialize PostgreSQL database with optimized settings"""
    try:
        # Initialize PostgreSQL database with enhanced configuration
        init_db()
        print("✅ PostgreSQL database initialized successfully")
        print(f"📊 Connection pool status: {get_pool_status()}")
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        raise

@app.on_event("shutdown")
def shutdown_event():
    """Clean up PostgreSQL database connections on application shutdown"""
    try:
        close_db()
        print("✅ PostgreSQL database connections closed successfully")
    except Exception as e:
        print(f"❌ Error closing database connections: {str(e)}")

def load_lesson_topics() -> List[str]:
    """Load lesson topics from Lessons_title.txt"""
    try:
        return lesson_parser.get_lesson_titles()
    except FileNotFoundError:
        # Fallback to old files if new one doesn't exist
        try:
            with open('Lessons_n_themes.txt', 'r') as f:
                # Try to parse the old format
                topics = []
                for line in f:
                    line = line.strip()
                    if line.startswith("Lesson Title:"):
                        title = line.replace("Lesson Title:", "").strip()
                        if title:
                            topics.append(title)
                return topics
        except FileNotFoundError:
            try:
                with open('Lesson_topics.txt', 'r') as f:
                    return [line.strip() for line in f.readlines() if line.strip()]
            except FileNotFoundError:
                return []

@app.get("/")
def read_root():
    return {"message": "DesiLanguage API - Language Learning Lesson Generator"}

@app.get("/health")
def health_check():
    """Health check endpoint with PostgreSQL database status"""
    db_healthy = check_db_health()
    
    health_status = {
        "status": "healthy" if db_healthy else "unhealthy",
        "database_type": "postgresql",
        "database_status": "connected" if db_healthy else "disconnected",
        "connection_pool": get_pool_status() if db_healthy else None
    }
    
    return health_status

@app.post("/generate-desi-lesson", response_model=schemas.DesiLessonResponse)
async def generate_desi_lesson(
    request: schemas.DesiLessonRequest,
    save_to_db: bool = True,
    db: Session = Depends(get_db)
):
    try:
        
        # Get lesson details from Lessons_title.txt
        lesson_info = lesson_parser.get_lesson_by_title(request.lesson_topic)
        difficulty = "beginner"  # Default difficulty level
        
        lesson_response = await gemini_service.generate_desi_lesson(
            target_language=request.target_language,
            lesson_topic=request.lesson_topic,
            theme=request.lesson_topic  # Use topic as theme for Gemini
        )
        
        if save_to_db:
            crud.create_desi_lesson(db, lesson_response, difficulty)
        
        return lesson_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/desi-lesson-topics", response_model=List[str])
def get_desi_lesson_topics():
    return load_lesson_topics()



@app.get("/desi-lessons", response_model=List[schemas.DesiLessonDB])
def get_desi_lessons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    lessons = crud.get_desi_lessons(db, skip=skip, limit=limit)
    return lessons

@app.get("/desi-lessons/{lesson_id}")
def get_desi_lesson(lesson_id: int, include_content: bool = False, db: Session = Depends(get_db)):
    if include_content:
        lesson = crud.get_desi_lesson_with_content(db, lesson_id=lesson_id)
    else:
        lesson = crud.get_desi_lesson(db, lesson_id=lesson_id)
    
    if lesson is None:
        raise HTTPException(status_code=404, detail="Desi lesson not found")
    return lesson

@app.get("/desi-lessons/language/{target_language}", response_model=List[schemas.DesiLessonDB])
def get_desi_lessons_by_language(target_language: str, db: Session = Depends(get_db)):
    lessons = crud.get_desi_lessons_by_language(db, target_language=target_language)
    return lessons

@app.get("/get-or-generate-desi-lesson", response_model=schemas.DesiLessonResponse)
async def get_or_generate_desi_lesson(
    target_language: str,
    lesson_topic: str,
    db: Session = Depends(get_db)
):
    """
    First tries to find an existing lesson in the database.
    If not found, generates a new lesson and saves it to the database.
    """
    try:
        # First, try to find existing lesson in database
        existing_lesson = crud.find_desi_lesson_by_title_and_language(
            db, lesson_topic, target_language
        )
        
        if existing_lesson:
            # Convert database lesson to response format
            return crud.convert_db_lesson_to_response_format(existing_lesson)
        
        # If not found, generate new lesson
        lesson_info = lesson_parser.get_lesson_by_title(lesson_topic)
        difficulty = "beginner"  # Default difficulty level
        
        lesson_response = await gemini_service.generate_desi_lesson(
            target_language=target_language,
            lesson_topic=lesson_topic,
            theme=lesson_topic  # Use topic as theme for Gemini
        )
        
        # Save to database
        crud.create_desi_lesson(db, lesson_response, difficulty)
        
        return lesson_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/translate", response_model=schemas.TranslationResponse)
async def translate_text(
    request: schemas.TranslationRequest,
    db: Session = Depends(get_db)
):
    """
    Translate text between languages using Gemini AI
    Optionally saves to user history if authenticated
    """
    try:
        
        # Try to get current user (optional - won't fail if not authenticated)
        current_user = None
        try:
            from fastapi import Request
            # Check if authorization header exists
            # For now, let's skip auto-saving and let users use the dedicated endpoints
            pass
        except:
            pass
        
        # Use Gemini service to translate
        translation_result = await gemini_service.translate_text(
            text=request.text,
            from_language=request.from_language,
            to_language=request.to_language
        )
        
        # Format response
        response = schemas.TranslationResponse(
            original_text=request.text,
            translated_text=translation_result["translation"],
            transliteration=translation_result.get("transliteration"),
            from_language=request.from_language,
            to_language=request.to_language
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)