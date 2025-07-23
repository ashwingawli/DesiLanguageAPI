# DesiLanguage API Testing Guide

## Customizable curl Test Script

The `test_api_simple.sh` script has been enhanced to work with any language.

### Usage

```bash
# Test with default language (Telugu)
./test_api_simple.sh

# Test with specific language
./test_api_simple.sh Kannada
./test_api_simple.sh Hindi
./test_api_simple.sh Tamil
./test_api_simple.sh Bengali
./test_api_simple.sh Marathi
```

### What the Script Does

1. **API Health Check** - Verifies the API is running
2. **Topic Retrieval** - Gets all 25 lesson topics
3. **Lesson Generation** - Creates lessons for each topic with proper numbering
4. **Database Storage** - Automatically stores successful lessons
5. **Results Organization** - Saves all results in language-specific directories

### Output Structure

```
api_test_results_[language]/
├── api_health.json
├── lesson_topics.json
├── lesson_XX_TOPIC_SUCCESS.json    # Successful lessons
├── lesson_XX_TOPIC_FAILED.json     # Failed lessons
├── test_summary.txt                 # Complete test summary
├── database_lessons.json           # All lessons in database
└── [language]_lessons_in_db.json   # Language-specific lessons
```

### Recent Test Results

## Telugu Language Test
- **Success Rate**: 32% (8/25 lessons)
- **Performance**: ~12-14 seconds per lesson
- **Issues**: Gemini occasionally returns null values

## Kannada Language Test  
- **Success Rate**: 60% (15/25 lessons)
- **Performance**: ~11-13 seconds per lesson
- **Improvement**: Better consistency than Telugu

### Key Features

✅ **Proper Lesson Numbering** - Sequential numbering per language (Lesson 1, 2, 3...)  
✅ **Database Integration** - Direct storage of successful lessons  
✅ **Error Handling** - Detailed error logs for failed generations  
✅ **Language Isolation** - Each language maintains separate lesson sequences  
✅ **Quality Content** - Generated lessons include script, transliteration, pronunciation  

### API Endpoints Tested

- `POST /generate-desi-lesson?save_to_db=true`
- `GET /desi-lesson-topics`
- `GET /desi-lessons`
- `GET /desi-lessons/language/{language}`

### Next Steps

- Test with other Indian languages (Hindi, Tamil, Bengali, etc.)
- Implement retry logic for failed lessons
- Add parallel processing for faster generation