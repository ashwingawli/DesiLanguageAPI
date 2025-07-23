# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a language learning project focused on South Asian (Desi) languages. The repository contains structured lesson templates and schemas for creating personalized language learning content.

## Project Structure

- `Gemini_prompt.txt` - Core prompt template for generating language lessons
- `Lesson_schema.json` - JSON schema defining the structure of language lessons 
- `Lesson_topics.txt` - List of 25 progressive lesson topics from basic greetings to intermediate grammar

## Lesson Schema Architecture

The project uses a strict JSON schema validation for lesson content with these key components:

### Lesson Structure
- **Title**: Format "Lesson X: [Topic]" 
- **Target Language**: Name of the language being taught
- **Theme**: Specific topic focus (e.g., greetings, numbers)
- **Vocabulary**: Exactly 10 words with English, target script, transliteration, and pronunciation
- **Example Sentences**: Exactly 5 sentences with full translations and transliterations
- **Short Story**: Dialogue format with multiple speakers
- **Quiz**: Exactly 4 multiple choice questions

### Key Requirements
- All content must include transliteration using English phonetics
- Focus is on spoken language, not reading/writing the target script
- Progressive difficulty across 25 predefined topics
- Structured for complete beginners who only read English

## Development Commands

### Setup and Installation
```bash
pip install -r requirements.txt
cp .env.example .env  # Configure DB_URL and GEMINI_API_KEY
```

### Database Operations
```bash
alembic revision --autogenerate -m "Migration message"
alembic upgrade head
```

### Running the Application
```bash
python run.py  # Development server with reload
uvicorn app.main:app --host 0.0.0.0 --port 8000  # Production
```

## FastAPI Architecture

The application follows a layered architecture:

### Core Components
- **app/main.py** - FastAPI application and route definitions
- **app/models.py** - SQLAlchemy database models for lessons, vocabulary, examples, stories, and quizzes
- **app/schemas.py** - Pydantic models for request/response validation
- **app/database.py** - Database connection and session management
- **app/crud.py** - Database operations for lesson creation and retrieval
- **app/gemini_service.py** - Gemini AI integration for lesson generation
- **app/config.py** - Environment configuration management

### Database Schema
- Normalized design with separate tables for vocabulary, example sentences, short stories, dialogue, and quiz questions
- Each lesson links to its components via foreign keys
- JSON schema validation ensures structured lesson content

### API Endpoints
- Lesson generation with custom or random topics
- Lesson storage and retrieval by ID, language, or all lessons
- Topic management from the predefined lesson topics list

## Development Notes

When modifying the system:
- Update `Lesson_schema.json` for content structure changes
- Modify `Gemini_prompt.txt` for AI prompt improvements  
- Add topics to `Lesson_topics.txt` for new lesson themes
- Use Alembic migrations for database schema changes