# DesiLanguage API - OpenAPI Documentation
Generated from FastAPI backend application

## API Information
- **Title**: DesiLanguage API
- **Description**: Language Learning Lesson Generator
- **Version**: 0.1.0
- **OpenAPI**: 3.1.0

## API Endpoints

### GET /
**Summary**: Read Root
Returns basic API information.

### POST /generate-desi-lesson
**Summary**: Generate Desi Lesson
Generates a new lesson using Gemini AI for the specified language and topic.

**Parameters**:
- `save_to_db` (query) - boolean - Optional (default: true)

**Request Body**: JSON object with DesiLessonRequest schema
```json
{
  "target_language": "string",
  "lesson_topic": "string"
}
```

### GET /get-or-generate-desi-lesson
**Summary**: Get Or Generate Desi Lesson
First checks database for existing lesson, generates new one if not found.

**Parameters**:
- `target_language` (query) - string - Required
- `lesson_topic` (query) - string - Required

### GET /desi-lessons-with-themes
**Summary**: Get Desi Lessons With Themes
Returns all available lesson topics and their themes from Lessons_n_themes.txt.

### GET /desi-lessons/language/{target_language}
**Summary**: Get Desi Lessons By Language
Returns all lessons for a specific language from the database.

**Parameters**:
- `target_language` (path) - string - Required

### GET /desi-lessons/{lesson_id}
**Summary**: Get Desi Lesson
Returns a specific lesson by ID from the database.

**Parameters**:
- `lesson_id` (path) - integer - Required

### GET /desi-lessons
**Summary**: Get Desi Lessons
Returns paginated list of all lessons in the database.

**Parameters**:
- `skip` (query) - integer - Optional (default: 0)
- `limit` (query) - integer - Optional (default: 100)

### GET /desi-lesson-topics
**Summary**: Get Desi Lesson Topics
Returns list of available lesson topics.

### POST /generate-random-desi-lesson
**Summary**: Generate Random Desi Lesson
Generates a lesson with a randomly selected topic.

**Parameters**:
- `target_language` (query) - string - Required
- `save_to_db` (query) - boolean - Optional (default: true)

### GET /random-desi-topic
**Summary**: Get Random Desi Topic
Returns a randomly selected lesson topic.

## Key Data Schemas

### DesiLessonRequest
**Properties**:
- `target_language`: string
- `lesson_topic`: string

### DesiLessonResponse
**Properties**:
- `desi_lesson`: DesiLessonContent

### DesiLessonContent
**Properties**:
- `title`: string
- `target_language`: string
- `theme`: string
- `vocabulary`: array of DesiVocabularyItem
- `example_sentences`: array of DesiExampleSentence
- `short_story`: DesiShortStory
- `quiz`: array of DesiQuizQuestion

### DesiVocabularyItem
**Properties**:
- `english`: string
- `target_language_script`: string
- `transliteration`: string
- `pronunciation`: string

### DesiExampleSentence
**Properties**:
- `english`: string
- `target_language_script`: string
- `transliteration`: string
- `pronunciation`: string

### DesiShortStory
**Properties**:
- `title`: string
- `dialogue`: array of DesiDialogueItem

### DesiDialogueItem
**Properties**:
- `speaker`: string
- `target_language_script`: string
- `transliteration`: string
- `english`: string

### DesiQuizQuestion
**Properties**:
- `question`: string
- `options`: array of strings
- `answer`: string

### DesiLessonDB
**Properties**:
- `id`: integer
- `title`: string
- `target_language`: string
- `theme`: string
- `lesson_number`: integer
- `created_at`: datetime

## Usage Examples

### Generate a New Lesson
```bash
curl -X POST "http://localhost:8000/generate-desi-lesson" \
  -H "Content-Type: application/json" \
  -d '{
    "target_language": "Hindi",
    "lesson_topic": "Greetings & Introductions"
  }'
```

### Get or Generate Lesson (Database First)
```bash
curl "http://localhost:8000/get-or-generate-desi-lesson?target_language=Tamil&lesson_topic=Numbers%201-10"
```

### Get Available Lesson Topics
```bash
curl "http://localhost:8000/desi-lessons-with-themes"
```

### Get Lessons by Language
```bash
curl "http://localhost:8000/desi-lessons/language/Hindi"
```

### Get Specific Lesson
```bash
curl "http://localhost:8000/desi-lessons/1"
```

## Authentication
Currently, no authentication is required for API access.

## Rate Limiting
No rate limiting is currently implemented.

## CORS
CORS is enabled for:
- http://localhost:3000
- http://127.0.0.1:3000

## Response Format
All responses are in JSON format. Error responses include a `detail` field with error information.

## Database
The API uses PostgreSQL database with the following main tables:
- `desi_lessons` - Main lesson metadata
- `desi_vocabulary` - Vocabulary items
- `desi_example_sentences` - Example sentences
- `desi_short_stories` - Story metadata
- `desi_dialogue` - Story dialogue lines  
- `desi_quiz_questions` - Quiz questions

## AI Integration
Lessons are generated using Google Gemini AI service based on predefined templates and themes.