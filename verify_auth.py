import sqlite3
import os
import bcrypt
import time
from database import init_db, get_db_connection

def test_database_creation():
    print("TEST: Database Initialization...")
    if os.path.exists("db.sqlite"):
        try:
            os.remove("db.sqlite")
            print("  - Removed existing db.sqlite for clean test.")
        except Exception as e:
            print(f"  - Warning: Could not remove db.sqlite: {e}")

    if init_db():
        print("  - init_db() returned True.")
        if os.path.exists("db.sqlite"):
            print("  - PASS: db.sqlite created.")
        else:
            print("  - FAIL: db.sqlite not found after init.")
    else:
        print("  - FAIL: init_db() returned False.")

def test_user_registration():
    print("\nTEST: User Registration (Direct DB)...")
    username = "testuser"
    email = "test@example.com"
    password = "password123"

    conn = get_db_connection()
    if not conn:
        print("  - FAIL: Could not connect to DB.")
        return

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        print(f"  - Inserted user '{username}'.")
    except Exception as e:
        print(f"  - FAIL: Insert failed: {e}")
    finally:
        conn.close()

    # Verify insertion
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        print(f"  - PASS: User '{username}' found in DB.")
        print(f"  - ID: {user['id']}")
        print(f"  - Email: {user['email']}")
    else:
        print("  - FAIL: User not found in DB.")

def test_user_duplicates():
    print("\nTEST: Duplicate Handling...")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            ("testuser", "test@example.com", b"dummyhash")
        )
        conn.commit()
        print("  - FAIL: Duplicate insert should have raised IntegrityError.")
    except sqlite3.IntegrityError:
        print("  - PASS: Duplicate insert raised IntegrityError as expected.")
    except Exception as e:
        print(f"  - FAIL: Unexpected error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print(f"--- STARTING VERIFICATION ---")
    test_database_creation()
    test_user_registration()
    test_user_duplicates()
    print(f"--- VERIFICATION COMPLETE ---")
