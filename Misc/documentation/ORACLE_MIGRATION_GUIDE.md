# PostgreSQL to Oracle Migration Guide

This guide documents the conversion of the DesiLanguage application from PostgreSQL to Oracle Database.

## Overview

The migration involved updating database drivers, connection strings, SQL queries, schema definitions, and ORM configurations to be compatible with Oracle Database.

## Major Changes Summary

### 1. Dependencies and Drivers

#### Before (PostgreSQL)
```python
# requirements.txt
psycopg2-binary==2.9.9
asyncpg==0.29.0
```

#### After (Oracle)
```python
# requirements.txt  
cx-Oracle==8.3.0
oracledb==1.4.2
```

**Key Changes:**
- Replaced `psycopg2-binary` with `cx-Oracle` for synchronous connections
- Replaced `asyncpg` with `oracledb` for Oracle's native Python driver support

### 2. Database Connection Configuration

#### Before (PostgreSQL)
```python
# app/utils/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.utils.config import settings

engine = create_engine(settings.db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

#### After (Oracle)
```python
# app/utils/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.utils.config import settings

# Database engine configuration with Oracle-specific optimizations
if settings.is_oracle:
    # Oracle-specific engine configuration
    engine = create_engine(
        settings.db_url,
        pool_size=settings.ORACLE_POOL_SIZE,
        max_overflow=settings.ORACLE_MAX_OVERFLOW,
        pool_recycle=settings.ORACLE_POOL_RECYCLE,
        pool_pre_ping=True,
        echo=False,
        connect_args={
            "encoding": "UTF-8",
            "nencoding": "UTF-8"
        }
    )
