import google.generativeai as genai
import json
import time
import random
import hashlib
from typing import Dict, List, Optional, Any
from app.utils.config import settings
from app.models.schemas import DesiLessonResponse, DesiLessonContent, DesiVocabularyItem, DesiExampleSentence, DesiShortStory, DesiDialogueItem, DesiQuizQuestion
from pydantic import BaseModel, Field


class VocabularyItem(BaseModel):
    word: str = Field(..., description="The vocabulary word in the target language")
    translation: str = Field(..., description="The English translation of the word")
    transliteration: str = Field(..., description="The phonetic transliteration of the word")


class SentenceItem(BaseModel):
    sentence: str = Field(..., description="The sentence in the target language")
    translation: str = Field(..., description="The English translation of the sentence")
    transliteration: str = Field(..., description="The phonetic transliteration of the sentence")


class ConversationLine(BaseModel):
    speaker: str = Field(..., description="The speaker's name")
    line: str = Field(..., description="The conversation line in the target language")
    translation: str = Field(..., description="The English translation of the line")
    transliteration: str = Field(..., description="The phonetic transliteration of the line")


class QuizQuestion(BaseModel):
    question: str = Field(..., description="The quiz question in English")
    options: List[str] = Field(..., description="Array of 4 possible answers")
    answer: str = Field(..., description="The correct answer from the options")


class EnhancedLearningData(BaseModel):
    vocabulary: List[VocabularyItem] = Field(..., min_items=12, max_items=12)
    sentences: List[SentenceItem] = Field(..., min_items=7, max_items=7)
    conversations: List[ConversationLine] = Field(..., min_items=9, max_items=9)
    quiz: List[QuizQuestion] = Field(..., min_items=5, max_items=5)


