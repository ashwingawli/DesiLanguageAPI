#!/usr/bin/env python3
"""
Test script for Oracle Autonomous Database wallet connection
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def test_wallet_connection():
    """Test Oracle wallet connection"""
    
    # Set up environment variables
    wallet_location = "/home/ashwin/projects/oracle_conn/desidb_wallet"
    os.environ["TNS_ADMIN"] = wallet_location
    
    print("Oracle Wallet Connection Test")
    print("=" * 50)
    print(f"Wallet Location: {wallet_location}")
    print(f"TNS_ADMIN: {os.environ.get('TNS_ADMIN')}")
    
    # Check if wallet files exist
    required_files = ["tnsnames.ora", "sqlnet.ora", "cwallet.sso", "ewallet.p12"]
    missing_files = []
    
    for file in required_files:
        file_path = os.path.join(wallet_location, file)
        if os.path.exists(file_path):
            print(f"✓ {file} found")
        else:
            print(f"✗ {file} missing")
            missing_files.append(file)
    
    if missing_files:
        print(f"\nError: Missing wallet files: {missing_files}")
        return False
    
    # Test connection with different TNS aliases
    tns_aliases = ["desidb_high", "desidb_medium", "desidb_low"]
    
    for alias in tns_aliases:
        print(f"\nTesting connection to {alias}...")
        
        # You'll need to replace with actual credentials
        username = input(f"Enter username for {alias} (default: ADMIN): ").strip() or "ADMIN"
        password = input(f"Enter password for {username}: ").strip()
        
        if not password:
            print("Password required. Skipping...")
            continue
        
        connection_string = f"oracle+cx_oracle://{username}:{password}@{alias}"
        
        try:
            # Create engine with wallet password support
            connect_args = {
                "encoding": "UTF-8",
                "nencoding": "UTF-8"
            }
            
            # Add wallet password if available
            wallet_password = "Adbwallet@2025"  # Your wallet password
            if wallet_password:
                connect_args["wallet_password"] = wallet_password
            
            engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                echo=False,
                connect_args=connect_args
            )
            
            # Test connection
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 'Connection successful!' as message FROM dual"))
                message = result.fetchone()[0]
                print(f"✓ {alias}: {message}")
                
                # Get database info
                result = connection.execute(text("SELECT sys_context('USERENV', 'DB_NAME') as db_name FROM dual"))
                db_name = result.fetchone()[0]
                print(f"  Database: {db_name}")
                
                # Check if we can see the schemas/tables
                result = connection.execute(text("SELECT COUNT(*) FROM user_tables"))
                table_count = result.fetchone()[0]
                print(f"  Tables in schema: {table_count}")
                
        except SQLAlchemyError as e:
            print(f"✗ {alias}: Connection failed")
            print(f"  Error: {e}")
        except Exception as e:
            print(f"✗ {alias}: Unexpected error")
            print(f"  Error: {e}")
    
    return True

def test_application_config():
    """Test application configuration with wallet"""
    print("\nTesting Application Configuration...")
    print("=" * 50)
    
    try:
        # Set environment for testing
        os.environ["WALLET_LOCATION"] = "/home/ashwin/projects/oracle_conn/desidb_wallet"
        os.environ["TNS_ALIAS"] = "desidb_high"
        
        from app.utils.config import settings
        
        print(f"Wallet location configured: {settings.uses_wallet}")
        print(f"Wallet path: {settings.WALLET_LOCATION}")
        print(f"TNS Alias: {settings.TNS_ALIAS}")
        print(f"Database type: {'Oracle' if settings.is_oracle else 'Other'}")
        
        # Test connection string generation
        if settings.uses_wallet:
            test_conn_str = settings.get_wallet_connection_string("testuser", "testpass")
            print(f"Generated connection string: {test_conn_str}")
        
        return True
        
    except Exception as e:
        print(f"Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    print("DesiLanguage Oracle Wallet Connection Test\n")
    
    # Test wallet files
    if not test_wallet_connection():
        sys.exit(1)
    
    # Test application configuration
    if not test_application_config():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Connection test completed!")
    print("\nTo use the wallet connection:")
    print("1. Copy .env.desidb to .env")
    print("2. Update the ADMIN password in .env")
    print("3. Update GEMINI_API_KEY in .env")
    print("4. Run: python run.py")