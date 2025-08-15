import json
from typing import Set, Optional
from sqlalchemy.orm import Session
from app.models.schemas import Language, CEFRLevel, StoryData, VocabularyWord, StoryGenerationRequest
from app.services.gemini_service import gemini_service
from app.api.story_crud import create_desi_story, find_similar_story

class StoryService:
    def __init__(self):
        self.non_latin_languages: Set[Language] = {
            Language.Arabic,
            Language.Assamese,
            Language.Bengali,
            Language.Gujarati,
            Language.Hindi,
            Language.Japanese,
            Language.Kannada,
            Language.Korean,
            Language.Malayalam,
            Language.Mandarin,
            Language.Marathi,
            Language.Odia,
            Language.Punjabi,
            Language.Russian,
            Language.Tamil,
            Language.Telugu,
            Language.Thai,
            Language.Urdu
        }

    async def generate_story(
        self, 
        request: StoryGenerationRequest, 
        db: Optional[Session] = None,
        user_id: Optional[int] = None,
        save_to_db: bool = True
    ) -> StoryData:
        """Generate a story based on CEFR level and language"""
        try:
            
            needs_transliteration = request.language in self.non_latin_languages
            transliteration_instruction = ""
            if needs_transliteration:
                transliteration_instruction = (
                    "For the translation, also provide a phonetic transliteration in the Latin alphabet "
                    "in the 'transliteration' field. The transliteration must have the same paragraph "
                    "structure as the translation."
                )
            
            scenario_text = f" about \"{request.scenario}\"" if request.scenario else ""
            
            vocabulary_instruction = ""
            if needs_transliteration:
                vocabulary_instruction = (
                    "For each vocabulary word, provide both the {request.language} translation "
                    "and its phonetic transliteration in the Latin alphabet."
                ).format(request=request)
            else:
                vocabulary_instruction = f"For each vocabulary word, provide its translation in {request.language}."
            
            prompt = f"""You are an expert language tutor. Generate one very short, simple story (3-5 sentences long){scenario_text} for a student learning English at the {request.level} CEFR level. The story should be engaging and use basic vocabulary.

Also provide the full translation of the story in {request.language}. From the story, identify 3-5 key vocabulary words appropriate for the level. {vocabulary_instruction} {transliteration_instruction}

CRITICAL: You MUST respond with ONLY a valid JSON object. No explanations, no markdown, no text before or after. Just the JSON.

Required JSON format:
{{
  "story": "English story text here",
  "translation": "Translated story here",
  "transliteration": "Romanized transliteration (only if the target language uses non-Latin script)",
  "vocabulary": [
    {{"word": "word1", "definition": "translation1", "transliteration": "transliteration1"}},
    {{"word": "word2", "definition": "translation2", "transliteration": "transliteration2"}}
  ]
}}

Example response:
{{"story": "The cat sits on the mat.", "translation": "बिल्ली चटाई पर बैठती है।", "transliteration": "billi chataee par baithati hai.", "vocabulary": [{{"word": "cat", "definition": "बिल्ली", "transliteration": "billi"}}, {{"word": "sits", "definition": "बैठती है", "transliteration": "baithati hai"}}]}}

Return ONLY the JSON object."""

            # Use the existing Gemini service
            response = await gemini_service.generate_completion(prompt)
            
            # Parse the JSON response
            try:
                response_text = response.strip()
                print(f"Raw AI response: {response_text[:500]}...")  # Debug output
                
                # Try multiple JSON extraction strategies
                story_json = None
                
                # Strategy 1: Direct JSON parsing (if response is pure JSON)
                try:
                    story_json = json.loads(response_text)
                    print("Successfully parsed JSON directly")
                except json.JSONDecodeError:
                    pass
                
                # Strategy 2: Remove common markdown wrappers
                if story_json is None:
                    cleaned_text = response_text
                    # Remove various markdown code block formats
                    if cleaned_text.startswith('```json'):
                        cleaned_text = cleaned_text.replace('```json', '').replace('```', '').strip()
                    elif cleaned_text.startswith('```'):
                        cleaned_text = cleaned_text.replace('```', '').strip()
                    
                    try:
                        story_json = json.loads(cleaned_text)
                        print("Successfully parsed JSON after markdown removal")
                    except json.JSONDecodeError:
                        pass
                
                # Strategy 3: Extract content between braces
                if story_json is None:
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}')
                    
                    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                        json_content = response_text[start_idx:end_idx + 1]
                        try:
                            story_json = json.loads(json_content)
                            print("Successfully parsed JSON from brace extraction")
                        except json.JSONDecodeError:
                            pass
                
                if story_json is None:
                    print(f"All JSON parsing strategies failed for response: {response_text}")
                    raise ValueError("No valid JSON found in response")
                
            except json.JSONDecodeError as e:
                raise ValueError("AI returned invalid JSON format")
            
            # Validate required fields
            if not story_json.get("story") or not story_json.get("translation"):
                raise ValueError("AI returned incomplete story data")
            
            # Create vocabulary objects
            vocabulary = []
            if story_json.get("vocabulary"):
                for vocab_item in story_json["vocabulary"]:
                    vocabulary.append(VocabularyWord(
                        word=vocab_item.get("word", ""),
                        definition=vocab_item.get("definition"),
                        transliteration=vocab_item.get("transliteration")
                    ))
            
            story_data = StoryData(
                story=story_json["story"],
                translation=story_json["translation"],
                transliteration=story_json.get("transliteration"),
                vocabulary=vocabulary
            )
            
            
            # Save to database if requested and db session is provided
            if save_to_db and db is not None:
                try:
                    # Store the prompt used for generation
                    generation_prompt = f"Level: {request.level}, Language: {request.language}"
                    if request.scenario:
                        generation_prompt += f", Scenario: {request.scenario}"
                    
                    # Check if similar story already exists to avoid duplicates
                    existing_story = find_similar_story(
                        db, 
                        str(request.language.value), 
                        str(request.level.value), 
                        request.scenario
                    )
                    
                    if not existing_story:
                        db_story = create_desi_story(
                            db=db,
                            story_data=story_data,
                            target_language=str(request.language.value),
                            cefr_level=str(request.level.value),
                            scenario=request.scenario,
                            user_id=user_id,
                            generation_prompt=generation_prompt
                        )
                    else:
                        pass
                        
                except Exception as e:
                    # Don't raise the error, just ignore it - story generation was successful
                    pass
            
            return story_data
            
        except Exception as e:
            raise Exception(f"Failed to generate story: {str(e)}")

    async def generate_custom_story(
        self, 
        request: StoryGenerationRequest, 
        db: Optional[Session] = None,
        user_id: Optional[int] = None,
        save_to_db: bool = True
    ) -> StoryData:
        """Generate a custom story with a specific scenario"""
        if not request.scenario:
            raise ValueError("Scenario is required for custom story generation")
        
        return await self.generate_story(request, db, user_id, save_to_db)

# Create a singleton instance
story_service = StoryService()