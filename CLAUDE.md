# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a language learning project focused on South Asian (Desi) languages with a FastAPI backend supporting structured lesson generation using Google Gemini AI.

## Project Architecture

This repository contains a FastAPI backend implementation:

### FastAPI Backend (Python/SQLAlchemy)
- `app/main.py` - FastAPI application entry point
- `app/api/crud.py` - Database CRUD operations using SQLAlchemy
- `app/models/` - Database models and Pydantic schemas
- `app/services/` - Business logic (Gemini AI integration, lesson parsing)
- `app/utils/` - Configuration and database utilities
- `alembic/` - Database migration management
- Uses PostgreSQL with SQLAlchemy ORM

### Core Files
- `Gemini_prompt.txt` - AI prompt template for lesson generation
- `Lesson_schema.json` - JSON schema defining lesson structure
- `lesson-resources/` - Lesson content and resources
  - `Lessons_title.txt` - Lesson titles and metadata
  - `Lessons_titletodo.txt` - Lesson planning todos
  - `Sections_Lessons.txt` - Lesson sections and structure
  - `Lessons_upload/` - Lesson upload files and batches
  - `temp/` - Temporary lesson files and backups

## Lesson Schema Architecture

The project uses a strict JSON schema validation for lesson content with these key components:

### Lesson Structure
- **Title**: Format "Lesson X: [Topic]" 
- **Target Language**: Name of the language being taught
- **Theme**: Specific topic focus (e.g., greetings, numbers)
- **Vocabulary**: Exactly 10 words with English, target script, transliteration, and pronunciation
- **Example Sentences**: Exactly 5 sentences with full translations and transliterations
- **Short Story**: Dialogue format with multiple speakers
- **Quiz**: Exactly 5 multiple choice questions

### Key Requirements
- All content must include transliteration using English phonetics
- Focus is on spoken language, not reading/writing the target script
- Progressive difficulty across 25 predefined topics
- Structured for complete beginners who only read English

## Development Commands

### FastAPI Backend
```bash
# Setup
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Environment setup
cp .env.example .env  # Configure DB_URL and GEMINI_API_KEY

# Database operations
alembic revision --autogenerate -m "Description"  # Create migration
alembic upgrade head                               # Apply migrations
alembic history                                   # View migration history

# Run application (IMPORTANT: Always activate virtual environment first)
source venv/bin/activate       # REQUIRED: Activate virtual environment 
python run.py                  # Development server (port 8000)
uvicorn app.main:app --reload  # Alternative run method

# Testing
bash scripts/test_api_simple.sh       # Simple API tests
bash scripts/test_api_curl.sh         # Full curl-based tests
python -m pytest tests/               # Python unit tests
```

## Backend Architecture

### FastAPI Backend Architecture
- **CORS Configuration**: Pre-configured for local development ports (3000, 5173-5175)
- **Database**: SQLAlchemy models with normalized schema for lessons, vocabulary, sentences, stories, dialogue, and quiz questions
- **AI Integration**: Google Gemini AI service for lesson generation
- **Validation**: JSON schema validation for lesson structure
- **Endpoints**: REST API with comprehensive lesson CRUD operations

### API Endpoints
- `POST /generate-desi-lesson` - Generate lessons with custom topics
- `POST /generate-random-desi-lesson` - Generate lessons with random topics
- `GET /get-or-generate-desi-lesson` - Get existing or generate new lessons
- `GET /desi-lessons` - Retrieve all lessons or by ID/language
- `GET /desi-lesson-topics` - Get available lesson topics
- `GET /desi-lessons-with-themes` - Get lessons grouped by themes
- `GET /random-desi-topic` - Get random topic for lesson generation

### Database Schema Design
The application uses a normalized schema with proper cascade deletion:
- **desi_lessons** - Main lesson metadata (title, language, theme, lesson_number)
- **desi_vocabulary** - 10 vocabulary items per lesson with English, target script, transliteration, pronunciation
- **desi_example_sentences** - 5 example sentences per lesson with full translations
- **desi_short_stories** - Story metadata with title and theme
- **desi_dialogue** - Story dialogue content with speaker attribution and order
- **desi_quiz_questions** - 5 multiple choice questions with JSON options array

**Cascade Deletion**: All child tables (vocabulary, sentences, stories, dialogue, quiz questions) are configured with CASCADE foreign key constraints. Deleting a lesson automatically removes all associated records, ensuring data integrity and preventing orphaned records.

## Frontend Application

The project includes a single comprehensive frontend implementation:

### Replit Demo App (`frontend/replt-app/`)
- Full-stack demo application with integrated backend
- Modern React 18+ with TypeScript and Tailwind CSS
- **TTS Integration**: Both Web Speech API and Google Cloud TTS support
- **Components**: Complete UI with shadcn/ui components for lesson viewing, quiz interface, language selection
- **Features**: Lesson progress tracking, audio playbook for pronunciation, comprehensive lesson management
- **Setup**: `npm install && npm run dev` (full development environment ready for deployment)