else:
    # PostgreSQL or other database engines
    engine = create_engine(
        settings.db_url,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

**Key Changes:**
- Added Oracle-specific connection pool configuration
- Added UTF-8 encoding settings for Oracle
- Implemented database type detection for flexible deployment

### 3. Environment Configuration

#### Before (PostgreSQL)
```bash
# .env
DB_URL=postgresql://user:password@localhost:5432/desi_language_db
GEMINI_API_KEY=your_api_key
```

#### After (Oracle)
```bash
# .env.oracle.example
# Oracle Database Configuration
# Format: oracle+cx_oracle://user:password@host:port/?service_name=service
DB_URL=oracle+cx_oracle://your_user:your_password@localhost:1521/?service_name=XEPDB1

# Oracle-specific environment variables (optional)
ORACLE_HOME=/path/to/oracle/client
TNS_ADMIN=/path/to/tnsnames/directory
ORACLE_POOL_SIZE=5
ORACLE_MAX_OVERFLOW=10
ORACLE_POOL_RECYCLE=3600

GEMINI_API_KEY=your_gemini_api_key_here
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
```

**Key Changes:**
- Changed connection string format from PostgreSQL to Oracle
- Added Oracle-specific environment variables
- Added connection pool configuration options

### 4. SQLAlchemy Model Changes

#### Before (PostgreSQL)
```python
# app/models/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean, Float, Enum

class DesiLesson(Base):
    __tablename__ = "desi_lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    target_language = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)

class DesiDialogue(Base):
    __tablename__ = "desi_dialogue"
    
    id = Column(Integer, primary_key=True, index=True)
    speaker = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
```

#### After (Oracle)
```python
# app/models/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean, Float, Enum, Sequence

class DesiLesson(Base):
    __tablename__ = "desi_lessons"
    
    id = Column(Integer, Sequence('desi_lessons_id_seq'), primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    target_language = Column(String(100), nullable=False)
    difficulty = Column(String(50), nullable=False)

class DesiDialogue(Base):
    __tablename__ = "desi_dialogue"
    
    id = Column(Integer, Sequence('desi_dialogue_id_seq'), primary_key=True, index=True)
    speaker = Column(String(100), nullable=False)
    order_num = Column(Integer, nullable=False)  # 'order' is reserved in Oracle
```

**Key Changes:**
- Added `Sequence` import and usage for auto-increment primary keys
- Added explicit length constraints to `String` columns (Oracle requirement)
- Renamed `order` column to `order_num` (Oracle reserved word conflict)
- All string columns now have explicit length limits

### 5. Alembic Migration Changes

#### Before (PostgreSQL)
```python
# alembic/versions/xxx_migration.py
def upgrade() -> None:
    op.create_table('desi_lessons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
```

#### After (Oracle)
```python
# alembic/versions/oracle_001_initial_schema.py
def upgrade() -> None:
    # Create sequences for Oracle auto-increment
    op.execute("CREATE SEQUENCE desi_lessons_id_seq START WITH 1 INCREMENT BY 1")
    
    op.create_table('desi_lessons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_desi_lessons_id'), 'desi_lessons', ['id'], unique=False)
```

**Key Changes:**
- Added sequence creation for auto-increment columns
- Added explicit string lengths in migrations
- Included sequence cleanup in downgrade operations

### 6. Application Code Changes

#### Before (PostgreSQL)
```python
# app/api/crud.py
for d in sorted(db_lesson.short_story.dialogue, key=lambda x: x.order)

# Creating dialogue
db_dialogue = models.DesiDialogue(
    short_story_id=db_story.id,
    speaker=dialogue_item.speaker,
    order=i
)
```

#### After (Oracle)
```python
# app/api/crud.py  
for d in sorted(db_lesson.short_story.dialogue, key=lambda x: x.order_num)

# Creating dialogue
db_dialogue = models.DesiDialogue(
    short_story_id=db_story.id,
    speaker=dialogue_item.speaker,
    order_num=i
)
```

**Key Changes:**
- Updated field references from `order` to `order_num`
- No changes required to most business logic due to SQLAlchemy abstraction

## Connection String Examples

### Oracle Connection Formats

1. **Basic Connection:**
   ```
   oracle+cx_oracle://user:password@localhost:1521/?service_name=XEPDB1
   ```

2. **TNS Names Connection:**
   ```
   oracle+cx_oracle://user:password@tns_name
   ```

3. **Oracle Cloud (Autonomous Database):**
   ```
   oracle+cx_oracle://user:password@host:port/service_name?wallet_location=/path/to/wallet&wallet_password=wallet_password
   ```

## Oracle-Specific Considerations

### 1. Sequence Management
Oracle requires explicit sequence creation for auto-increment columns:

```sql
CREATE SEQUENCE table_name_id_seq START WITH 1 INCREMENT BY 1;
```

### 2. String Column Lengths
Oracle requires explicit length specifications for VARCHAR2 columns:

```python
# Required in Oracle
Column(String(255), nullable=False)

# Works in PostgreSQL but not Oracle  
Column(String, nullable=False)
```

### 3. Reserved Words
Oracle has more reserved words than PostgreSQL:
- `ORDER` → `ORDER_NUM`
- `LEVEL` → `USER_LEVEL` 
- `COMMENT` → `USER_COMMENT`

### 4. Case Sensitivity
Oracle converts unquoted identifiers to uppercase by default. SQLAlchemy handles this automatically.

### 5. Connection Pooling
Oracle benefits from connection pooling configuration:

```python
engine = create_engine(
    connection_string,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600
)
```

## Migration Steps

1. **Install Oracle Client Libraries**
   ```bash
   # Download and install Oracle Instant Client
   # Set ORACLE_HOME and TNS_ADMIN environment variables
   ```

2. **Update Dependencies**
   ```bash
   pip uninstall psycopg2-binary asyncpg
   pip install cx-Oracle oracledb
   ```

3. **Configure Database Connection**
   ```bash
   cp .env.oracle.example .env
   # Update DB_URL with your Oracle connection details
   ```

4. **Run Migrations**
   ```bash
   alembic upgrade oracle_001
   ```

5. **Test Application**
   ```bash
   python run.py
   ```

## Performance Considerations

### Oracle-Specific Optimizations

1. **Connection Pooling**: Configure appropriate pool sizes
2. **Sequence Caching**: Use sequence caching for high-volume inserts
3. **Index Strategy**: Oracle optimizer may prefer different indexing strategies
4. **Query Hints**: Oracle supports query hints for optimization
5. **PL/SQL**: Consider stored procedures for complex operations

### Monitoring and Tuning

1. **AWR Reports**: Use Oracle's Automatic Workload Repository
2. **SQL Tuning Advisor**: Oracle's built-in SQL optimization tool
3. **Execution Plans**: Monitor query execution plans
4. **Session Statistics**: Track database session metrics

## Backup and Recovery

### Oracle-Specific Backup Strategy

1. **RMAN Backups**: Use Oracle Recovery Manager
2. **Data Pump**: For logical backups and data migration
3. **Flashback**: Oracle's point-in-time recovery feature
4. **Archive Log Mode**: Ensure database is in archive log mode

## Troubleshooting

### Common Issues

1. **TNS-12154**: Cannot resolve connect identifier
   - Check TNS_ADMIN path and tnsnames.ora file

2. **ORA-00942**: Table or view does not exist
   - Verify schema name and object case sensitivity

3. **ORA-00001**: Unique constraint violated
   - Check for duplicate sequence values after data migration

4. **ORA-01400**: Cannot insert NULL into column
   - Verify NOT NULL constraints match application expectations

### Testing Checklist

- [ ] Database connection established
- [ ] All tables created successfully
- [ ] Sequences functioning correctly
- [ ] Foreign key constraints working
- [ ] Application CRUD operations functional
- [ ] Migration rollback tested
- [ ] Performance benchmarks within acceptable range
- [ ] Backup and recovery procedures tested

## Conclusion

The migration from PostgreSQL to Oracle requires attention to:
- Driver and dependency changes
- Connection string format differences  
- String length specifications
- Reserved word conflicts
- Sequence management for auto-increment columns
- Oracle-specific performance optimizations

The SQLAlchemy ORM abstracts most database differences, making the migration relatively straightforward once the configuration and schema issues are addressed.