from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    db_url: str
    gemini_api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()