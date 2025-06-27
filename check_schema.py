# check_schema.py
#
# This script connects to your events.db and prints the table structure.
# It helps diagnose mismatches between the code and the actual database schema.
# Place this file in your root project directory (smart-contract-monitor).

import sqlite3
import os # Import the os module

DATABASE_FILE = 'events.db'

def check_db_schema():
    """Connects to the database and prints the schema of the 'events' table."""
    try:
        # --- NEW DIAGNOSTIC CODE ---
        print(f"Running from directory: {os.getcwd()}")
        db_path = os.path.abspath(DATABASE_FILE)
        print(f"Looking for database at: {db_path}")
        # ---------------------------

        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        print(f"\n--- Checking schema for '{DATABASE_FILE}' ---")
        
        # Check if the 'events' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events';")
        if cursor.fetchone() is None:
            print("\nError: The 'events' table does not exist in the database.")
            print("This likely means the listener script has not run successfully yet or is creating the DB elsewhere.")
            return

        # Print the schema of the 'events' table
        print("\nSchema for 'events' table:")
        cursor.execute("PRAGMA table_info(events);")
        columns = cursor.fetchall()
        
        if not columns:
            print("Error: Could not retrieve schema for 'events' table.")
        else:
            print(f"{'ID':<5} {'Name':<20} {'Type':<15} {'Not Null':<10}")
            print("-" * 55)
            for col in columns:
                # col[0] is cid, col[1] is name, col[2] is type, col[5] is primary key flag
                print(f"{col[0]:<5} {col[1]:<20} {col[2]:<15} {'YES' if col[3] else 'NO':<10}")

    except sqlite3.Error as e:
        print(f"\nAn error occurred while connecting to the database: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == '__main__':
    check_db_schema()
