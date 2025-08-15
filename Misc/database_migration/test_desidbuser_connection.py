#!/usr/bin/env python3
"""
Test Oracle wallet connection with DESIDBUSER credentials
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def test_desidbuser_connection():
    """Test connection with DESIDBUSER credentials"""
    
    # Set up environment
    wallet_location = "/home/ashwin/projects/oracle_conn/desidb_wallet"
    wallet_password = "Adbwallet@2025"
    os.environ["TNS_ADMIN"] = wallet_location
    
    # Database credentials
    username = "DESIDBUSER"
    password = "g4RJX2sVhRtGFxw"
    
    print("Oracle Wallet Connection Test - DESIDBUSER")
    print("=" * 50)
    print(f"Wallet Location: {wallet_location}")
    print(f"TNS_ADMIN: {os.environ.get('TNS_ADMIN')}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}")
    
    # Test different TNS aliases
    aliases_to_test = ["desidb_high", "desidb_medium", "desidb_low"]
    
    for alias in aliases_to_test:
        print(f"\n--- Testing {alias} ---")
        
        connection_string = f"oracle+cx_oracle://{username}:{password}@{alias}"
        
        try:
            # Create engine with wallet password
            engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                echo=False,
                connect_args={
                    "encoding": "UTF-8",
                    "nencoding": "UTF-8",
                    "wallet_password": wallet_password
                }
            )
            
            # Test connection
            with engine.connect() as connection:
                # Test basic connection
                result = connection.execute(text("SELECT 'Connection successful!' as message FROM dual"))
                message = result.fetchone()[0]
                print(f"✓ {message}")
                
                # Get database info
                result = connection.execute(text("SELECT sys_context('USERENV', 'DB_NAME') as db_name FROM dual"))
                db_name = result.fetchone()[0]
                print(f"✓ Database: {db_name}")
                
                # Check current user
                result = connection.execute(text("SELECT user FROM dual"))
                current_user = result.fetchone()[0]
                print(f"✓ Connected as: {current_user}")
                
                # Check service name  
                result = connection.execute(text("SELECT sys_context('USERENV', 'SERVICE_NAME') as service FROM dual"))
                service = result.fetchone()[0]
                print(f"✓ Service: {service}")
                
                # Check session info
                result = connection.execute(text("SELECT sys_context('USERENV', 'SESSION_USER') as session_user FROM dual"))
                session_user = result.fetchone()[0]
                print(f"✓ Session user: {session_user}")
                
                # Check available tables
                result = connection.execute(text("SELECT COUNT(*) FROM user_tables"))
                table_count = result.fetchone()[0]
                print(f"✓ Tables in schema: {table_count}")
                
                # Check table creation privileges
                try:
                    result = connection.execute(text("""
                        SELECT privilege 
                        FROM user_sys_privs 
                        WHERE privilege IN ('CREATE TABLE', 'CREATE SEQUENCE', 'CREATE INDEX')
                        ORDER BY privilege
                    """))
                    privileges = [row[0] for row in result.fetchall()]
                    if privileges:
                        print(f"✓ Privileges: {', '.join(privileges)}")
                    else:
                        print("! No CREATE privileges found - checking role privileges...")
                        
                        # Check role privileges
                        result = connection.execute(text("""
                            SELECT granted_role 
                            FROM user_role_privs 
                            ORDER BY granted_role
                        """))
                        roles = [row[0] for row in result.fetchall()]
                        if roles:
                            print(f"✓ Roles: {', '.join(roles)}")
                        
                except Exception as e:
                    print(f"! Could not check privileges: {e}")
                
                # Try to check if any existing DesiLanguage tables exist
                try:
                    result = connection.execute(text("""
                        SELECT table_name 
                        FROM user_tables 
                        WHERE table_name LIKE 'DESI_%' 
                        OR table_name LIKE 'USER_%'
                        ORDER BY table_name
                    """))
                    desi_tables = [row[0] for row in result.fetchall()]
                    if desi_tables:
                        print(f"✓ Existing DesiLanguage tables: {', '.join(desi_tables)}")
                    else:
                        print("ℹ No existing DesiLanguage tables found")
                except Exception as e:
                    print(f"! Could not check existing tables: {e}")
                
                print(f"✅ {alias} connection successful!")
                
        except SQLAlchemyError as e:
            print(f"❌ {alias} connection failed: {e}")
            continue
        except Exception as e:
            print(f"❌ {alias} unexpected error: {e}")
            continue
    
    return True

def test_application_config():
    """Test application configuration with DESIDBUSER"""
    print("\n" + "=" * 50)
    print("Testing Application Configuration")
    print("=" * 50)
    
    try:
        # Set environment variables
        os.environ["DB_URL"] = "oracle+cx_oracle://DESIDBUSER:g4RJX2sVhRtGFxw@desidb_high"
        os.environ["WALLET_LOCATION"] = "/home/ashwin/projects/oracle_conn/desidb_wallet"
        os.environ["WALLET_PASSWORD"] = "Adbwallet@2025"
        os.environ["TNS_ALIAS"] = "desidb_high"
        
        from app.utils.config import settings
        from app.utils.database import engine
        
        print(f"✓ Configuration loaded")
        print(f"✓ Uses wallet: {settings.uses_wallet}")
        print(f"✓ Is Oracle: {settings.is_oracle}")
        print(f"✓ Wallet location: {settings.WALLET_LOCATION}")
        print(f"✓ TNS alias: {settings.TNS_ALIAS}")
        
        # Test actual application database connection
        print("\nTesting application database engine...")
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 'App connection successful!' as message FROM dual"))
            message = result.fetchone()[0]
            print(f"✅ {message}")
            
            # Check if we can run migrations
            result = connection.execute(text("""
                SELECT table_name 
                FROM user_tables 
                WHERE table_name = 'ALEMBIC_VERSION'
            """))
            alembic_table = result.fetchall()
            if alembic_table:
                print("✓ Alembic version table exists")
            else:
                print("ℹ No Alembic version table - ready for initial migration")
        
        return True
        
    except Exception as e:
        print(f"❌ Application configuration test failed: {e}")
        return False

if __name__ == "__main__":
    print("DesiLanguage Oracle Connection Test - DESIDBUSER\n")
    
    # Test direct connection
    test_desidbuser_connection()
    
    # Test application configuration
    test_application_config()
    
    print("\n" + "=" * 50)
    print("Connection test completed!")
    print("\nIf connections are successful:")
    print("1. Update .env with DESIDBUSER credentials")
    print("2. Run: alembic upgrade oracle_001")
    print("3. Run: python run.py")
    print("\nRecommended .env configuration:")
    print("DB_URL=oracle+cx_oracle://DESIDBUSER:g4RJX2sVhRtGFxw@desidb_high")
    print("WALLET_LOCATION=/home/ashwin/projects/oracle_conn/desidb_wallet")
    print("WALLET_PASSWORD=Adbwallet@2025")
    print("TNS_ALIAS=desidb_high")