#!/usr/bin/env python3
"""
Script to load lesson JSON files from Lessons_upload folder into the database
"""
import json
import sys
import os
import glob
import shutil
from pathlib import Path
from sqlalchemy.orm import Session

# Add the parent directory to sys.path so we can import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.api import crud
from app.utils.database import SessionLocal
from app.models import schemas

def transform_lesson_json(lesson_json):
    """
    Transform lesson JSON to match Gemini response format
    """
    lesson_data = lesson_json["lesson"]
    
    # Keep all quiz questions (expecting 5)
    quiz_questions = lesson_data["quiz"][:5]
    
    # Transform to Gemini response format
    transformed = {
        "desi_lesson": {
            "title": lesson_data["title"],
            "target_language": lesson_data["target_language"],
            "theme": lesson_data["theme"],
            "vocabulary": lesson_data["vocabulary"],
            "example_sentences": lesson_data["example_sentences"],
            "short_story": lesson_data["short_story"],
            "quiz": quiz_questions
        }
    }
    
    return transformed

def move_file_to_folder(file_path, destination_folder):
    """
    Move file to destination folder, creating folder if needed
    """
    # Create destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)
    
    # Get filename and create destination path
    filename = os.path.basename(file_path)
    destination_path = os.path.join(destination_folder, filename)
    
    # Handle duplicate filenames by adding a number
    counter = 1
    original_destination = destination_path
    while os.path.exists(destination_path):
        name, ext = os.path.splitext(original_destination)
        destination_path = f"{name}_{counter}{ext}"
        counter += 1
    
    # Move the file
    shutil.move(file_path, destination_path)
    return destination_path

def load_lesson_from_file(file_path, loaded_folder="Lessons_upload/loaded", failed_folder="Lessons_upload/failed"):
    """
    Load lesson from a single JSON file into database
    """
    filename = os.path.basename(file_path)
    print(f"\n📁 Processing file: {filename}")
    print("-" * 40)
    
    # Read lesson JSON file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lesson_data_raw = json.load(f)
        print(f"✅ Successfully read {filename}")
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        
        # Move file to failed folder
        try:
            moved_path = move_file_to_folder(file_path, failed_folder)
            print(f"📁 Moved to failed folder: {moved_path}")
        except Exception as e:
            print(f"⚠️  Could not move file to failed folder: {e}")
        
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format in {filename}: {e}")
        
        # Move file to failed folder
        try:
            moved_path = move_file_to_folder(file_path, failed_folder)
            print(f"📁 Moved to failed folder: {moved_path}")
        except Exception as e:
            print(f"⚠️  Could not move file to failed folder: {e}")
        
        return False
    
    # Validate structure
    lesson_data = lesson_data_raw.get("lesson", {})
    vocab_count = len(lesson_data.get("vocabulary", []))
    sentences_count = len(lesson_data.get("example_sentences", []))
    dialogue_count = len(lesson_data.get("short_story", {}).get("dialogue", []))
    quiz_count = len(lesson_data.get("quiz", []))
    
    print(f"📊 Lesson structure:")
    print(f"   - Vocabulary: {vocab_count} items")
    print(f"   - Example sentences: {sentences_count} items")
    print(f"   - Dialogue: {dialogue_count} items")
    print(f"   - Quiz questions: {quiz_count} items")
    
    # Check if meets requirements
    if vocab_count != 12:
        print(f"⚠️  Vocabulary count is {vocab_count}, expected 12")
    if sentences_count != 7:
        print(f"⚠️  Example sentences count is {sentences_count}, expected 7")
    if dialogue_count != 9:
        print(f"⚠️  Dialogue count is {dialogue_count}, expected 9")
    if quiz_count < 5:
        print(f"⚠️  Quiz questions count is {quiz_count}, need at least 5")
    
    # Transform to Gemini format
    print("🔄 Transforming to Gemini response format...")
    try:
        transformed_data = transform_lesson_json(lesson_data_raw)
        
        # Create Pydantic model
        lesson_response = schemas.DesiLessonResponse(**transformed_data)
        print("✅ Successfully validated lesson structure")
        
    except Exception as e:
        print(f"❌ Validation failed for {filename}: {e}")
        
        # Move file to failed folder
        try:
            moved_path = move_file_to_folder(file_path, failed_folder)
            print(f"📁 Moved to failed folder: {moved_path}")
        except Exception as e:
            print(f"⚠️  Could not move file to failed folder: {e}")
        
        return False
    
    # Save to database
    print("💾 Saving to database...")
    db = SessionLocal()
    try:
        # Get target language from lesson data
        target_language = lesson_data.get("target_language", "Unknown")
        
        # Check if lesson already exists
        existing_lessons = crud.get_desi_lessons_by_language(db, target_language)
        print(f"📊 Existing {target_language} lessons in DB: {len(existing_lessons)}")
        
        # Save lesson
        db_lesson = crud.create_desi_lesson(db, lesson_response, lesson_data["theme"])
        
        print(f"✅ Successfully saved lesson to database with ID: {db_lesson.id}")
        print(f"📝 Lesson title: {db_lesson.title}")
        print(f"🌍 Language: {db_lesson.target_language}")
        print(f"🎯 Theme: {db_lesson.theme}")
        print(f"📊 Lesson number: {db_lesson.lesson_number}")
        
        # Verify final state
        final_lessons = crud.get_desi_lessons_by_language(db, target_language)
        print(f"📊 Total {target_language} lessons in DB now: {len(final_lessons)}")
        
    except Exception as e:
        print(f"❌ Database save failed for {filename}: {e}")
        db.rollback()
        
        # Move file to failed folder
        try:
            moved_path = move_file_to_folder(file_path, failed_folder)
            print(f"📁 Moved to failed folder: {moved_path}")
        except Exception as e:
            print(f"⚠️  Could not move file to failed folder: {e}")
        
        return False
    finally:
        db.close()
    
    print(f"✅ Lesson from {filename} loaded successfully!")
    
    # Move file to loaded folder
    try:
        moved_path = move_file_to_folder(file_path, loaded_folder)
        print(f"📁 Moved to: {moved_path}")
    except Exception as e:
        print(f"⚠️  Could not move file to loaded folder: {e}")
    
    return True

