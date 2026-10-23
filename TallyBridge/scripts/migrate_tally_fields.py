"""
Migration Script: Add Tally Integration Fields to Companies Table
Run this script to add tally_guid, tally_server, tally_port, last_sync_at, last_alter_id columns

Usage:
    python scripts/migrate_tally_fields.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from app.config import settings


def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in the table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def migrate():
    """Add Tally integration fields to companies table"""
    
    print("=" * 60)
    print("TallyBridge - Database Migration")
    print("Adding Tally Integration Fields to Companies Table")
    print("=" * 60)
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Define new columns to add
    new_columns = [
        ("tally_guid", "VARCHAR(100) UNIQUE"),
        ("tally_server", "VARCHAR(100) DEFAULT 'localhost'"),
        ("tally_port", "INTEGER DEFAULT 9000"),
        ("last_sync_at", "DATETIME"),
        ("last_alter_id", "INTEGER DEFAULT 0"),
    ]
    
    with engine.connect() as conn:
        for column_name, column_type in new_columns:
            if check_column_exists(engine, 'companies', column_name):
                print(f"[SKIP] Column '{column_name}' already exists")
            else:
                try:
                    # SQLite uses different syntax
                    if 'sqlite' in settings.DATABASE_URL:
                        sql = f"ALTER TABLE companies ADD COLUMN {column_name} {column_type}"
                    else:
                        sql = f"ALTER TABLE companies ADD COLUMN {column_name} {column_type}"
                    
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"[DONE] Added column '{column_name}'")
                except Exception as e:
                    print(f"[ERROR] Failed to add column '{column_name}': {e}")
    
    print("=" * 60)
    print("Migration completed!")
    print("=" * 60)
    
    # Verify columns
    print("\nVerifying columns in 'companies' table:")
    inspector = inspect(engine)
    columns = inspector.get_columns('companies')
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")


if __name__ == "__main__":
    migrate()
