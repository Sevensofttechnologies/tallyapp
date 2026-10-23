"""Create mst_company table manually"""
import sqlite3

conn = sqlite3.connect('TallyInsight/tally.db')
cursor = conn.cursor()

# Create mst_company table
cursor.execute("""
CREATE TABLE IF NOT EXISTS mst_company (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    _company TEXT NOT NULL UNIQUE,
    guid TEXT NOT NULL DEFAULT '',
    alter_id INTEGER NOT NULL DEFAULT 0,
    name TEXT NOT NULL DEFAULT '',
    formal_name TEXT NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT '',
    state TEXT NOT NULL DEFAULT '',
    country TEXT NOT NULL DEFAULT '',
    pincode TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    mobile TEXT NOT NULL DEFAULT '',
    telephone TEXT NOT NULL DEFAULT '',
    website TEXT NOT NULL DEFAULT '',
    gstin TEXT NOT NULL DEFAULT '',
    pan TEXT NOT NULL DEFAULT '',
    tan TEXT NOT NULL DEFAULT '',
    cin TEXT NOT NULL DEFAULT '',
    books_from TEXT,
    books_to TEXT,
    starting_from TEXT,
    currency TEXT NOT NULL DEFAULT 'INR',
    decimal_places INTEGER NOT NULL DEFAULT 2,
    maintain_inventory INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
print("mst_company table created successfully!")

# Verify
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mst_company'")
result = cursor.fetchone()
if result:
    print(f"Table exists: {result[0]}")
else:
    print("Table NOT created!")

conn.close()