def load_lessons_from_folder(folder_path="Lessons_upload"):
    """
    Load all lesson JSON files from the specified folder
    """
    print("🚀 Loading lesson files from Lessons_upload folder...")
    print("=" * 60)
    
    # Check if folder exists
    if not os.path.exists(folder_path):
        print(f"❌ Folder '{folder_path}' not found!")
        print(f"Please create the folder and add JSON lesson files.")
        return
    
    # Find all JSON files in the folder
    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    
    if not json_files:
        print(f"❌ No JSON files found in '{folder_path}' folder!")
        print(f"Please add lesson JSON files to the folder.")
        return
    
    print(f"📂 Found {len(json_files)} JSON file(s) in '{folder_path}':")
    for file_path in json_files:
        print(f"   - {os.path.basename(file_path)}")
    
    # Process each file
    successful_loads = 0
    failed_loads = 0
    
    # Create loaded and failed folders
    loaded_folder = os.path.join(folder_path, "loaded")
    failed_folder = os.path.join(folder_path, "failed")
    
    for file_path in json_files:
        success = load_lesson_from_file(file_path, loaded_folder, failed_folder)
        if success:
            successful_loads += 1
        else:
            failed_loads += 1
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {len(json_files)}")
    print(f"✅ Successful loads: {successful_loads}")
    print(f"❌ Failed loads: {failed_loads}")
    
    if successful_loads > 0:
        print(f"\n🎉 Successfully loaded {successful_loads} lesson(s) into the database!")
        print(f"📁 Successful files moved to: {loaded_folder}/")
    
    if failed_loads > 0:
        print(f"\n⚠️  {failed_loads} file(s) failed to load. Check the error messages above.")
        print(f"📁 Failed files moved to: {failed_folder}/")

def main():
    """Main function"""
    load_lessons_from_folder()

if __name__ == "__main__":
    main()