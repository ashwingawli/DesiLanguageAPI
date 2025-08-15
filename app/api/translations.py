from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.utils.database import get_db
from app.auth.dependencies import get_current_user
from app.models import models, schemas

router = APIRouter(prefix="/translations", tags=["translations"])

@router.post("/", response_model=schemas.UserTranslationResponse)
async def save_translation(
    translation: schemas.UserTranslationCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a translation to user's history
    """
    try:
        # Create new translation record
        db_translation = models.UserTranslation(
            user_id=current_user.id,
            from_text=translation.from_text,
            to_text=translation.to_text,
            to_text_transliteration=translation.to_text_transliteration,
            from_language=translation.from_language,
            to_language=translation.to_language,
            from_language_name=translation.from_language_name,
            to_language_name=translation.to_language_name,
            created_at=datetime.utcnow()
        )
        
        db.add(db_translation)
        db.commit()
        db.refresh(db_translation)
        
        
        return schemas.UserTranslationResponse(
            id=db_translation.id,
            from_text=db_translation.from_text,
            to_text=db_translation.to_text,
            to_text_transliteration=db_translation.to_text_transliteration,
            from_language=db_translation.from_language,
            to_language=db_translation.to_language,
            from_language_name=db_translation.from_language_name,
            to_language_name=db_translation.to_language_name,
            created_at=db_translation.created_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save translation")

@router.get("/", response_model=List[schemas.UserTranslationResponse])
async def get_user_translations(
    skip: int = 0,
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's translation history with pagination
    """
    try:
        translations = db.query(models.UserTranslation)\
            .filter(models.UserTranslation.user_id == current_user.id)\
            .order_by(models.UserTranslation.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return [
            schemas.UserTranslationResponse(
                id=t.id,
                from_text=t.from_text,
                to_text=t.to_text,
                to_text_transliteration=t.to_text_transliteration,
                from_language=t.from_language,
                to_language=t.to_language,
                from_language_name=t.from_language_name,
                to_language_name=t.to_language_name,
                created_at=t.created_at
            )
            for t in translations
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve translations")

@router.delete("/{translation_id}")
async def delete_translation(
    translation_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific translation from user's history
    """
    try:
        translation = db.query(models.UserTranslation)\
            .filter(
                models.UserTranslation.id == translation_id,
                models.UserTranslation.user_id == current_user.id
            )\
            .first()
        
        if not translation:
            raise HTTPException(status_code=404, detail="Translation not found")
        
        db.delete(translation)
        db.commit()
        
        return {"message": "Translation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete translation")

@router.delete("/")
async def clear_translation_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear all translations for the current user
    """
    try:
        deleted_count = db.query(models.UserTranslation)\
            .filter(models.UserTranslation.user_id == current_user.id)\
            .delete()
        
        db.commit()
        
        return {"message": f"Cleared {deleted_count} translations from history"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to clear translation history")

@router.get("/stats")
async def get_translation_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get translation statistics for the current user
    """
    try:
        total_translations = db.query(models.UserTranslation)\
            .filter(models.UserTranslation.user_id == current_user.id)\
            .count()
        
        # Get unique language pairs
        language_pairs = db.query(
            models.UserTranslation.from_language,
            models.UserTranslation.to_language
        )\
            .filter(models.UserTranslation.user_id == current_user.id)\
            .distinct()\
            .all()
        
        unique_pairs = len(language_pairs)
        
        # Get most recent translation
        recent_translation = db.query(models.UserTranslation)\
            .filter(models.UserTranslation.user_id == current_user.id)\
            .order_by(models.UserTranslation.created_at.desc())\
            .first()
        
        return {
            "total_translations": total_translations,
            "unique_language_pairs": unique_pairs,
            "most_recent_translation": recent_translation.created_at if recent_translation else None,
            "language_pairs": [
                {"from": pair[0], "to": pair[1]} 
                for pair in language_pairs
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve translation statistics")