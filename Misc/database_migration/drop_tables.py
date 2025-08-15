#!/usr/bin/env python3
"""
Drop existing Oracle tables script
"""

import os
from sqlalchemy import create_engine, text

def drop_existing_tables():
    """Drop all existing Oracle tables"""
    
    # Set up environment
    wallet_location = "/home/ashwin/projects/oracle_conn/desidb_wallet"
    os.environ["TNS_ADMIN"] = wallet_location
    
    # Connection details
    username = "DESIDBUSER"
    password = "g4RJX2sVhRtGFxw"
    wallet_password = "Adbwallet@2025"
    
    print("Dropping existing tables...")
    
    try:
        engine = create_engine(
            f"oracle+oracledb://{username}:{password}@desidb_high",
            connect_args={
                "config_dir": wallet_location,
                "wallet_location": wallet_location,
                "wallet_password": wallet_password
            }
        )
        
        with engine.connect() as connection:
            # Get all existing user tables
            result = connection.execute(text("SELECT table_name FROM user_tables"))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"Found {len(tables)} existing tables to drop")
            
            # Drop all tables (disable foreign key checks by cascading)
            for table in tables:
                if table != "ALEMBIC_VERSION":  # Keep Alembic version table
                    try:
                        connection.execute(text(f"DROP TABLE {table} CASCADE CONSTRAINTS"))
                        print(f"✓ Dropped table: {table}")
                    except Exception as e:
                        print(f"• Could not drop table {table}: {e}")
            
            # Drop all sequences
            result = connection.execute(text("SELECT sequence_name FROM user_sequences"))
            sequences = [row[0] for row in result.fetchall()]
            
            for seq in sequences:
                try:
                    connection.execute(text(f"DROP SEQUENCE {seq}"))
                    print(f"✓ Dropped sequence: {seq}")
                except Exception as e:
                    print(f"• Could not drop sequence {seq}: {e}")
            
            connection.commit()
            print("✅ Cleanup completed successfully!")
            
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

if __name__ == "__main__":
    drop_existing_tables()