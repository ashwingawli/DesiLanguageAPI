import google.generativeai as genai
import json
from app.utils.config import settings
from app.models.schemas import DesiLessonResponse

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
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
        prompt_template = self.load_prompt_template()
        
        # Use provided theme or default to lesson topic
        lesson_theme = theme or lesson_topic
        
        prompt = prompt_template.format(
            target_language=target_language,
            lesson_topic=lesson_topic
        )
        
        # Add theme context to the prompt
        if theme and theme != lesson_topic:
            prompt += f"\n\nLesson Focus: {theme}"
        
        prompt += f"""

IMPORTANT: Respond with ONLY valid JSON in this EXACT format. Do not include any text before or after the JSON:

{{
  "desi_lesson": {{
    "title": "{lesson_topic}",
    "target_language": "{target_language}",
    "theme": "{lesson_theme}",
    "vocabulary": [
      {{
        "english": "hello",
        "target_language_script": "नमस्ते",
        "transliteration": "namaste",
        "pronunciation": "nuh-muh-stay"
      }}
    ],
    "example_sentences": [
      {{
        "english": "Hello, how are you?",
        "target_language_script": "नमस्ते, आप कैसे हैं?",
        "transliteration": "namaste, aap kaise hain?",
        "pronunciation": "nuh-muh-stay, ahp kai-say hain"
      }}
    ],
    "short_story": {{
      "title": "A Simple Greeting",
      "dialogue": [
        {{
          "speaker": "Person A",
          "target_language_script": "नमस्ते!",
          "transliteration": "Namaste!",
          "english": "Hello!"
        }}
      ]
    }},
    "quiz": [
      {{
        "question": "How do you say 'hello' in {target_language}?",
        "options": ["namaste", "goodbye", "thank you"],
        "answer": "namaste"
      }}
    ]
  }}
}}

Use exactly these field names: english, target_language_script, transliteration, pronunciation, speaker, question, options, answer. Include exactly 10 vocabulary items, 5 example sentences, and 4 quiz questions."""
        
        try:
            response = self.model.generate_content(prompt)
            
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
            print(f"Failed to parse JSON. Response was: {response_text[:500]}...")
            raise ValueError(f"Invalid JSON response from Gemini: {e}")
        except Exception as e:
            raise ValueError(f"Error generating desi lesson: {e}")

gemini_service = GeminiService()