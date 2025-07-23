# DesiLanguage API - South Asian Language Learning Backend

A FastAPI-based backend service for generating structured language lessons for South Asian (Desi) languages using Google's Gemini AI. This API provides comprehensive endpoints for lesson generation, storage, and retrieval with a focus on progressive language learning.

## 🌟 Features

- **AI-Powered Lesson Generation**: Uses Google's Gemini AI to create structured language lessons
- **RESTful API**: Well-documented FastAPI backend with OpenAPI specification
- **Comprehensive Database**: PostgreSQL-backed storage for lessons, vocabulary, and quiz content
- **Progressive Learning**: 25 structured lesson topics from basic greetings to intermediate grammar
- **Multi-Language Support**: Designed for various South Asian languages (Telugu, Kannada, etc.)
- **Structured Content**: Each lesson includes vocabulary, examples, stories, and quizzes
- **Schema Validation**: JSON schema validation ensures consistent lesson structure

## 🏗️ Project Structure

```
├── app/                    # FastAPI application
│   ├── api/               # API endpoints and CRUD operations
│   │   └── crud.py        # Database operations
│   ├── models/            # Database models and Pydantic schemas
│   │   ├── models.py      # SQLAlchemy database models
│   │   └── schemas.py     # Pydantic response/request schemas
│   ├── services/          # Business logic and external services
│   │   ├── gemini_service.py    # Google Gemini AI integration
│   │   └── lesson_parser.py     # Lesson topic parsing utilities
│   ├── utils/             # Utilities and configuration
│   │   ├── config.py      # Environment configuration
│   │   └── database.py    # Database connection management
│   └── main.py           # FastAPI application entry point
├── alembic/              # Database migration files
├── config/               # Configuration files
│   └── alembic.ini       # Alembic configuration
├── data/                 # Data files and storage
│   ├── lessons/          # Sample lesson JSON files
│   └── test-results/     # API test results and summaries
├── docs/                 # Project documentation
├── tests/                # Test files and test data
├── scripts/              # Utility scripts for testing
├── Gemini_prompt.txt     # AI prompt template for lesson generation
├── Lesson_schema.json    # JSON schema defining lesson structure
├── Lesson_topics.txt     # List of 25 progressive lesson topics
└── run.py                # Development server entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Google Gemini API key

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd DesiLanguage
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and Gemini API key
   ```
   
   Required environment variables:
   ```env
   DB_URL=postgresql://user:password@host:port/database
   GEMINI_API_KEY=your_google_gemini_api_key
   ```

5. **Database setup**:
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

6. **Run the application**:
   ```bash
   python run.py
   ```

   The API will be available at `http://localhost:8000`

## 📚 API Endpoints

### Core Endpoints

- **`GET /`** - API health check
- **`POST /generate-desi-lesson`** - Generate a new lesson for specified language and topic
- **`GET /desi-lesson-topics`** - Retrieve all available lesson topics
- **`GET /random-desi-topic`** - Get a random lesson topic
- **`POST /generate-random-desi-lesson`** - Generate lesson with random topic
- **`GET /desi-lessons`** - List all stored lessons with pagination
- **`GET /desi-lessons/{lesson_id}`** - Retrieve specific lesson by ID
- **`GET /desi-lessons/language/{target_language}`** - Get lessons filtered by language
- **`GET /get-or-generate-desi-lesson`** - Smart endpoint that returns existing lesson or generates new one
- **`GET /desi-lessons-with-themes`** - Get all lesson titles and themes

### Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🗄️ Database Schema

The application uses PostgreSQL with normalized tables:

- **`desi_lessons`** - Main lesson metadata (title, language, theme)
- **`desi_vocabulary`** - Vocabulary items with translations and pronunciation
- **`desi_example_sentences`** - Example sentences with full translations
- **`desi_short_stories`** - Story metadata and themes
- **`desi_dialogue`** - Story dialogue content with speaker attribution
- **`desi_quiz_questions`** - Multiple choice questions with answers

## 📖 Lesson Structure

Each lesson follows a structured format defined in `Lesson_schema.json`:

```json
{
  "title": "Lesson 1: Greetings and Introductions",
  "target_language": "Telugu",
  "theme": "Basic social interactions",
  "vocabulary": [
    {
      "english": "Hello",
      "target_script": "హలో",
      "transliteration": "halo",
      "pronunciation": "ha-lo"
    }
    // ... 9 more vocabulary items
  ],
  "example_sentences": [
    {
      "english": "Hello, how are you?",
      "target_script": "హలో, మీరు ఎలా ఉన్నారు?",
      "transliteration": "halo, meeru ela unnaru?",
      "pronunciation": "ha-lo, mee-ru eh-la un-na-ru?"
    }
    // ... 4 more example sentences
  ],
  "short_story": {
    "title": "Meeting a New Friend",
    "theme": "First meeting conversation",
    "dialogue": [/* Story dialogue */]
  },
  "quiz": [
    {
      "question": "How do you say 'Hello' in Telugu?",
      "options": ["హలో", "వందనములు", "నమస్కారం", "గుడ్ మార్నింగ్"],
      "correct_answer": "హలో"
    }
    // ... 3 more quiz questions
  ]
}
```

## 🧪 Testing

Run the test suite:
```bash
# Python tests
python -m pytest tests/

# API integration tests
bash scripts/test_api_simple.sh

# Full API testing with curl
bash scripts/test_api_curl.sh
```

Test results are automatically stored in `tests/data/` for analysis.

## 🛠️ Development

### Adding New Languages

1. Update lesson topics in `Lesson_topics.txt`
2. Modify the Gemini prompt template in `Gemini_prompt.txt`
3. Test lesson generation with the new language

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# View migration history
alembic history
```

### Code Style

The project follows Python PEP 8 standards. Use:
```bash
# Format code
black app/
flake8 app/
```

## 📋 Configuration

### Environment Variables

The application uses the following environment variables (configure in `.env`):

- `DB_URL`: PostgreSQL database connection string
- `GEMINI_API_KEY`: Google Gemini API key for lesson generation

### Lesson Topics

The system includes 25 progressive lesson topics defined in `Lesson_topics.txt`:

1. Greetings and Introductions
2. Essential Survival Phrases
3. Numbers (1-10)
4. Basic Verbs (To Be and Common Actions)
5. Common Nouns (People, Places)
... and 20 more topics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Documentation

- [API Documentation](docs/API_DOCUMENTATION.md)
- [Testing Guide](docs/README_TESTING.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `docs/` folder
- Review test results in `tests/data/` for debugging

---

**Built with ❤️ for South Asian language learners**