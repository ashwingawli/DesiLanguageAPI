from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import random

from app.utils.database import get_db
from app.models import models, schemas
from app.api import crud
from app.services.gemini_service import gemini_service
from app.services.lesson_parser import lesson_parser

app = FastAPI(title="DesiLanguage API", description="Language Learning Lesson Generator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
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
    from app.utils.database import engine
    models.Base.metadata.create_all(bind=engine)

def load_lesson_topics() -> List[str]:
    """Load lesson topics from Lessons_n_themes.txt"""
    try:
        return lesson_parser.get_lesson_titles()
    except FileNotFoundError:
        # Fallback to old file if new one doesn't exist
        try:
            with open('Lesson_topics.txt', 'r') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            return []

@app.get("/")
def read_root():
    return {"message": "DesiLanguage API - Language Learning Lesson Generator"}

@app.post("/generate-desi-lesson", response_model=schemas.DesiLessonResponse)
async def generate_desi_lesson(
    request: schemas.DesiLessonRequest,
    save_to_db: bool = True,
    db: Session = Depends(get_db)
):
    try:
        # Get lesson details from Lessons_n_themes.txt
        lesson_info = lesson_parser.get_lesson_by_title(request.lesson_topic)
        theme = lesson_info["theme"] if lesson_info else request.lesson_topic
        
        lesson_response = await gemini_service.generate_desi_lesson(
            target_language=request.target_language,
            lesson_topic=request.lesson_topic,
            theme=theme
        )
        
        if save_to_db:
            crud.create_desi_lesson(db, lesson_response, theme)
        
        return lesson_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/desi-lesson-topics", response_model=List[str])
def get_desi_lesson_topics():
    return load_lesson_topics()

@app.get("/desi-lessons-with-themes")
def get_desi_lessons_with_themes():
    """Get all lesson titles and themes from Lessons_n_themes.txt"""
    try:
        lessons = lesson_parser.get_lessons()
        return {"lessons": lessons, "count": len(lessons)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Lessons_n_themes.txt file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/random-desi-topic")
def get_random_desi_topic():
    topics = load_lesson_topics()
    return {"topic": random.choice(topics)}

@app.post("/generate-random-desi-lesson", response_model=schemas.DesiLessonResponse)
async def generate_random_desi_lesson(
    target_language: str,
    save_to_db: bool = True,
    db: Session = Depends(get_db)
):
    topics = load_lesson_topics()
    if not topics:
        raise HTTPException(status_code=500, detail="No lesson topics available")
    
    random_topic = random.choice(topics)
    
    request = schemas.DesiLessonRequest(
        target_language=target_language,
        lesson_topic=random_topic
    )
    
    return await generate_desi_lesson(request, save_to_db, db)

@app.get("/desi-lessons", response_model=List[schemas.DesiLessonDB])
def get_desi_lessons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    lessons = crud.get_desi_lessons(db, skip=skip, limit=limit)
    return lessons

@app.get("/desi-lessons/{lesson_id}")
def get_desi_lesson(lesson_id: int, db: Session = Depends(get_db)):
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
        theme = lesson_info["theme"] if lesson_info else lesson_topic
        
        lesson_response = await gemini_service.generate_desi_lesson(
            target_language=target_language,
            lesson_topic=lesson_topic,
            theme=theme
        )
        
        # Save to database
        crud.create_desi_lesson(db, lesson_response, theme)
        
        return lesson_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)