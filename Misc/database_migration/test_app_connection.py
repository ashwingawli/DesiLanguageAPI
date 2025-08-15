#!/usr/bin/env python3
"""
Test DesiLanguage application with DESIDBUSER credentials
"""

import os
from sqlalchemy import text

def test_app_connection():
    """Test application with DESIDBUSER configuration"""
    
    # Set environment variables for testing
    os.environ["DB_URL"] = "oracle+oracledb://DESIDBUSER:g4RJX2sVhRtGFxw@desidb_high"
    os.environ["WALLET_LOCATION"] = "/home/ashwin/projects/oracle_conn/desidb_wallet"
    os.environ["WALLET_PASSWORD"] = "Adbwallet@2025"
    os.environ["TNS_ALIAS"] = "desidb_high"
    os.environ["GEMINI_API_KEY"] = "test_key"  # Placeholder for testing
    
    print("DesiLanguage Application Connection Test")
    print("=" * 50)
    print(f"DB_URL: oracle+oracledb://DESIDBUSER:***@desidb_high")
    print(f"WALLET_LOCATION: {os.environ['WALLET_LOCATION']}")
    print(f"TNS_ADMIN: {os.environ.get('TNS_ADMIN', 'Not set')}")
    
    try:
        # Import application modules
        from app.utils.config import settings
        from app.utils.database import engine
        
        print(f"\n✓ Configuration loaded successfully")
        print(f"✓ Uses wallet: {settings.uses_wallet}")
        print(f"✓ Is Oracle: {settings.is_oracle}")
        print(f"✓ Database URL configured: {settings.db_url.split('@')[1]}")  # Hide credentials
        
        # Test database engine
        print(f"\n--- Testing Database Engine ---")
        with engine.connect() as connection:
            # Basic connection test
            result = connection.execute(text("SELECT 'Application connection successful!' FROM dual"))
            message = result.fetchone()[0]
            print(f"✓ {message}")
            
            # Database info
            result = connection.execute(text("SELECT sys_context('USERENV', 'DB_NAME') FROM dual"))
            db_name = result.fetchone()[0]
            print(f"✓ Database: {db_name}")
            
            # Current user
            result = connection.execute(text("SELECT user FROM dual"))
            current_user = result.fetchone()[0]
            print(f"✓ Connected as: {current_user}")
            
            # Check for existing tables
            result = connection.execute(text("SELECT COUNT(*) FROM user_tables"))
            table_count = result.fetchone()[0]
            print(f"✓ Current tables in schema: {table_count}")
            
            # Check if Alembic version table exists
            result = connection.execute(text("""
                SELECT COUNT(*) FROM user_tables 
                WHERE table_name = 'ALEMBIC_VERSION'
            """))
            alembic_exists = result.fetchone()[0] > 0
            print(f"✓ Alembic version table exists: {alembic_exists}")
            
            # Test creating a simple table (and drop it)
            try:
                connection.execute(text("""
                    CREATE TABLE test_connection_table (
                        id NUMBER(10) PRIMARY KEY,
                        test_message VARCHAR2(100)
                    )
                """))
                print("✓ Can create tables")
                
                # Test insert
                connection.execute(text("""
                    INSERT INTO test_connection_table (id, test_message) 
                    VALUES (1, 'Connection test successful')
                """))
                print("✓ Can insert data")
                
                # Test select
                result = connection.execute(text("""
                    SELECT test_message FROM test_connection_table WHERE id = 1
                """))
                test_msg = result.fetchone()[0]
                print(f"✓ Can select data: {test_msg}")
                
                # Clean up
                connection.execute(text("DROP TABLE test_connection_table"))
                print("✓ Can drop tables")
                
                # Commit the transaction
                connection.commit()
                
            except Exception as e:
                print(f"! Table operations failed: {e}")
                # Try to clean up if table was created
                try:
                    connection.execute(text("DROP TABLE test_connection_table"))
                    connection.commit()
                except:
                    pass
        
        print("\n✅ Application connection test SUCCESSFUL!")
        print("\n🎉 Ready to run migrations and start the application!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Application connection test FAILED: {e}")
        return False

def show_next_steps():
    """Show next steps for running the application"""
    print("\n" + "=" * 50)
    print("NEXT STEPS")
    print("=" * 50)
    print("1. Copy the working configuration:")
    print("   cp .env.desidb .env")
    print("")
    print("2. Add your Gemini API key to .env:")
    print("   GEMINI_API_KEY=your_actual_gemini_api_key")
    print("")
    print("3. Run database migrations:")
    print("   source venv/bin/activate")
    print("   alembic upgrade oracle_001")
    print("")
    print("4. Start the application:")
    print("   python run.py")
    print("")
    print("5. Access the API at:")
    print("   http://localhost:8000")
    print("   http://localhost:8000/docs (Swagger UI)")

if __name__ == "__main__":
    print("DesiLanguage Application Connection Test - DESIDBUSER\n")
    
    success = test_app_connection()
    
    if success:
        show_next_steps()
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Ensure Oracle wallet files are accessible")
        print("2. Check TNS_ADMIN environment variable")
        print("3. Verify DESIDBUSER credentials")
        print("4. Test network connectivity to Oracle Cloud")