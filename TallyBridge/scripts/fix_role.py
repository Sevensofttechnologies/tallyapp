import sqlite3
import os

db_path = 'app.db'
email = 'ganeshachavan@gmail.com'

def fix_role():
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Check current state
    cursor.execute("SELECT id, email, role FROM users WHERE email=?", (email,))
    row = cursor.fetchone()
    print(f"Before Update: {row}")
    
    if row:
        # 2. Force update
        cursor.execute("UPDATE users SET role='super_admin' WHERE email=?", (email,))
        conn.commit()
        print("Update command executed and committed.")
        
        # 3. Verify
        cursor.execute("SELECT id, email, role FROM users WHERE email=?", (email,))
        new_row = cursor.fetchone()
        print(f"After Update: {new_row}")
    else:
        print(f"User {email} not found in database.")
        
    conn.close()

if __name__ == "__main__":
    fix_role()
