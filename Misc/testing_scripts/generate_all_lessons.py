#!/usr/bin/env python3
"""
Script to generate all lessons for a specific language using all topics from Lessons_title.txt
Saves lessons directly to the database
"""
import asyncio
import json
import sys
import os
import time
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session

# Add the parent directory to sys.path so we can import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.gemini_service import gemini_service
from app.services.lesson_parser import lesson_parser
from app.api import crud
from app.utils.database import SessionLocal
from app.models import models

async def generate_all_lessons(target_language: str, save_to_db: bool = True, delay_seconds: int = 2):
    """
    Generate lessons for all topics in Lessons_title.txt for the specified language
    
    Args:
        target_language: The language to generate lessons for (e.g., "Telugu", "Hindi", "Kannada")
        save_to_db: Whether to save lessons to database (True by default)
        delay_seconds: Delay between API calls to avoid rate limiting
    """
    print(f"🚀 Starting lesson generation for {target_language}")
    print("=" * 60)
    
    # Load all lesson topics
    try:
        topics = lesson_parser.get_lesson_titles()
        print(f"📚 Found {len(topics)} lesson topics in Lessons_title.txt")
    except Exception as e:
        print(f"❌ Failed to load lesson topics: {e}")
        return
    
    if not topics:
        print("❌ No topics found in Lessons_title.txt")
        return
    
    # Print first few topics as preview
    print(f"📝 Sample topics: {topics[:3]}...")
    print()
    
    # Initialize tracking
    results = []
    successful_lessons = []
    failed_lessons = []
    saved_to_db = []
    start_time = time.time()
    
    # Initialize database session
    db = SessionLocal()
    
    print(f"🗄️  Database: {'Enabled' if save_to_db else 'Disabled'}")
    
    # Check existing lessons in database
    if save_to_db:
        existing_lessons = crud.get_desi_lessons_by_language(db, target_language)
        print(f"📊 Existing lessons in DB for {target_language}: {len(existing_lessons)}")
    
    print()
    
    # Generate lessons for each topic
    for i, topic in enumerate(topics, 1):
        print(f"🔄 Generating Lesson {i}/{len(topics)}: {topic}")
        
        try:
            # Generate lesson using Gemini API
            lesson_response = await gemini_service.generate_desi_lesson(
                target_language=target_language,
                lesson_topic=topic,
                theme=topic  # Use topic as theme
            )
            
            print(f"✅ Successfully generated: {lesson_response.desi_lesson.title}")
            
            # Save to database if requested
            db_lesson_id = None
            if save_to_db:
                try:
                    # Save lesson to database using CRUD
                    db_lesson = crud.create_desi_lesson(db, lesson_response, topic)
                    db_lesson_id = db_lesson.id
                    saved_to_db.append(db_lesson)
                    print(f"🗄️  Saved to database with ID: {db_lesson_id}")
                except Exception as db_error:
                    print(f"⚠️  Database save failed: {str(db_error)}")
            
            # Track success
            lesson_info = {
                "lesson_number": i,
                "topic": topic,
                "status": "success",
                "title": lesson_response.desi_lesson.title,
                "target_language": lesson_response.desi_lesson.target_language,
                "vocabulary_count": len(lesson_response.desi_lesson.vocabulary),
                "sentences_count": len(lesson_response.desi_lesson.example_sentences),
                "dialogue_count": len(lesson_response.desi_lesson.short_story.dialogue),
                "quiz_count": len(lesson_response.desi_lesson.quiz),
                "generated_at": datetime.now().isoformat(),
                "db_lesson_id": db_lesson_id,
                "saved_to_db": db_lesson_id is not None
            }
            results.append(lesson_info)
            successful_lessons.append(lesson_response)
            
        except Exception as e:
            print(f"❌ Failed to generate lesson for '{topic}': {str(e)}")
            
            # Track failure
            lesson_info = {
                "lesson_number": i,
                "topic": topic,
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }
            results.append(lesson_info)
            failed_lessons.append(lesson_info)
        
        # Add delay to avoid rate limiting
        if i < len(topics):  # Don't delay after the last lesson
            print(f"⏳ Waiting {delay_seconds} seconds...")
            await asyncio.sleep(delay_seconds)
        
        print()  # Empty line for readability
    
    # Close database session
    db.close()
    
    # Calculate summary statistics
    total_time = time.time() - start_time
    success_count = len(successful_lessons)
    failure_count = len(failed_lessons)
    db_save_count = len(saved_to_db)
    success_rate = (success_count / len(topics)) * 100 if topics else 0
    db_save_rate = (db_save_count / success_count) * 100 if success_count > 0 else 0
    
    # Generate summary report
    print("=" * 60)
    print(f"📊 LESSON GENERATION SUMMARY FOR {target_language.upper()}")
    print("=" * 60)
    print(f"Total topics: {len(topics)}")
    print(f"Successful generations: {success_count}")
    print(f"Failed generations: {failure_count}")
    print(f"Generation success rate: {success_rate:.1f}%")
    if save_to_db:
        print(f"Saved to database: {db_save_count}")
        print(f"Database save rate: {db_save_rate:.1f}%")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Average time per lesson: {total_time/len(topics):.1f} seconds")
    
    if failed_lessons:
        print(f"\n❌ Failed lessons ({len(failed_lessons)}):")
        for fail in failed_lessons:
            print(f"  - Lesson {fail['lesson_number']}: {fail['topic']}")
            print(f"    Error: {fail['error'][:100]}...")
    
    # Save comprehensive summary report
    summary_data = {
        "generation_summary": {
            "target_language": target_language,
            "total_topics": len(topics),
            "successful_generations": success_count,
            "failed_generations": failure_count,
            "generation_success_rate": success_rate,
            "saved_to_database": db_save_count if save_to_db else 0,
            "database_save_rate": db_save_rate if save_to_db else 0,
            "total_time_minutes": total_time / 60,
            "average_time_per_lesson_seconds": total_time / len(topics),
            "generated_at": datetime.now().isoformat(),
            "database_enabled": save_to_db
        },
        "lesson_results": results,
        "failed_lessons": failed_lessons
    }
    
    # Save summary to a logs directory
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = f"{logs_dir}/{target_language.lower()}_generation_summary_{timestamp}.json"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 Summary saved to: {summary_file}")
    
    if save_to_db:
        print(f"🗄️  {db_save_count} lessons saved to database")
        
        # Show final database state
        db_final = SessionLocal()
        try:
            final_lessons = crud.get_desi_lessons_by_language(db_final, target_language)
            print(f"📊 Total lessons in DB for {target_language}: {len(final_lessons)}")
        finally:
            db_final.close()
    
    print(f"\n🎉 Generation complete! {success_count}/{len(topics)} lessons generated successfully")
    
    return summary_data

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: python generate_all_lessons.py <target_language> [delay_seconds] [--no-database]")
        print("Examples:")
        print("  python generate_all_lessons.py Telugu")
        print("  python generate_all_lessons.py Hindi 3")
        print("  python generate_all_lessons.py Kannada 2 --no-database")
        print("\nBy default, lessons are saved to the database.")
        print("Use --no-database to disable database saving (generation only).")
        sys.exit(1)
    
    target_language = sys.argv[1]
    delay_seconds = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 2
    save_to_db = "--no-database" not in sys.argv
    
    print(f"🎯 Target Language: {target_language}")
    print(f"⏱️  Delay between lessons: {delay_seconds} seconds")
    print(f"🗄️  Save to database: {save_to_db}")
    print()
    
    # Run the async lesson generation
    asyncio.run(generate_all_lessons(target_language, save_to_db, delay_seconds))

if __name__ == "__main__":
    main()