import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'payments.db'

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with the payments table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE NOT NULL,
            amount REAL NOT NULL,
            card_number TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('SUCCESS', 'PENDING', 'REFUND')),
            status_code INTEGER NOT NULL,
            code INTEGER,
            payment_token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def migrate_db():
    """Migrate existing database to add new columns for v2."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if columns exist, if not add them
    cursor.execute("PRAGMA table_info(payments)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'code' not in columns:
        cursor.execute('ALTER TABLE payments ADD COLUMN code INTEGER')
        print("Added 'code' column")
    
    if 'payment_token' not in columns:
        cursor.execute('ALTER TABLE payments ADD COLUMN payment_token TEXT')
        print("Added 'payment_token' column")
    
    # Migrate existing data: copy status_code to code
    cursor.execute('UPDATE payments SET code = status_code WHERE code IS NULL')
    
    conn.commit()
    conn.close()
    print("Database migration completed successfully!")

if __name__ == '__main__':
    init_db()
    migrate_db()
