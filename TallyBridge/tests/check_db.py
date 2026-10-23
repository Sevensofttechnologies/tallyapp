"""
Database Check Script
Check tables, data, and audit logs
"""
import sqlite3
import os

# Find database file
db_path = "app.db"
if not os.path.exists(db_path):
    db_path = "data/app.db"
    if not os.path.exists(db_path):
        print("ERROR: Database file not found!")
        exit(1)

print(f"Database: {db_path}")
print("=" * 60)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
print("\n=== TABLES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
for t in tables:
    print(f"  - {t[0]}")

print("\n" + "=" * 60)

# Check each table for data
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\n=== {table_name.upper()} ({count} records) ===")
    
    if count > 0:
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Columns: {', '.join(columns)}")
        
        # Show first 5 records
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = cursor.fetchall()
        print(f"\nSample Data (first {min(5, count)} records):")
        for row in rows:
            print(f"  {row}")

# Check for audit_log table specifically
print("\n" + "=" * 60)
print("\n=== AUDIT LOG CHECK ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%audit%'")
audit_tables = cursor.fetchall()
if audit_tables:
    print(f"Audit tables found: {[t[0] for t in audit_tables]}")
else:
    print("No audit log table found in database!")
    print("Audit logging may need to be implemented.")

conn.close()
print("\n" + "=" * 60)