## Testing Infrastructure

### Comprehensive Test Scripts
- **Language-specific testing**: Dedicated test scripts for Telugu, Kannada, Hindi
- **Automated result collection**: Test results stored in `data/test-results/` with success/failure tracking
- **Performance monitoring**: API response time tracking and timeout handling
- **Database verification**: Automated checks for lesson storage and retrieval

### Test Result Analysis
- Success rate calculation and reporting
- Failed lesson analysis with error categorization
- Database state verification after test runs
- Generated test summaries for each language and test run

## Project Structure

```
DesiLanguage/
├── README.md                    # Main project documentation
├── CLAUDE.md                    # Claude Code instructions
├── requirements.txt             # Python dependencies
├── run.py                      # FastAPI application runner
├── Gemini_prompt.txt           # AI prompt template
├── Lesson_schema.json          # Lesson structure schema
├── openapi_schema.json         # Generated API schema
├── 
├── lesson-resources/           # Lesson content and planning
│   ├── Lessons_title.txt       # Lesson titles and metadata
│   ├── Lessons_titletodo.txt   # Lesson planning todos
│   ├── Sections_Lessons.txt    # Lesson sections structure
│   ├── Lessons_upload/         # Lesson upload batches
│   └── temp/                   # Temporary and backup files
├── 
├── config/                     # Configuration files
│   ├── alembic.ini            # Alembic migration config
│   └── google_tts.json        # Google TTS configuration
├── 
├── assets/                     # Static assets
│   └── images/                # Application images
├── 
├── app/                        # FastAPI backend (primary)
│   ├── main.py                # Application entry point
│   ├── api/                   # API endpoints
│   ├── models/                # Database models and schemas
│   ├── services/              # Business logic
│   ├── auth/                  # Authentication system
│   ├── utils/                 # Utilities and configuration
│   └── tests/                 # Unit and integration tests
├── 
├── frontend/replt-app/         # Frontend application
│   ├── client/                # React TypeScript frontend
│   ├── server/                # Backend integration
│   └── shared/                # Shared types and schemas
├── 
├── data/                       # Data storage and analysis
│   ├── lessons/               # Generated lesson files
│   ├── test-results/          # Test execution results
│   └── logs/                  # Application logs
├── 
├── docs/                       # Project documentation
│   ├── API_DOCUMENTATION.md   # API reference
│   ├── PROJECT_STRUCTURE.md   # Architecture details
│   └── README_TESTING.md      # Testing guidelines
├── 
├── scripts/                    # Utility and maintenance scripts
│   ├── test_api_curl.sh       # API testing scripts
│   ├── generate_all_lessons.py # Lesson generation utilities
│   └── create_test_users.py   # User management scripts
├── 
├── alembic/                    # Database migration management
│   ├── env.py                 # Migration environment
│   └── versions/              # Migration files
├── 
└── tests/                      # Global test suite
    ├── data/                  # Test data and results
    └── test_telugu_lessons.py # Language-specific tests
```

## Development Notes

### System Modification Guidelines
- **Schema changes**: Update both `Lesson_schema.json` and database models
- **AI improvements**: Modify `Gemini_prompt.txt` for lesson generation enhancements
- **New languages**: Add topics to `Lesson_topics.txt` and test with language-specific scripts
- **Database migrations**: Use `alembic revision --autogenerate` and `alembic upgrade head`
- **Testing**: Run appropriate test scripts after changes and verify success rates

### Environment Configuration
The backend requires:
- **DATABASE_URL**: PostgreSQL connection string
- **GEMINI_API_KEY**: Google Gemini AI API key for lesson generation
- **CORS origins**: Pre-configured for common development ports

### Key Architecture Decisions
- **Single backend approach**: Uses Python/FastAPI for robust API development
- **Normalized database**: Separate tables for lesson components enable efficient querying and updates
- **Progressive complexity**: 25 lesson topics designed for beginner to intermediate language learners
- **Transliteration focus**: Emphasizes spoken language learning for English-only readers

### Admin Lesson Access
**Prerequisite Bypass**: Admin users can launch any lesson without completing previous lessons. This functionality includes:

- **Backend Logic**: `user.role === 'admin'` bypasses the `isLocked` lesson restriction logic
- **Admin Dashboard**: Green "Launch Lesson" button (🎮) allows direct access to any lesson from the lesson management page
- **Lessons Page**: 
  - Locked lessons show "Admin Access" badge for admin users
  - Locked lesson buttons change from "Locked" to "Launch (Admin)" for admins
  - Admin users can click through to access any lesson regardless of progression
- **Navigation**: Lessons launch using `/learn/{language}/{encodedTopic}` URL pattern
- **Visual Indicators**: Admin-specific UI elements clearly distinguish admin capabilities from regular user restrictions

This feature enables content administrators to review, test, and demonstrate any lesson without progressing through the curriculum sequentially.