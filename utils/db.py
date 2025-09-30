# utils/db.py

import sqlite3

DATABASE_FILE = 'events.db'

def init_db():
    """
    Initializes the database and creates the 'events' table with a new,
    structured schema if it doesn't already exist.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # SQL command to create the table with separate columns for each data point
    # This makes querying much more efficient and straightforward.
    create_table_query = """
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tx_hash TEXT NOT NULL UNIQUE,
        blockNumber INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        from_address TEXT NOT NULL,
        to_address TEXT NOT NULL,
        value REAL NOT NULL,
        tokenSymbol TEXT NOT NULL
    );
    """
    
    cursor.execute(create_table_query)
    
    # You might want to create an index for faster lookups by block number or timestamp
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_blockNumber ON events (blockNumber);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON events (timestamp);")

    conn.commit()
    conn.close()
    print("Database initialized successfully with the new schema.")


def save_event(event_data):
    """
    Saves a single structured event dictionary into the database.
    
    :param event_data: A dictionary containing the event details.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # The new INSERT statement uses named placeholders for each column.
    insert_query = """
    INSERT INTO events (
        tx_hash, 
        blockNumber, 
        timestamp, 
        from_address, 
        to_address, 
        value, 
        tokenSymbol
    ) VALUES (
        :tx_hash, 
        :blockNumber, 
        :timestamp, 
        :from_address, 
        :to_address, 
        :value, 
        :tokenSymbol
    );
    """
    
    try:
        # The second argument to execute is the dictionary of data.
        # The keys in the dictionary must match the named placeholders in the query.
        cursor.execute(insert_query, event_data)
        conn.commit()
    except sqlite3.IntegrityError:
        # This will happen if you try to insert a transaction hash that already exists.
        # It's safe to ignore as it just means the event was processed before.
        print(f"Event with tx_hash {event_data['tx_hash']} already exists. Skipping.")
    except Exception as e:
        print(f"Error saving event to database: {e}")
    finally:
        conn.close()