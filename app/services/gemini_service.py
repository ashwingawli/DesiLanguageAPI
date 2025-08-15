import google.generativeai as genai
import json
import time
import random
import hashlib
from typing import Dict, Optional
from app.utils.config import settings
from app.models.schemas import DesiLessonResponse

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        # Configure model for faster responses
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,  # Lower temperature for more consistent, faster responses
            max_output_tokens=800,  # Increased for story generation with translation and vocabulary
            top_p=0.8,
            top_k=40
        )
        self.model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
        self.max_retries = 2  # Reduced from 3
        self.base_delay = 1   # Reduced from 2
        
        # Simple in-memory cache for translations
        self.translation_cache: Dict[str, dict] = {}
        self.max_cache_size = 1000  # Limit cache size
    
    def load_prompt_template(self) -> str:
        with open('Gemini_prompt.txt', 'r') as f:
            return f.read()
    
    def create_desi_lesson_schema(self) -> dict:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Desi Language Lesson Schema",
            "description": "A structured lesson for any target language with desi prefix",
            "type": "object",
            "properties": {
                "desi_lesson": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "pattern": "^Lesson \\d+: .+",
                            "minLength": 1
                        },
                        "target_language": {
                            "type": "string",
                            "minLength": 1
                        },
                        "theme": {
                            "type": "string",
                            "minLength": 1
                        },
                        "vocabulary": {
                            "type": "array",
                            "minItems": 10,
                            "maxItems": 10,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "english": {"type": "string", "minLength": 1},
                                    "target_language_script": {"type": "string", "minLength": 1},
                                    "transliteration": {"type": "string", "minLength": 1},
                                    "pronunciation": {"type": "string", "minLength": 1}
                                },
                                "required": ["english", "target_language_script", "transliteration", "pronunciation"],
                                "additionalProperties": false
                            }
                        },
                        "example_sentences": {
                            "type": "array",
                            "minItems": 5,
                            "maxItems": 5,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "english": {"type": "string", "minLength": 1},
                                    "target_language_script": {"type": "string", "minLength": 1},
                                    "transliteration": {"type": "string", "minLength": 1},
                                    "pronunciation": {"type": "string", "minLength": 1}
                                },
                                "required": ["english", "target_language_script", "transliteration", "pronunciation"],
                                "additionalProperties": false
                            }
                        },
                        "short_story": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "minLength": 1},
                                "dialogue": {
                                    "type": "array",
                                    "minItems": 1,
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "speaker": {"type": "string", "minLength": 1},
                                            "target_language_script": {"type": "string", "minLength": 1},
                                            "transliteration": {"type": "string", "minLength": 1},
                                            "english": {"type": "string", "minLength": 1}
                                        },
                                        "required": ["speaker", "target_language_script", "transliteration", "english"],
                                        "additionalProperties": false
                                    }
                                }
                            },
                            "required": ["title", "dialogue"],
                            "additionalProperties": false
                        },
                        "quiz": {
                            "type": "array",
                            "minItems": 4,
                            "maxItems": 4,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string", "minLength": 1},
                                    "options": {
                                        "type": "array",
                                        "minItems": 2,
                                        "items": {"type": "string", "minLength": 1}
                                    },
                                    "answer": {"type": "string", "minLength": 1}
                                },
                                "required": ["question", "options", "answer"],
                                "additionalProperties": false
                            }
                        }
                    },
                    "required": ["title", "target_language", "theme", "vocabulary", "example_sentences", "short_story", "quiz"],
                    "additionalProperties": false
                }
            },
            "required": ["desi_lesson"],
            "additionalProperties": false
        }
    
    async def generate_desi_lesson(self, target_language: str, lesson_topic: str, theme: str = None) -> DesiLessonResponse:
        # Use provided theme or default to lesson topic
        lesson_theme = theme or lesson_topic
        
        # Randomly select names for variety
        male_names = ["Arjun", "Rohan", "Vikram", "Raj", "Amit", "Arun", "Karthik", "Nikhil", "Suresh", "Ravi"]
        female_names = ["Priya", "Anita", "Meera", "Kavitha", "Sunita", "Pooja", "Sneha", "Divya", "Nisha", "Geeta"]
        
        selected_male = random.choice(male_names)
        selected_female = random.choice(female_names)
        
        # Create a concise, structured prompt for lesson generation
        prompt = f"""Create a {target_language} lesson on "{lesson_topic}".

Requirements:
- 10 vocabulary items
- 5 example sentences  
- 1 short story with dialogue between two people with these specific Indian names: {selected_male} (male speaker) and {selected_female} (female speaker)
- 4 quiz questions
- Include transliteration for all {target_language} text
- Use English phonetics for pronunciation

Respond with ONLY valid JSON in this exact format:
{{
  "desi_lesson": {{
    "title": "{lesson_topic}",
    "target_language": "{target_language}",
    "theme": "{lesson_theme}",
    "vocabulary": [
      {{
        "english": "word",
        "target_language_script": "script",
        "transliteration": "phonetic",
        "pronunciation": "pronunciation"  
      }}
    ],
    "example_sentences": [
      {{
        "english": "sentence",
        "target_language_script": "script",
        "transliteration": "phonetic",
        "pronunciation": "pronunciation"
      }}
    ],
    "short_story": {{
      "title": "title",
      "dialogue": [
        {{
          "speaker": "name",
          "target_language_script": "script",
          "transliteration": "phonetic",
          "english": "translation"
        }}
      ]
    }},
    "quiz": [
      {{
        "question": "question text",
        "options": ["option1", "option2", "option3"],
        "answer": "correct_option"
      }}
    ]
  }}
}}"""
        
        try:
            response = await self._make_request_with_retry(prompt, "lesson generation")
            
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Find JSON content between braces
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                raise ValueError("No valid JSON found in response")
            
            json_content = response_text[start_idx:end_idx + 1]
            
            # Parse JSON
            lesson_data = json.loads(json_content)
            
            return DesiLessonResponse(**lesson_data)
            
        except json.JSONDecodeError as e:
            # Log the actual response for debugging
            print(f"Failed to parse lesson JSON. Full response was: {response_text}")
            print(f"JSON error at position {e.pos}: {e.msg}")
            # Temporarily return the response for debugging
            raise ValueError(f"Invalid JSON response from Gemini: {e}. Response was: {response_text[:500]}...")
        except Exception as e:
            raise ValueError(f"Error generating desi lesson: {e}")
    
    async def generate_completion(self, prompt: str) -> str:
        """Generate a completion for any prompt"""
        try:
            response = await self._make_request_with_retry(prompt, "completion")
            return response.text.strip()
        except Exception as e:
            raise ValueError(f"Error generating completion: {e}")
    
    async def _make_request_with_retry(self, prompt: str, operation_name: str = "request"):
        """Make a request to Gemini with retry logic for handling rate limits and overload"""
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
                    if attempt < self.max_retries - 1:  # Don't sleep on last attempt
                        # Faster retry with minimal jitter
                        delay = self.base_delay * (1.5 ** attempt) + random.uniform(0, 0.5)
                        print(f"Gemini API {operation_name} failed (attempt {attempt + 1}/{self.max_retries}): retrying in {delay:.1f}s")
                        time.sleep(delay)
                        continue
                else:
                    # Non-retryable error, fail immediately
                    raise e
        
        # All retries exhausted
        raise Exception(f"Gemini API {operation_name} failed after {self.max_retries} attempts. Last error: {last_exception}")

    def _get_cache_key(self, text: str, from_language: str, to_language: str) -> str:
        """Generate cache key for translation"""
        key_string = f"{text.lower().strip()}|{from_language}|{to_language}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _manage_cache_size(self):
        """Remove oldest entries if cache is too large"""
        if len(self.translation_cache) > self.max_cache_size:
            # Remove 25% of oldest entries
            keys_to_remove = list(self.translation_cache.keys())[:len(self.translation_cache) // 4]
            for key in keys_to_remove:
                del self.translation_cache[key]

    async def translate_text(self, text: str, from_language: str, to_language: str) -> dict:
        """Translate text from one language to another with transliteration"""
        try:
            # Check cache first
            cache_key = self._get_cache_key(text, from_language, to_language)
            if cache_key in self.translation_cache:
                print(f"Cache hit for translation: {text[:30]}...")
                return self.translation_cache[cache_key]
            # Create concise translation prompt
            south_asian_langs = ["Hindi", "Tamil", "Telugu", "Kannada", "Marathi", "Bengali", "Gujarati", "Punjabi", "Urdu", "Malayalam", "Odia", "Assamese"]
            needs_transliteration = to_language in south_asian_langs
            
            transliteration_field = ', "transliteration": "phonetic"' if needs_transliteration else ''
            transliteration_note = f"Include transliteration for {to_language}." if needs_transliteration else ""
            
            prompt = f"""Translate "{text}" from {from_language} to {to_language}.

Respond with ONLY JSON:
{{"translation": "translated text"{transliteration_field}}}

{transliteration_note}"""

            response = await self._make_request_with_retry(prompt, "translation")
            response_text = response.text.strip()
            
            # Clean up response text
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Find JSON content between braces
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                raise ValueError("No valid JSON found in translation response")
            
            json_content = response_text[start_idx:end_idx + 1]
            
            # Parse JSON
            translation_data = json.loads(json_content)
            
            # Validate required fields
            if 'translation' not in translation_data:
                raise ValueError("Translation field missing from response")
            
            # Cache the result
            self.translation_cache[cache_key] = translation_data
            self._manage_cache_size()
            
            return translation_data
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse translation JSON. Response was: {response_text[:500]}...")
            raise ValueError(f"Invalid JSON response from Gemini: {e}")
        except Exception as e:
            raise ValueError(f"Error translating text: {e}")

gemini_service = GeminiService()