from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

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
    difficulty: str
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
    difficulty: str
    lesson_number: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DesiLessonFromDB(BaseModel):
    """Schema for lesson with complete content from database"""
    id: int
    title: str
    target_language: str
    difficulty: str
    lesson_number: int
    created_at: datetime
    vocabulary: List[DesiVocabularyItem]
    example_sentences: List[DesiExampleSentence]
    short_story: DesiShortStory
    quiz: List[DesiQuizQuestion]
    
    class Config:
        from_attributes = True


# Story module schemas
class CEFRLevel(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"

class Language(str, Enum):
    Arabic = "Arabic"
    Assamese = "Assamese"
    Bengali = "Bengali"
    Dutch = "Dutch"
    French = "French"
    German = "German"
    Gujarati = "Gujarati"
    Hindi = "Hindi"
    Italian = "Italian"
    Japanese = "Japanese"
    Kannada = "Kannada"
    Korean = "Korean"
    Malayalam = "Malayalam"
    Mandarin = "Mandarin Chinese"
    Marathi = "Marathi"
    Odia = "Odia"
    Polish = "Polish"
    Portuguese = "Portuguese"
    Punjabi = "Punjabi"
    Russian = "Russian"
    Spanish = "Spanish"
    Tamil = "Tamil"
    Telugu = "Telugu"
    Thai = "Thai"
    Urdu = "Urdu"
    Vietnamese = "Vietnamese"

class VocabularyWord(BaseModel):
    word: str
    definition: Optional[str] = None
    transliteration: Optional[str] = None

class StoryData(BaseModel):
    story: str
    translation: str
    transliteration: Optional[str] = None
    vocabulary: List[VocabularyWord]

class StoryGenerationRequest(BaseModel):
    level: CEFRLevel
    language: Language
    scenario: Optional[str] = None

class StoryResponse(BaseModel):
    story_data: StoryData
    target_language: Language
    level: CEFRLevel

# Database story schemas
class DesiStoryVocabularyDB(BaseModel):
    id: int
    word: str
    definition: Optional[str] = None
    transliteration: Optional[str] = None
    order_index: int
    
    class Config:
        from_attributes = True

class DesiStoryDB(BaseModel):
    id: int
    title: Optional[str] = None
    target_language: str
    cefr_level: str
    scenario: Optional[str] = None
    english_text: str
    translated_text: str
    transliteration: Optional[str] = None
    generated_at: datetime
    user_id: Optional[int] = None
    is_custom: bool
    generation_prompt: Optional[str] = None
    vocabulary: List[DesiStoryVocabularyDB] = []
    
    class Config:
        from_attributes = True

class DesiStoryCreate(BaseModel):
    title: Optional[str] = None
    target_language: str
    cefr_level: str
    scenario: Optional[str] = None
    english_text: str
    translated_text: str
    transliteration: Optional[str] = None
    user_id: Optional[int] = None
    is_custom: bool = False
    generation_prompt: Optional[str] = None
    vocabulary: List[VocabularyWord] = []

# Translation schemas
class TranslationRequest(BaseModel):
    text: str
    from_language: str
    to_language: str

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    transliteration: Optional[str] = None
    from_language: str
    to_language: str

# User Translation History schemas
class UserTranslationCreate(BaseModel):
    from_text: str
    to_text: str
    to_text_transliteration: Optional[str] = None
    from_language: str
    to_language: str
    from_language_name: str
    to_language_name: str

class UserTranslationResponse(BaseModel):
    id: int
    from_text: str
    to_text: str
    to_text_transliteration: Optional[str] = None
    from_language: str
    to_language: str
    from_language_name: str
    to_language_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True