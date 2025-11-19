"""
Database module for AdapterTransformer project.
This is a standalone database, independent from the main Routes project.
"""
import sqlite3
import os
from datetime import datetime

# Database path - independent from Routes project
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'payments_adapter.db')


def get_db_connection():
    """Get a connection to the AdapterTransformer database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialize the database with the payments table.
    This creates a new independent database for the AdapterTransformer project.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create payments table with all fields to support both v1 and v2
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
    print(f"✅ AdapterTransformer database initialized: {DB_PATH}")


def seed_sample_data():
    """Seed the database with sample payment data for testing."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM payments')
    if cursor.fetchone()[0] > 0:
        print("⚠️  Database already contains data. Skipping seed.")
        conn.close()
        return
    
    # Sample data
    sample_payments = [
        {
            'transaction_id': 'TXN-2024-001',
            'amount': 150.00,
            'card_number': '4111-1111-1111-1111',
            'payment_token': 'TOK-a1b2c3d4e5f6',
            'status': 'SUCCESS',
            'status_code': 200,
            'code': 200
        },
        {
            'transaction_id': 'TXN-2024-002',
            'amount': 250.50,
            'card_number': '5500-0000-0000-0004',
            'payment_token': 'TOK-x7y8z9w0v1u2',
            'status': 'SUCCESS',
            'status_code': 200,
            'code': 200
        },
        {
            'transaction_id': 'TXN-2024-003',
            'amount': 99.99,
            'card_number': '3400-0000-0000-009',
            'payment_token': 'TOK-m3n4o5p6q7r8',
            'status': 'PENDING',
            'status_code': 202,
            'code': 202
        }
    ]
    
    for payment in sample_payments:
        cursor.execute('''
            INSERT INTO payments (transaction_id, amount, card_number, payment_token, status, status_code, code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            payment['transaction_id'],
            payment['amount'],
            payment['card_number'],
            payment['payment_token'],
            payment['status'],
            payment['status_code'],
            payment['code']
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(sample_payments)} sample payments")


def reset_db():
    """Reset the database by dropping and recreating tables."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️  Removed old database: {DB_PATH}")
    
    init_db()
    seed_sample_data()


if __name__ == '__main__':
    """Run this script to initialize or reset the database."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_db()
    else:
        init_db()
        seed_sample_data()
