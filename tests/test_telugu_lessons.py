#!/usr/bin/env python3
"""
Test script to generate all lesson topics for Telugu language
"""
import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.gemini_service import gemini_service
from app.schemas import DesiLessonRequest

async def test_telugu_lessons():
    """Generate lessons for all topics in Telugu"""
    
    # Load lesson topics
    with open('Lesson_topics.txt', 'r') as f:
        topics = [line.strip() for line in f.readlines() if line.strip()]
    
    print(f"Found {len(topics)} lesson topics")
    print("Starting Telugu lesson generation...\n")
    
    results = []
    
    for i, topic in enumerate(topics, 1):
        print(f"Generating Lesson {i}: {topic}")
        
        try:
            # Generate lesson
            lesson_response = await gemini_service.generate_desi_lesson(
                target_language="Telugu",
                lesson_topic=topic
            )
            
            print(f"✅ Successfully generated: {lesson_response.desi_lesson.title}")
            
            # Store result
            results.append({
                "lesson_number": i,
                "topic": topic,
                "status": "success",
                "title": lesson_response.desi_lesson.title,
                "vocabulary_count": len(lesson_response.desi_lesson.vocabulary),
                "sentences_count": len(lesson_response.desi_lesson.example_sentences),
                "quiz_count": len(lesson_response.desi_lesson.quiz)
            })
            
            # Save individual lesson to file
            with open(f'telugu_lesson_{i:02d}_{topic.replace(" ", "_").replace(":", "").replace("&", "and")}.json', 'w', encoding='utf-8') as f:
                json.dump(lesson_response.dict(), f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"❌ Failed to generate lesson for '{topic}': {str(e)}")
            results.append({
                "lesson_number": i,
                "topic": topic,
                "status": "failed",
                "error": str(e)
            })
        
        print()  # Empty line for readability
    
    # Generate summary report
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]
    
    print("=" * 60)
    print("TELUGU LESSON GENERATION SUMMARY")
    print("=" * 60)
    print(f"Total topics: {len(topics)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Success rate: {len(successful)/len(topics)*100:.1f}%")
    
    if failed:
        print("\nFailed lessons:")
        for fail in failed:
            print(f"  - Lesson {fail['lesson_number']}: {fail['topic']}")
            print(f"    Error: {fail['error'][:100]}...")
    
    # Save summary report
    with open('telugu_lessons_summary.json', 'w') as f:
        json.dump({
            "summary": {
                "total": len(topics),
                "successful": len(successful),
                "failed": len(failed),
                "success_rate": len(successful)/len(topics)*100
            },
            "results": results
        }, f, indent=2)
    
    print(f"\nSummary saved to: telugu_lessons_summary.json")
    print("Individual lessons saved as: telugu_lesson_XX_*.json")

if __name__ == "__main__":
    asyncio.run(test_telugu_lessons())