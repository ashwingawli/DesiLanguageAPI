#!/usr/bin/env python3
"""
Script to regenerate missing transliterations for existing stories.
This script finds stories that have vocabulary without transliterations
and uses the Gemini AI service to generate them.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session, joinedload
from app.utils.database import get_db
from app.models.models import DesiStory, DesiStoryVocabulary
from app.services.gemini_service import gemini_service
from app.utils.logger import api_logger
import json

# Languages that need transliteration (non-Latin scripts)
NON_LATIN_LANGUAGES = {
    'Arabic', 'Assamese', 'Bengali', 'Gujarati', 'Hindi', 'Japanese', 
    'Kannada', 'Korean', 'Malayalam', 'Mandarin', 'Marathi', 'Odia', 
    'Punjabi', 'Russian', 'Tamil', 'Telugu', 'Thai', 'Urdu'
}

async def generate_vocabulary_transliterations(vocabulary_items, target_language):
    """Generate transliterations for vocabulary items using Gemini AI"""
    
    if target_language not in NON_LATIN_LANGUAGES:
        return {}  # No transliterations needed for Latin script languages
    
    # Prepare vocabulary for AI
    vocab_list = [{"word": vocab.word, "definition": vocab.definition} for vocab in vocabulary_items]
    
    prompt = f"""You are an expert linguist. For each English word and its {target_language} translation below, provide the phonetic transliteration in the Latin alphabet.

Vocabulary items:
{json.dumps(vocab_list, indent=2, ensure_ascii=False)}

IMPORTANT: Respond with ONLY valid JSON in this EXACT format:
{{
  "word1": "transliteration1",
  "word2": "transliteration2"
}}

The keys should be the English words, and the values should be the phonetic transliterations of the {target_language} translations."""

    try:
        response = await gemini_service.generate_completion(prompt)
        
        # Parse the JSON response
        response_text = response.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text.replace('```json', '').replace('```', '').strip()
        elif response_text.startswith('```'):
            response_text = response_text.replace('```', '').strip()
        
        # Find JSON content between braces
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            api_logger.error(f"No valid JSON found in response: {response_text[:200]}")
            return {}
        
        json_content = response_text[start_idx:end_idx + 1]
        transliterations = json.loads(json_content)
        
        return transliterations
        
    except Exception as e:
        api_logger.error(f"Error generating transliterations: {str(e)}")
        return {}

async def regenerate_missing_transliterations():
    """Find stories with missing transliterations and regenerate them"""
    
    db = next(get_db())
    try:
        # Find stories that have vocabulary items without transliterations
        stories_with_missing_transliterations = db.query(DesiStory).options(
            joinedload(DesiStory.vocabulary)
        ).join(DesiStoryVocabulary).filter(
            DesiStoryVocabulary.transliteration.is_(None)
        ).distinct().all()
        
        print(f"Found {len(stories_with_missing_transliterations)} stories with missing transliterations")
        
        updated_count = 0
        for story in stories_with_missing_transliterations:
            print(f"\nProcessing Story ID {story.id} ({story.target_language})")
            
            # Get vocabulary items without transliterations
            missing_vocab = [vocab for vocab in story.vocabulary if not vocab.transliteration]
            
            if not missing_vocab:
                continue
                
            print(f"  - Missing transliterations for {len(missing_vocab)} vocabulary items")
            
            # Generate transliterations
            transliterations = await generate_vocabulary_transliterations(missing_vocab, story.target_language)
            
            if not transliterations:
                print(f"  - Failed to generate transliterations for story {story.id}")
                continue
            
            # Update vocabulary items
            updated_vocab_count = 0
            for vocab in missing_vocab:
                if vocab.word in transliterations:
                    vocab.transliteration = transliterations[vocab.word]
                    updated_vocab_count += 1
                    print(f"    * {vocab.word} -> {vocab.transliteration}")
            
            if updated_vocab_count > 0:
                db.commit()
                updated_count += 1
                print(f"  - Updated {updated_vocab_count} vocabulary items")
            
        print(f"\nCompleted! Updated {updated_count} stories with missing transliterations")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Regenerating missing transliterations for existing stories...")
    asyncio.run(regenerate_missing_transliterations())