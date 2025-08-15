"""
Lesson parser for reading Lessons_n_themes.txt file
"""
from typing import List, Dict, Optional
import os

class LessonParser:
    def __init__(self, file_path: str = "Lessons_title.txt"):
        self.file_path = file_path
        self._lessons_cache = None
    
    def parse_lessons_file(self) -> List[Dict[str, str]]:
        """
        Parse Lessons_title.txt file and return list of lessons with titles
        
        Returns:
            List of dictionaries with 'title' and 'theme' keys (theme will be same as title)
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Lessons file not found: {self.file_path}")
        
        lessons = []
        
        with open(self.file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                
                if line.startswith("Lesson Title:"):
                    # Extract title
                    title = line.replace("Lesson Title:", "").strip()
                    if title:
                        # Use title as both title and theme
                        lessons.append({"title": title, "theme": title})
        
        return lessons
    
    def get_lessons(self) -> List[Dict[str, str]]:
        """
        Get lessons with caching
        """
        if self._lessons_cache is None:
            self._lessons_cache = self.parse_lessons_file()
        return self._lessons_cache
    
    def get_lesson_by_title(self, title: str) -> Optional[Dict[str, str]]:
        """
        Get a specific lesson by title
        """
        lessons = self.get_lessons()
        for lesson in lessons:
            if lesson["title"] == title:
                return lesson
        return None
    
    def get_lesson_titles(self) -> List[str]:
        """
        Get list of all lesson titles
        """
        lessons = self.get_lessons()
        return [lesson["title"] for lesson in lessons]
    
    def get_lesson_count(self) -> int:
        """
        Get total number of lessons
        """
        return len(self.get_lessons())

# Global instance
lesson_parser = LessonParser()