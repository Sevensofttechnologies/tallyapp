"""
Check TallyInsight Database Schema
"""
import sqlite3

conn = sqlite3.connect('tally.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("TallyInsight Database Tables:")
print("-" * 40)
for t in tables:
    print(f"  - {t[0]}")

conn.close()