class EnhancedGeminiService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        
        # Configure model for better structured responses
        generation_config = genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=4000,  # Increased for more content
            top_p=0.9,
            top_k=40
        )
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp', generation_config=generation_config)
        self.max_retries = 3
        self.base_delay = 2
        
        # Cache for learning data
        self.learning_cache: Dict[str, EnhancedLearningData] = {}
        self.max_cache_size = 100

    def get_response_schema(self) -> Dict[str, Any]:
        """Get the structured response schema for Gemini API"""
        return {
            "type": "object",
            "properties": {
                "vocabulary": {
                    "type": "array",
                    "description": "A list of 12 vocabulary words related to the topic in the target language.",
                    "minItems": 12,
                    "maxItems": 12,
                    "items": {
                        "type": "object",
                        "required": ["word", "translation", "transliteration"],
                        "properties": {
                            "word": {"type": "string", "description": "The vocabulary word in the target language."},
                            "translation": {"type": "string", "description": "The English translation of the word."},
                            "transliteration": {"type": "string", "description": "The phonetic transliteration of the word."}
                        }
                    }
                },
                "sentences": {
                    "type": "array",
                    "description": "A list of 7 sample sentences using the provided vocabulary.",
                    "minItems": 7,
                    "maxItems": 7,
                    "items": {
                        "type": "object",
                        "required": ["sentence", "translation", "transliteration"],
                        "properties": {
                            "sentence": {"type": "string", "description": "The sentence in the target language."},
                            "translation": {"type": "string", "description": "The English translation of the sentence."},
                            "transliteration": {"type": "string", "description": "The phonetic transliteration of the sentence."}
                        }
                    }
                },
                "conversations": {
                    "type": "array",
                    "description": "A list of 9 conversation lines (a dialogue between two people with common Indian names) related to the vocabulary. Should not be simple repetitive sentences from the list above.",
                    "minItems": 9,
                    "maxItems": 9,
                    "items": {
                        "type": "object",
                        "required": ["speaker", "line", "translation", "transliteration"],
                        "properties": {
                            "speaker": {"type": "string", "description": "The speaker's name (e.g., 'Priya' or 'Rohan')."},
                            "line": {"type": "string", "description": "The conversation line in the target language."},
                            "translation": {"type": "string", "description": "The English translation of the line."},
                            "transliteration": {"type": "string", "description": "The phonetic transliteration of the line."}
                        }
                    }
                },
                "quiz": {
                    "type": "array",
                    "description": "A list of 5 multiple-choice quiz questions based on the content to test understanding. The questions and options must be in English or use transliteration for target language words, as the learner cannot read the target language script.",
                    "minItems": 5,
                    "maxItems": 5,
                    "items": {
                        "type": "object",
                        "required": ["question", "options", "answer"],
                        "properties": {
                            "question": {"type": "string", "description": "The quiz question, in English. It should test vocabulary or sentence understanding without using the target language's native script."},
                            "options": {
                                "type": "array",
                                "description": "An array of 4 possible answers. These should be in English or transliterated from the target language. Do not use the target language's native script.",
                                "minItems": 4,
                                "maxItems": 4,
                                "items": {"type": "string"}
                            },
                            "answer": {"type": "string", "description": "The correct answer from the options. Must exactly match one of the options."}
                        }
                    }
                }
            },
            "required": ["vocabulary", "sentences", "conversations", "quiz"]
        }

    async def fetch_learning_data(self, topic: str, language: str) -> EnhancedLearningData:
        """
        Generate enhanced learning data for a topic in the target language
        Equivalent to the TypeScript fetchLearningData function
        """
        # Randomly select names for variety
        male_names = ["Arjun", "Rohan", "Vikram", "Raj", "Amit", "Arun", "Karthik", "Nikhil", "Suresh", "Ravi"]
        female_names = ["Priya", "Anita", "Meera", "Kavitha", "Sunita", "Pooja", "Sneha", "Divya", "Nisha", "Geeta"]
        
        selected_male = random.choice(male_names)
        selected_female = random.choice(female_names)

        # Check cache with names included for uniqueness
        cache_key = self._get_cache_key(f"{topic}_{selected_male}_{selected_female}", language)
        if cache_key in self.learning_cache:
            return self.learning_cache[cache_key]

        prompt = f"""
Generate language learning materials for the topic "{topic}" in the language "{language}".
The output must be a JSON object that strictly follows the provided schema.
The materials must include:
1. Exactly 12 vocabulary words with English translations and transliterations.
2. Exactly 7 sample sentences using the vocabulary, with English translations and transliterations.
3. A conversation sample with exactly 9 turns/lines between two people with these specific Indian names: {selected_male} (male speaker) and {selected_female} (female speaker). The conversation should be related to the vocabulary, including English translations and transliterations. The sentences should be conversational and not just a list of examples.
4. A quiz with exactly 5 multiple-choice questions to test comprehension. IMPORTANT: The learner can only read English and transliterations, not the native script of the target language. Therefore, all quiz questions must be in English. Any words from the target language used in questions or options MUST be the transliteration. Do not use the native script of the target language in the quiz at all. Each question must have 4 options.

IMPORTANT FORMATTING RULES:
- "word" field must contain ONLY the word in native {language} script, no parentheses or transliterations mixed in
- "sentence" field must contain ONLY the sentence in native {language} script, no parentheses or transliterations mixed in  
- "line" field must contain ONLY the dialogue in native {language} script, no parentheses or transliterations mixed in
- "transliteration" field must contain ONLY the phonetic pronunciation in English letters
- Do NOT mix native script with transliterations like "పాఠశాల (Pāṭhaśāla)" - keep them completely separate

Respond with ONLY valid JSON that follows this exact structure:
{{
  "vocabulary": [
    {{"word": "word_in_target_language_only", "translation": "english_meaning", "transliteration": "phonetic_pronunciation_only"}},
    ...12 items total
  ],
  "sentences": [
    {{"sentence": "sentence_in_target_language_only", "translation": "english_translation", "transliteration": "phonetic_pronunciation_only"}},
    ...7 items total
  ],
  "conversations": [
    {{"speaker": "name", "line": "dialogue_in_target_language_only", "translation": "english_translation", "transliteration": "phonetic_pronunciation_only"}},
    ...9 items total
  ],
  "quiz": [
    {{"question": "question_text_in_english", "options": ["option1", "option2", "option3", "option4"], "answer": "correct_option"}},
    ...5 items total
  ]
}}
"""

        try:
            response = await self._make_request_with_retry(prompt, "enhanced lesson generation")
            
            response_text = response.text.strip()
            
            # Clean up response text
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Find JSON content
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                raise ValueError("No valid JSON found in response")
            
            json_content = response_text[start_idx:end_idx + 1]
            
            # Parse and validate JSON
            parsed_data = json.loads(json_content)
            learning_data = EnhancedLearningData(**parsed_data)
            
            # Cache the result
            self.learning_cache[cache_key] = learning_data
            self._manage_cache_size()
            
            return learning_data
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse enhanced lesson JSON. Response: {response_text[:1000]}...")
            raise ValueError(f"Invalid JSON response from Gemini: {e}")
        except Exception as e:
            print(f"Error generating enhanced learning data: {e}")
            raise ValueError(f"Failed to generate learning content. The AI may be unable to process this topic in the requested language, or there was a network issue. Please try again with a different topic.")

    async def _make_request_with_retry(self, prompt: str, operation_name: str = "request"):
        """Make a request to Gemini with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response
            except Exception as e:
                last_exception = e
                error_msg = str(e).lower()
                
                # Check if it's a retryable error
                if any(keyword in error_msg for keyword in ['overloaded', 'rate limit', 'quota', '503', '429', '500']):
                    if attempt < self.max_retries - 1:
                        delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                        print(f"Gemini API {operation_name} failed (attempt {attempt + 1}/{self.max_retries}): retrying in {delay:.1f}s")
                        time.sleep(delay)
                        continue
                else:
                    # Non-retryable error, fail immediately
                    raise e
        
        # All retries exhausted
        raise Exception(f"Gemini API {operation_name} failed after {self.max_retries} attempts. Last error: {last_exception}")

    def _get_cache_key(self, topic: str, language: str) -> str:
        """Generate cache key for learning data"""
        key_string = f"{topic.lower().strip()}|{language.lower().strip()}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _manage_cache_size(self):
        """Remove oldest entries if cache is too large"""
        if len(self.learning_cache) > self.max_cache_size:
            # Remove 25% of oldest entries
            keys_to_remove = list(self.learning_cache.keys())[:len(self.learning_cache) // 4]
            for key in keys_to_remove:
                del self.learning_cache[key]

    def transform_to_desi_lesson_format(self, enhanced_data: EnhancedLearningData, topic: str, language: str, difficulty: str = "beginner") -> DesiLessonResponse:
        """
        Transform enhanced learning data to the existing DesiLessonResponse format for database storage.
        This allows us to use the existing database schema and CRUD functions.
        """
        # Transform all 12 vocabulary items from enhanced data
        vocabulary_items = []
        for i, vocab in enumerate(enhanced_data.vocabulary):  # Use all vocabulary items (12)
            vocabulary_items.append(DesiVocabularyItem(
                english=vocab.translation,
                target_language_script=vocab.word,
                transliteration=vocab.transliteration,
                pronunciation=vocab.transliteration  # Use transliteration as pronunciation fallback
            ))

        # Transform all 7 sentences from enhanced data
        sentence_items = []
        for i, sentence in enumerate(enhanced_data.sentences):  # Use all sentences (7)
            sentence_items.append(DesiExampleSentence(
                english=sentence.translation,
                target_language_script=sentence.sentence,
                transliteration=sentence.transliteration,
                pronunciation=sentence.transliteration  # Use transliteration as pronunciation fallback
            ))

        # Transform conversations to dialogue format
        dialogue_items = []
        for i, conv in enumerate(enhanced_data.conversations):
            dialogue_items.append(DesiDialogueItem(
                speaker=conv.speaker,
                target_language_script=conv.line,
                transliteration=conv.transliteration,
                english=conv.translation
            ))

        # Create short story from conversations
        short_story = DesiShortStory(
            title=f"{topic} Conversation",
            dialogue=dialogue_items
        )

        # Transform quiz questions (existing schema supports variable number)
        quiz_questions = []
        for quiz in enhanced_data.quiz:
            quiz_questions.append(DesiQuizQuestion(
                question=quiz.question,
                options=quiz.options,
                answer=quiz.answer
            ))

        # Create the lesson content
        lesson_content = DesiLessonContent(
            title=topic,
            target_language=language,
            difficulty=difficulty,
            vocabulary=vocabulary_items,
            example_sentences=sentence_items,
            short_story=short_story,
            quiz=quiz_questions
        )

        # Return in the existing format
        return DesiLessonResponse(desi_lesson=lesson_content)


# Global instance
enhanced_gemini_service = EnhancedGeminiService()