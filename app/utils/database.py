from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.utils.config import settings
import logging

# Enhanced PostgreSQL database configuration with Oracle migration insights
# Applying performance best practices learned from Oracle migration

# Set up logging for database performance monitoring
db_logger = logging.getLogger('database')

def optimize_postgresql_connection(dbapi_conn, connection_record):
    """Apply PostgreSQL-specific optimizations per connection"""
    try:
        with dbapi_conn.cursor() as cursor:
            # Set application name for monitoring
            cursor.execute("SET application_name = 'DesiLanguage-API'")
            # Commit the connection-level settings
            dbapi_conn.commit()
    except Exception as e:
        # Log but don't fail on optimization errors
        db_logger.warning(f"Connection optimization failed: {str(e)}")

# Create optimized PostgreSQL engine with insights from Oracle migration
pg_params = settings.get_pg_connection_params

engine = create_engine(
    settings.db_url,
    # Enhanced connection pooling (learned from Oracle pool optimization)
    poolclass=QueuePool,
    pool_size=pg_params['pool_size'],
    max_overflow=pg_params['max_overflow'], 
    pool_recycle=pg_params['pool_recycle'],
    pool_pre_ping=pg_params['pool_pre_ping'],
    pool_timeout=pg_params['pool_timeout'],
    
    # Enhanced performance settings
    echo=pg_params['echo'],
    echo_pool=pg_params['echo_pool'],
    
    # PostgreSQL-specific optimizations
    connect_args=pg_params['connect_args'],
    
    # Execution options for better performance
    execution_options={
        "isolation_level": "READ_COMMITTED",
        "postgresql_readonly": False,
        "postgresql_deferrable": False,
    }
)

# Apply connection-level optimizations
event.listen(engine, "connect", optimize_postgresql_connection)

# Create session factory with optimized settings
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    # Expire on commit for better cache performance
    expire_on_commit=False
)

# Database connection pool monitoring (inspired by Oracle pool monitoring)
def get_pool_status():
    """Get PostgreSQL connection pool status for monitoring"""
    try:
        pool = engine.pool
        return {
            "status": "active",
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def get_db():
    """Dependency to get database session with enhanced error handling"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db_logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

# Health check function for database connectivity
def check_db_health():
    """Check database health and connectivity"""
    try:
        from sqlalchemy import text
        db = SessionLocal()
        # Simple query to test connectivity
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        db_logger.error(f"Database health check failed: {str(e)}")
        return False

# Database initialization and cleanup functions
def init_db():
    """Initialize database with optimal settings"""
    try:
        # Import models to ensure they're registered
        from app.models import models
        
        # Create tables if they don't exist
        models.Base.metadata.create_all(bind=engine)
        
        db_logger.info("✅ PostgreSQL database initialized successfully")
        db_logger.info(f"Pool configuration: {get_pool_status()}")
        
    except Exception as e:
        db_logger.error(f"❌ Database initialization failed: {str(e)}")
        raise

def close_db():
    """Clean shutdown of database connections"""
    try:
        engine.dispose()
        db_logger.info("✅ Database connections closed successfully")
    except Exception as e:
        db_logger.error(f"❌ Error closing database connections: {str(e)}")

# Create declarative base
Base = declarative_base()

# Export key components
__all__ = [
    'engine', 
    'SessionLocal', 
    'Base', 
    'get_db', 
    'get_pool_status', 
    'check_db_health',
    'init_db', 
    'close_db'
]