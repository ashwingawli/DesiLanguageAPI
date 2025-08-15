#!/usr/bin/env python3
"""
Simple test for Oracle wallet connection with password
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def test_connection():
    """Test Oracle wallet connection with password"""
    
    # Set up environment
    wallet_location = "/home/ashwin/projects/oracle_conn/desidb_wallet"
    wallet_password = "Adbwallet@2025"
    os.environ["TNS_ADMIN"] = wallet_location
    
    print("Oracle Wallet Connection Test (with password)")
    print("=" * 50)
    print(f"Wallet Location: {wallet_location}")
    print(f"Wallet Password: {'*' * len(wallet_password)}")
    print(f"TNS_ADMIN: {os.environ.get('TNS_ADMIN')}")
    
    # Get database credentials
    username = input("Enter database username (default: ADMIN): ").strip() or "ADMIN"
    password = input(f"Enter password for {username}: ").strip()
    
    if not password:
        print("Password required!")
        return False
    
    # Test connection with wallet password
    connection_string = f"oracle+cx_oracle://{username}:{password}@desidb_high"
    
    try:
        print("\nTesting connection...")
        
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
            print(f"✓ Connected to database: {db_name}")
            
            # Check current user
            result = connection.execute(text("SELECT user FROM dual"))
            current_user = result.fetchone()[0]
            print(f"✓ Connected as user: {current_user}")
            
            # Check service name
            result = connection.execute(text("SELECT sys_context('USERENV', 'SERVICE_NAME') as service FROM dual"))
            service = result.fetchone()[0]
            print(f"✓ Service: {service}")
            
            # Check if we can create tables (for migrations)
            try:
                connection.execute(text("SELECT COUNT(*) FROM user_tables"))
                print("✓ Can access user tables")
                
                # Check if we have create table privileges
                result = connection.execute(text("""
                    SELECT privilege 
                    FROM user_sys_privs 
                    WHERE privilege = 'CREATE TABLE'
                """))
                if result.fetchone():
                    print("✓ Has CREATE TABLE privilege")
                else:
                    print("! No CREATE TABLE privilege found")
                    
            except Exception as e:
                print(f"! Could not check table privileges: {e}")
        
        print("\n✅ Connection test successful!")
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        print("\n🎉 Your Oracle wallet connection is working!")
        print("\nNext steps:")
        print("1. Copy .env.desidb to .env")
        print("2. Update the ADMIN password in .env")
        print("3. Add your GEMINI_API_KEY to .env")
        print("4. Run: alembic upgrade oracle_001")
        print("5. Run: python run.py")
    else:
        print("\n❌ Connection test failed. Please check your configuration.")