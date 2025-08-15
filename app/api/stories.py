from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models.schemas import (
    StoryGenerationRequest, 
    StoryResponse, 
    Language, 
    CEFRLevel,
    StoryData,
    DesiStoryDB
)
from app.services.story_service import story_service
from app.api.story_crud import get_desi_stories, get_story_statistics, convert_db_story_to_response_format
from app.utils.database import get_db

router = APIRouter()

@router.post("/stories/generate", response_model=StoryResponse)
async def generate_story(request: StoryGenerationRequest, db: Session = Depends(get_db)):
    """Generate a story based on CEFR level and language"""
    try:
        
        story_data = await story_service.generate_story(
            request=request, 
            db=db, 
            user_id=None,  # TODO: Get from authentication when available
            save_to_db=True
        )
        
        return StoryResponse(
            story_data=story_data,
            target_language=request.language,
            level=request.level
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stories/generate-custom", response_model=StoryResponse)
async def generate_custom_story(request: StoryGenerationRequest, db: Session = Depends(get_db)):
    """Generate a custom story with a specific scenario"""
    try:
        if not request.scenario:
            raise HTTPException(status_code=400, detail="Scenario is required for custom story generation")
        
        
        story_data = await story_service.generate_custom_story(
            request=request, 
            db=db, 
            user_id=None,  # TODO: Get from authentication when available
            save_to_db=True
        )
        
        return StoryResponse(
            story_data=story_data,
            target_language=request.language,
            level=request.level
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stories/languages", response_model=List[str])
def get_supported_languages():
    """Get list of Indian languages for story generation"""
    # 12 Indian languages supported in DesiLanguage
    indian_languages = [
        Language.Hindi,
        Language.Urdu,
        Language.Punjabi,
        Language.Bengali,
        Language.Gujarati,
        Language.Odia,
        Language.Marathi,
        Language.Tamil,
        Language.Telugu,
        Language.Kannada,
        Language.Malayalam,
        Language.Assamese,
    ]
    return [lang.value for lang in indian_languages]

@router.get("/stories/levels", response_model=List[str])
def get_cefr_levels():
    """Get list of supported CEFR levels"""
    return [level.value for level in CEFRLevel]

@router.get("/stories/level-descriptions")
def get_level_descriptions():
    """Get CEFR level descriptions"""
    return {
        "A1": "Beginner",
        "A2": "Elementary",
        "B1": "Intermediate",
        "B2": "Upper-Intermediate",
        "C1": "Advanced"
    }

@router.get("/stories", response_model=List[DesiStoryDB])
def get_stories(
    skip: int = 0,
    limit: int = 50,
    target_language: str = None,
    cefr_level: str = None,
    is_custom: bool = None,
    db: Session = Depends(get_db)
):
    """Get stories from database with optional filters"""
    try:
        stories = get_desi_stories(
            db=db,
            skip=skip,
            limit=limit,
            target_language=target_language,
            cefr_level=cefr_level,
            is_custom=is_custom
        )
        return stories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stories/statistics")
def get_stories_statistics(db: Session = Depends(get_db)):
    """Get statistics about generated stories"""
    try:
        stats = get_story_statistics(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stories/{story_id}", response_model=StoryResponse)
def get_story_by_id(story_id: int, db: Session = Depends(get_db)):
    """Get a specific story by ID"""
    try:
        from app.api.story_crud import get_desi_story
        story = get_desi_story(db, story_id)
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        
        return convert_db_story_to_response_format(story)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))