from sqlalchemy.orm import Session, joinedload
from app.models import models, schemas
from typing import List, Optional

def create_desi_lesson(db: Session, lesson_data: schemas.DesiLessonResponse, difficulty: str = None) -> models.DesiLesson:
    lesson_content = lesson_data.desi_lesson
    
    # Calculate the next lesson number for this language
    max_lesson = db.query(models.DesiLesson).filter(
        models.DesiLesson.target_language == lesson_content.target_language
    ).order_by(models.DesiLesson.lesson_number.desc()).first()
    
    lesson_number = (max_lesson.lesson_number + 1) if max_lesson else 1
    
    # Use the original title from the lesson content
    lesson_title = lesson_content.title
    
    # Use provided difficulty or fall back to lesson difficulty
    final_difficulty = difficulty or lesson_content.difficulty
    
    db_lesson = models.DesiLesson(
        title=lesson_title,
        target_language=lesson_content.target_language,
        difficulty=final_difficulty,
        lesson_number=lesson_number
    )
    db.add(db_lesson)
    db.flush()
    
    for vocab_item in lesson_content.vocabulary:
        db_vocab = models.DesiVocabulary(
            lesson_id=db_lesson.id,
            english=vocab_item.english,
            target_language_script=vocab_item.target_language_script,
            transliteration=vocab_item.transliteration,
            pronunciation=vocab_item.pronunciation
        )
        db.add(db_vocab)
    
    for sentence in lesson_content.example_sentences:
        db_sentence = models.DesiExampleSentence(
            lesson_id=db_lesson.id,
            english=sentence.english,
            target_language_script=sentence.target_language_script,
            transliteration=sentence.transliteration,
            pronunciation=sentence.pronunciation
        )
        db.add(db_sentence)
    
    db_story = models.DesiShortStory(
        lesson_id=db_lesson.id,
        title=lesson_content.short_story.title
    )
    db.add(db_story)
    db.flush()
    
    for i, dialogue_item in enumerate(lesson_content.short_story.dialogue):
        db_dialogue = models.DesiDialogue(
            short_story_id=db_story.id,
            speaker=dialogue_item.speaker,
            target_language_script=dialogue_item.target_language_script,
            transliteration=dialogue_item.transliteration,
            english=dialogue_item.english,
            order_num=i
        )
        db.add(db_dialogue)
    
    for quiz_item in lesson_content.quiz:
        # PostgreSQL JSONB handles Python objects natively - no need for json.dumps
        db_quiz = models.DesiQuizQuestion(
            lesson_id=db_lesson.id,
            question=quiz_item.question,
            options=quiz_item.options,  # PostgreSQL JSONB handles list objects directly
            answer=quiz_item.answer
        )
        db.add(db_quiz)
    
    db.commit()
    db.refresh(db_lesson)
    return db_lesson

def get_desi_lesson(db: Session, lesson_id: int) -> Optional[models.DesiLesson]:
    return db.query(models.DesiLesson).filter(models.DesiLesson.id == lesson_id).first()

def get_desi_lessons(db: Session, skip: int = 0, limit: int = 100) -> List[models.DesiLesson]:
    return db.query(models.DesiLesson).offset(skip).limit(limit).all()

def get_desi_lessons_by_language(db: Session, target_language: str) -> List[models.DesiLesson]:
    return db.query(models.DesiLesson).filter(models.DesiLesson.target_language == target_language).all()

def get_desi_lesson_by_language_and_number(db: Session, target_language: str, lesson_number: int) -> Optional[models.DesiLesson]:
    """Get lesson by language and lesson number with all related content"""
    return db.query(models.DesiLesson).filter(
        models.DesiLesson.target_language == target_language,
        models.DesiLesson.lesson_number == lesson_number
    ).options(
        joinedload(models.DesiLesson.vocabulary),
        joinedload(models.DesiLesson.example_sentences),
        joinedload(models.DesiLesson.short_story).joinedload(models.DesiShortStory.dialogue),
        joinedload(models.DesiLesson.quiz_questions)
    ).first()

def get_desi_lesson_with_content(db: Session, lesson_id: int) -> Optional[models.DesiLesson]:
    """Get lesson with all related content (vocabulary, examples, story, quiz)"""
    return db.query(models.DesiLesson).filter(
        models.DesiLesson.id == lesson_id
    ).options(
        joinedload(models.DesiLesson.vocabulary),
        joinedload(models.DesiLesson.example_sentences),
        joinedload(models.DesiLesson.short_story).joinedload(models.DesiShortStory.dialogue),
        joinedload(models.DesiLesson.quiz_questions)
    ).first()

def find_desi_lesson_by_title_and_language(db: Session, title: str, target_language: str) -> Optional[models.DesiLesson]:
    """Find lesson by title and language, with full content"""
    return db.query(models.DesiLesson).filter(
        models.DesiLesson.target_language == target_language,
        models.DesiLesson.title.contains(title)
    ).options(
        joinedload(models.DesiLesson.vocabulary),
        joinedload(models.DesiLesson.example_sentences),
        joinedload(models.DesiLesson.short_story).joinedload(models.DesiShortStory.dialogue),
        joinedload(models.DesiLesson.quiz_questions)
    ).first()

def convert_db_lesson_to_response_format(db_lesson: models.DesiLesson) -> schemas.DesiLessonResponse:
    """Convert database lesson to the response format expected by frontend"""
    
    # Convert vocabulary
    vocabulary = [
        schemas.DesiVocabularyItem(
            english=vocab.english,
            target_language_script=vocab.target_language_script,
            transliteration=vocab.transliteration,
            pronunciation=vocab.pronunciation
        )
        for vocab in db_lesson.vocabulary
    ]
    
    # Convert example sentences  
    example_sentences = [
        schemas.DesiExampleSentence(
            english=sentence.english,
            target_language_script=sentence.target_language_script,
            transliteration=sentence.transliteration,
            pronunciation=sentence.pronunciation
        )
        for sentence in db_lesson.example_sentences
    ]
    
    # Convert story and dialogue
    dialogue = []
    if db_lesson.short_story and db_lesson.short_story.dialogue:
        dialogue = [
            schemas.DesiDialogueItem(
                speaker=d.speaker,
                target_language_script=d.target_language_script,
                transliteration=d.transliteration,
                english=d.english
            )
            for d in sorted(db_lesson.short_story.dialogue, key=lambda x: x.order_num)
        ]
    
    short_story = schemas.DesiShortStory(
        title=db_lesson.short_story.title if db_lesson.short_story else "",
        dialogue=dialogue
    )
    
    # Convert quiz questions
    quiz = [
        schemas.DesiQuizQuestion(
            question=q.question,
            options=q.options,
            answer=q.answer
        )
        for q in db_lesson.quiz_questions
    ]
    
    # Create lesson content
    lesson_content = schemas.DesiLessonContent(
        title=db_lesson.title,
        target_language=db_lesson.target_language,
        difficulty=db_lesson.difficulty,
        vocabulary=vocabulary,
        example_sentences=example_sentences,
        short_story=short_story,
        quiz=quiz
    )
    
    return schemas.DesiLessonResponse(desi_lesson=lesson_content)