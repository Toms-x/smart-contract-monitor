import sqlite3
import json

DB_FILE = 'events.db'  # local file to store events

# Connect to SQLite DB and create table if not exists
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Save an event (as JSON string) into the DB
def save_event(event):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    event_json = json.dumps(event)
    cursor.execute('INSERT INTO events (event_data) VALUES (?)', (event_json,))
    conn.commit()
    conn.close()
