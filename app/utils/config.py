from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DB_URL: str
    GEMINI_API_KEY: str
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    SESSION_SECRET_KEY: str = "your-session-secret-key-change-in-production"
    
    # PostgreSQL Performance Settings (enhanced from Oracle migration learnings)
    PG_POOL_SIZE: int = 20  # Larger than Oracle due to better concurrency handling
    PG_MAX_OVERFLOW: int = 30  # PostgreSQL handles more connections efficiently
    PG_POOL_RECYCLE: int = 3600  # 1 hour connection recycling
    PG_POOL_PRE_PING: bool = True  # Health checks on connection retrieve
    PG_POOL_TIMEOUT: int = 30  # Connection timeout
    
    # PostgreSQL Query Performance
    PG_STATEMENT_TIMEOUT: int = 30000  # 30 seconds for statement timeout
    PG_ECHO_POOL: bool = False  # Set to True for connection pool debugging
    PG_ECHO_SQL: bool = False  # Set to True for SQL query debugging
    
    class Config:
        env_file = ".env"
        extra = "ignore"
    
    @property
    def db_url(self) -> str:
        return self.DB_URL
    
    @property
    def gemini_api_key(self) -> str:
        return self.GEMINI_API_KEY
    
    @property
    def is_postgresql(self) -> bool:
        """Check if the configured database is PostgreSQL"""
        return "postgresql" in self.DB_URL.lower()
    
    @property
    def get_pg_connection_params(self) -> dict:
        """Get optimized PostgreSQL connection parameters"""
        return {
            'pool_size': self.PG_POOL_SIZE,
            'max_overflow': self.PG_MAX_OVERFLOW,
            'pool_recycle': self.PG_POOL_RECYCLE,
            'pool_pre_ping': self.PG_POOL_PRE_PING,
            'pool_timeout': self.PG_POOL_TIMEOUT,
            'echo': self.PG_ECHO_SQL,
            'echo_pool': self.PG_ECHO_POOL,
            'connect_args': {
                'options': f'-c statement_timeout={self.PG_STATEMENT_TIMEOUT}ms',
                'application_name': 'DesiLanguage-API'
            }
        }

settings = Settings()