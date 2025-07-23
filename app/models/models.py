from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class DesiLesson(Base):
    __tablename__ = "desi_lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    target_language = Column(String, nullable=False)
    theme = Column(String, nullable=False)
    lesson_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vocabulary = relationship("DesiVocabulary", back_populates="lesson", cascade="all, delete-orphan")
    example_sentences = relationship("DesiExampleSentence", back_populates="lesson", cascade="all, delete-orphan")
    short_story = relationship("DesiShortStory", back_populates="lesson", uselist=False, cascade="all, delete-orphan")
    quiz_questions = relationship("DesiQuizQuestion", back_populates="lesson", cascade="all, delete-orphan")

class DesiVocabulary(Base):
    __tablename__ = "desi_vocabulary"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("desi_lessons.id"))
    english = Column(String, nullable=False)
    target_language_script = Column(String, nullable=False)
    transliteration = Column(String, nullable=False)
    pronunciation = Column(String, nullable=False)
    
    lesson = relationship("DesiLesson", back_populates="vocabulary")

class DesiExampleSentence(Base):
    __tablename__ = "desi_example_sentences"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("desi_lessons.id"))
    english = Column(Text, nullable=False)
    target_language_script = Column(Text, nullable=False)
    transliteration = Column(Text, nullable=False)
    pronunciation = Column(Text, nullable=False)
    
    lesson = relationship("DesiLesson", back_populates="example_sentences")

class DesiShortStory(Base):
    __tablename__ = "desi_short_stories"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("desi_lessons.id"))
    title = Column(String, nullable=False)
    
    lesson = relationship("DesiLesson", back_populates="short_story")
    dialogue = relationship("DesiDialogue", back_populates="short_story", cascade="all, delete-orphan")

class DesiDialogue(Base):
    __tablename__ = "desi_dialogue"
    
    id = Column(Integer, primary_key=True, index=True)
    short_story_id = Column(Integer, ForeignKey("desi_short_stories.id"))
    speaker = Column(String, nullable=False)
    target_language_script = Column(Text, nullable=False)
    transliteration = Column(Text, nullable=False)
    english = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    
    short_story = relationship("DesiShortStory", back_populates="dialogue")

class DesiQuizQuestion(Base):
    __tablename__ = "desi_quiz_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("desi_lessons.id"))
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    answer = Column(String, nullable=False)
    
    lesson = relationship("DesiLesson", back_populates="quiz_questions")