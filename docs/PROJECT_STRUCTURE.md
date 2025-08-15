# Project Structure

This document outlines the organized structure of the DesiLanguage project.

## Root Directory Structure

```
/
├── app/                    # Backend FastAPI application
│   ├── api/               # API endpoints and CRUD operations
│   ├── models/            # Database models and Pydantic schemas
│   ├── services/          # Business logic and external services
│   ├── utils/             # Utilities (config, database connection)
│   └── main.py           # FastAPI application entry point
├── alembic/              # Database migration files
├── config/               # Configuration files
│   └── alembic.ini       # Alembic configuration
├── data/                 # Data files and storage
│   ├── lessons/          # Individual lesson JSON files
│   └── test-results/     # API test results and summaries
├── docs/                 # Project documentation
│   ├── API_DOCUMENTATION.md
│   ├── README_TESTING.md
│   └── PROJECT_STRUCTURE.md (this file)
├── frontend/             # Frontend applications
│   └── replt-app/        # React frontend application with TTS integration
├── scripts/              # Utility and test scripts
│   ├── test_api_curl.sh
│   └── test_api_simple.sh
├── tests/                # Test files and data
│   ├── data/             # Test result data
│   ├── integration/      # Integration tests
│   ├── unit/             # Unit tests
│   └── test_telugu_lessons.py
├── venv/                 # Python virtual environment (excluded from git)
├── CLAUDE.md             # Claude Code project instructions
├── Gemini_prompt.txt     # AI prompt template
├── Lesson_schema.json    # JSON schema for lessons
├── Lesson_topics.txt     # List of lesson topics
├── Lessons_n_themes.txt  # Additional lesson themes
├── README.md             # Main project documentation
├── openapi_schema.json   # OpenAPI specification
├── requirements.txt      # Python dependencies
└── run.py                # Development server entry point
```

## Backend Application Structure (`app/`)

- **api/**: Contains CRUD operations and API endpoint logic
- **models/**: Database models (SQLAlchemy) and Pydantic schemas for validation
- **services/**: Business logic, Gemini AI integration, and lesson parsing
- **utils/**: Configuration management and database connection utilities
- **main.py**: FastAPI application setup and route definitions

## Frontend Structure (`frontend/`)

- **replt-app/**: React-based frontend with TypeScript and TTS integration

## Data Organization (`data/`)

- **lessons/**: Individual lesson JSON files for different languages
- **test-results/**: API test results organized by language and test runs

## Testing Structure (`tests/`)

- **data/**: Test result data and summaries
- **integration/**: Integration test files
- **unit/**: Unit test files
- **test_telugu_lessons.py**: Language-specific test suite

## Configuration Files

- **config/alembic.ini**: Database migration configuration
- **requirements.txt**: Python package dependencies
- **openapi_schema.json**: API documentation schema
- **Lesson_schema.json**: JSON schema for lesson structure validation

## Development Files

- **run.py**: Development server launcher
- **scripts/**: Shell scripts for API testing and automation
- **CLAUDE.md**: Instructions for Claude Code development assistance
- **.gitignore**: Git ignore rules (excludes venv/, .env, __pycache__, etc.)

## Excluded from Version Control

The following directories/files are excluded via `.gitignore`:
- `venv/` - Python virtual environment
- `.env` - Environment variables with API keys
- `__pycache__/` - Python bytecode cache
- `node_modules/` - Node.js dependencies
- Database files (*.db, *.sqlite)
- IDE configuration files