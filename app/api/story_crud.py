from sqlalchemy.orm import Session, joinedload
from app.models import models, schemas
from typing import List, Optional
from datetime import datetime

def create_desi_story(
    db: Session, 
    story_data: schemas.StoryData, 
    target_language: str,
    cefr_level: str,
    scenario: Optional[str] = None,
    user_id: Optional[int] = None,
    generation_prompt: Optional[str] = None
) -> models.DesiStory:
    """Create a new story in the database"""
    
    # Create the main story record
    db_story = models.DesiStory(
        title=None,  # Stories don't have titles by default
        target_language=target_language,
        cefr_level=cefr_level,
        scenario=scenario,
        english_text=story_data.story,
        translated_text=story_data.translation,
        transliteration=story_data.transliteration,
        generated_at=datetime.utcnow(),
        user_id=user_id,
        is_custom=bool(scenario),
        generation_prompt=generation_prompt
    )
    
    db.add(db_story)
    db.flush()  # Get the story ID
    
    # Add vocabulary items
    for index, vocab_item in enumerate(story_data.vocabulary):
        db_vocab = models.DesiStoryVocabulary(
            story_id=db_story.id,
            word=vocab_item.word,
            definition=vocab_item.definition,
            transliteration=vocab_item.transliteration,
            order_index=index
        )
        db.add(db_vocab)
    
    db.commit()
    db.refresh(db_story)
    return db_story

def get_desi_story(db: Session, story_id: int) -> Optional[models.DesiStory]:
    """Get a story by ID with all related data"""
    return db.query(models.DesiStory).options(
        joinedload(models.DesiStory.vocabulary)
    ).filter(models.DesiStory.id == story_id).first()

def get_desi_stories(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None,
    target_language: Optional[str] = None,
    cefr_level: Optional[str] = None,
    is_custom: Optional[bool] = None
) -> List[models.DesiStory]:
    """Get stories with optional filters"""
    
    query = db.query(models.DesiStory).options(
        joinedload(models.DesiStory.vocabulary)
    )
    
    if user_id is not None:
        query = query.filter(models.DesiStory.user_id == user_id)
    
    if target_language:
        query = query.filter(models.DesiStory.target_language == target_language)
    
    if cefr_level:
        query = query.filter(models.DesiStory.cefr_level == cefr_level)
    
    if is_custom is not None:
        query = query.filter(models.DesiStory.is_custom == is_custom)
    
    return query.order_by(models.DesiStory.generated_at.desc()).offset(skip).limit(limit).all()

def get_stories_by_language(db: Session, target_language: str) -> List[models.DesiStory]:
    """Get all stories for a specific language"""
    return db.query(models.DesiStory).options(
        joinedload(models.DesiStory.vocabulary)
    ).filter(models.DesiStory.target_language == target_language).order_by(
        models.DesiStory.generated_at.desc()
    ).all()

def delete_desi_story(db: Session, story_id: int) -> bool:
    """Delete a story and its vocabulary"""
    story = db.query(models.DesiStory).filter(models.DesiStory.id == story_id).first()
    if story:
        db.delete(story)
        db.commit()
        return True
    return False

def convert_db_story_to_response_format(db_story: models.DesiStory) -> schemas.StoryResponse:
    """Convert database story to response format"""
    
    # Convert vocabulary
    vocabulary = [
        schemas.VocabularyWord(
            word=vocab.word,
            definition=vocab.definition,
            transliteration=vocab.transliteration
        )
        for vocab in sorted(db_story.vocabulary, key=lambda x: x.order_index)
    ]
    
    story_data = schemas.StoryData(
        story=db_story.english_text,
        translation=db_story.translated_text,
        transliteration=db_story.transliteration,
        vocabulary=vocabulary
    )
    
    return schemas.StoryResponse(
        story_data=story_data,
        target_language=schemas.Language(db_story.target_language),
        level=schemas.CEFRLevel(db_story.cefr_level)
    )

def find_similar_story(
    db: Session,
    target_language: str,
    cefr_level: str,
    scenario: Optional[str] = None
) -> Optional[models.DesiStory]:
    """Find a similar existing story to avoid duplicates"""
    
    query = db.query(models.DesiStory).filter(
        models.DesiStory.target_language == target_language,
        models.DesiStory.cefr_level == cefr_level
    )
    
    if scenario:
        query = query.filter(models.DesiStory.scenario == scenario)
    else:
        query = query.filter(models.DesiStory.scenario.is_(None))
    
    return query.first()

def get_story_statistics(db: Session) -> dict:
    """Get statistics about generated stories"""
    total_stories = db.query(models.DesiStory).count()
    custom_stories = db.query(models.DesiStory).filter(models.DesiStory.is_custom == True).count()
    random_stories = total_stories - custom_stories
    
    # Language distribution
    from sqlalchemy import func
    language_stats = db.query(
        models.DesiStory.target_language,
        func.count(models.DesiStory.id).label('count')
    ).group_by(models.DesiStory.target_language).all()
    
    # Level distribution
    level_stats = db.query(
        models.DesiStory.cefr_level,
        func.count(models.DesiStory.id).label('count')
    ).group_by(models.DesiStory.cefr_level).all()
    
    return {
        "total_stories": total_stories,
        "custom_stories": custom_stories,
        "random_stories": random_stories,
        "languages": {lang: count for lang, count in language_stats},
        "levels": {level: count for level, count in level_stats}
    }