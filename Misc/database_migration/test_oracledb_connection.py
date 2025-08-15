#!/usr/bin/env python3
"""
Test Oracle wallet connection with DESIDBUSER credentials using oracledb (thin mode)
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def test_oracledb_connection():
    """Test connection with DESIDBUSER credentials using oracledb thin mode"""
    
    # Set up environment
    wallet_location = "/home/ashwin/projects/oracle_conn/desidb_wallet"
    os.environ["TNS_ADMIN"] = wallet_location
    
    # Database credentials
    username = "DESIDBUSER"
    password = "g4RJX2sVhRtGFxw"
    
    print("Oracle Wallet Connection Test - DESIDBUSER (using oracledb)")
    print("=" * 60)
    print(f"Wallet Location: {wallet_location}")
    print(f"TNS_ADMIN: {os.environ.get('TNS_ADMIN')}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}")
    
    # Test different connection methods and aliases
    connection_tests = [
        # Method 1: oracledb with TNS alias
        ("oracledb (TNS)", "oracle+oracledb://", "desidb_high"),
        ("oracledb (TNS)", "oracle+oracledb://", "desidb_medium"),
        # Method 2: Direct connection string (for comparison)
        ("oracledb (Direct)", "oracle+oracledb://", "adb.ap-hyderabad-1.oraclecloud.com:1522/gae164f8549ae26_desidb_high.adb.oraclecloud.com"),
    ]
    
    for method, prefix, connection_target in connection_tests:
        print(f"\n--- Testing {method}: {connection_target} ---")
        
        connection_string = f"{prefix}{username}:{password}@{connection_target}"
        
        try:
            # Create engine with wallet configuration
            connect_args = {
                "config_dir": wallet_location,  # For wallet location
                "wallet_location": wallet_location,
                "wallet_password": "Adbwallet@2025"
            }
            
            engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                echo=False,
                connect_args=connect_args
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
                
                # Check available tables
                result = connection.execute(text("SELECT COUNT(*) FROM user_tables"))
                table_count = result.fetchone()[0]
                print(f"✓ Tables in schema: {table_count}")
                
                # Check privileges
                try:
                    result = connection.execute(text("""
                        SELECT privilege 
                        FROM user_sys_privs 
                        WHERE privilege IN ('CREATE TABLE', 'CREATE SEQUENCE', 'CREATE INDEX')
                        ORDER BY privilege
                    """))
                    privileges = [row[0] for row in result.fetchall()]
                    if privileges:
                        print(f"✓ System privileges: {', '.join(privileges)}")
                    
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
                
                print(f"✅ {method} connection successful!")
                return True  # Return after first successful connection
                
        except SQLAlchemyError as e:
            print(f"❌ {method} connection failed: {e}")
            continue
        except Exception as e:
            print(f"❌ {method} unexpected error: {e}")
            continue
    
    return False

def test_pure_oracledb():
    """Test with pure oracledb (no SQLAlchemy) to isolate issues"""
    print(f"\n--- Testing Pure oracledb Connection ---")
    
    try:
        import oracledb
        
        # Set wallet location
        wallet_location = "/home/ashwin/projects/oracle_conn/desidb_wallet"
        os.environ["TNS_ADMIN"] = wallet_location
        
        # Try thin mode connection
        print("Testing oracledb thin mode...")
        
        # Connect using TNS alias
        connection = oracledb.connect(
            user="DESIDBUSER",
            password="g4RJX2sVhRtGFxw",
            dsn="desidb_high",
            config_dir=wallet_location,
            wallet_location=wallet_location,
            wallet_password="Adbwallet@2025"
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT 'Pure oracledb connection successful!' FROM dual")
        result = cursor.fetchone()
        print(f"✓ {result[0]}")
        
        # Get database info
        cursor.execute("SELECT sys_context('USERENV', 'DB_NAME') FROM dual")
        db_name = cursor.fetchone()[0]
        print(f"✓ Database: {db_name}")
        
        cursor.close()
        connection.close()
        
        print("✅ Pure oracledb connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Pure oracledb connection failed: {e}")
        return False

if __name__ == "__main__":
    print("DesiLanguage Oracle Connection Test - DESIDBUSER (oracledb driver)\n")
    
    # Test pure oracledb first
    pure_success = test_pure_oracledb()
    
    # Test SQLAlchemy with oracledb
    sqlalchemy_success = test_oracledb_connection()
    
    print("\n" + "=" * 60)
    print("Connection test results:")
    print(f"Pure oracledb: {'✅ SUCCESS' if pure_success else '❌ FAILED'}")
    print(f"SQLAlchemy + oracledb: {'✅ SUCCESS' if sqlalchemy_success else '❌ FAILED'}")
    
    if pure_success or sqlalchemy_success:
        print("\n🎉 DESIDBUSER connection successful!")
        print("\nRecommended configuration for .env:")
        print("DB_URL=oracle+oracledb://DESIDBUSER:g4RJX2sVhRtGFxw@desidb_high")
        print("WALLET_LOCATION=/home/ashwin/projects/oracle_conn/desidb_wallet")
        print("WALLET_PASSWORD=Adbwallet@2025")
        print("TNS_ALIAS=desidb_high")
    else:
        print("\n❌ All connection tests failed.")
        print("Please check:")
        print("1. Oracle wallet files are accessible")
        print("2. TNS_ADMIN environment variable")
        print("3. Network connectivity to Oracle Cloud")
        print("4. User credentials are correct")