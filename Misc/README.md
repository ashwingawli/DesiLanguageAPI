# Miscellaneous Files

This folder contains various files created during development, migrations, and testing that are not part of the main application but may be useful for reference or debugging.

## Directory Structure

### `/database_migration/`
- **Oracle database setup and migration scripts**
- Connection testing utilities
- User creation and table setup scripts
- Database schema creation tools

Files:
- `create_missing_tables.py` - Script to create missing database tables
- `create_oracle_schema.py` - Oracle schema creation script
- `create_oracle_users.py` - Oracle user management script
- `drop_tables.py` - Utility to drop database tables
- `fix_existing_users.py` - Script to fix user data inconsistencies
- `test_*.py` - Various database connection test scripts

### `/database_migration/models_backup/`
- **Backup of database models**
- `models_postgresql_backup.py` - Backup of PostgreSQL-specific models

### `/documentation/`
- **Setup and migration guides**
- `GOOGLE_TTS_SETUP.md` - Google Text-to-Speech setup instructions
- `ORACLE_MIGRATION_GUIDE.md` - Guide for migrating to Oracle database
- `ORACLE_WALLET_SETUP.md` - Oracle Wallet configuration guide

### `/summaries/`
- **Analysis and testing summaries**
- `admin_lesson_access_summary.md` - Admin access functionality summary
- `enhanced_api_fix_summary.md` - API enhancement and bug fix summary
- `frontend_integration_test.md` - Frontend integration testing results
- `test_frontend_lesson_flow.md` - Lesson flow testing documentation

### `/credentials/`
- **Test credentials and access information**
- `ADMIN_CREDENTIALS.md` - Admin user credentials for testing
- `USER_CREDENTIALS.md` - Test user credentials

### `/reference_implementations/`
- **Reference code and implementations**
- `desi_lesson_generate_GeminiService.ts` - TypeScript reference implementation

## Notes

- **Credentials**: Files in `/credentials/` contain test credentials and should be kept secure
- **Migration Scripts**: Files in `/database_migration/` were used during Oracle migration and may be needed for future database maintenance
- **Documentation**: Setup guides in `/documentation/` contain important configuration information
- **Testing**: Files in `/summaries/` document testing results and may be useful for troubleshooting

## Usage

These files are primarily for reference and maintenance purposes. The main application does not depend on any files in this directory.