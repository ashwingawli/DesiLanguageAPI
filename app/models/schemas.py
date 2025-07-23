from pydantic import BaseModel
from typing import List
from datetime import datetime

class DesiVocabularyItem(BaseModel):
    english: str
    target_language_script: str
    transliteration: str
    pronunciation: str

class DesiExampleSentence(BaseModel):
    english: str
    target_language_script: str
    transliteration: str
    pronunciation: str

class DesiDialogueItem(BaseModel):
    speaker: str
    target_language_script: str
    transliteration: str
    english: str

class DesiShortStory(BaseModel):
    title: str
    dialogue: List[DesiDialogueItem]

class DesiQuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str

class DesiLessonContent(BaseModel):
    title: str
    target_language: str
    theme: str
    vocabulary: List[DesiVocabularyItem]
    example_sentences: List[DesiExampleSentence]
    short_story: DesiShortStory
    quiz: List[DesiQuizQuestion]

class DesiLessonResponse(BaseModel):
    desi_lesson: DesiLessonContent

class DesiLessonRequest(BaseModel):
    target_language: str
    lesson_topic: str

class DesiLessonDB(BaseModel):
    id: int
    title: str
    target_language: str
    theme: str
    lesson_number: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DesiLessonFromDB(BaseModel):
    """Schema for lesson with complete content from database"""
    id: int
    title: str
    target_language: str
    theme: str
    lesson_number: int
    created_at: datetime
    vocabulary: List[DesiVocabularyItem]
    example_sentences: List[DesiExampleSentence]
    short_story: DesiShortStory
    quiz: List[DesiQuizQuestion]
    
    class Config:
        from_attributes = True