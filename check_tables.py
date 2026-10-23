import sqlite3

conn = sqlite3.connect('TallyInsight/tally.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("All tables in database:")
for t in tables:
    print(f"  - {t[0]}")

# Check for company-related tables
print("\nCompany-related tables:")
for t in tables:
    if 'company' in t[0].lower():
        print(f"  - {t[0]}")

conn.close()
