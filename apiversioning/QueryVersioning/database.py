"""
Database module for QueryVersioning project.
Independent SQLite database for query parameter versioning demo.
"""
import sqlite3
import os
import hashlib


DB_PATH = 'payments_query.db'


def get_db_connection():
    """Get a connection to the QueryVersioning database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with the payments table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            amount REAL NOT NULL,
            card_number TEXT,
            payment_token TEXT,
            status TEXT NOT NULL,
            status_code INTEGER,
            code INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"QueryVersioning database initialized: {DB_PATH}")


def seed_sample_data():
    """Seed the database with sample payment data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM payments')
    if cursor.fetchone()[0] > 0:
        print("ℹDatabase already contains data. Skipping seed.")
        conn.close()
        return
    
    # Sample data
    sample_data = [
        ('TXN-001', 100.50, '4532-1111-2222-3333', 'SUCCESS', 200),
        ('TXN-002', 250.00, '5500-0000-0000-0004', 'PENDING', 102),
        ('TXN-003', 75.25, '3400-0000-0000-009', 'SUCCESS', 200),
        ('TXN-004', 500.00, '6011-0000-0000-0004', 'REFUND', 204),
    ]
    
    for txn_id, amount, card, status, status_code in sample_data:
        # Generate payment token
        token = hashlib.sha256(card.encode()).hexdigest()[:32].upper()
        payment_token = f"TOK-{token}"
        
        cursor.execute('''
            INSERT INTO payments (transaction_id, amount, card_number, payment_token, status, status_code, code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (txn_id, amount, card, payment_token, status, status_code, status_code))
    
    conn.commit()
    conn.close()
    print(f"Seeded database with {len(sample_data)} sample payments")


if __name__ == '__main__':
    init_db()
    seed_sample_data()
