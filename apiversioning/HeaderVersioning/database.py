"""
Database module for HeaderVersioning project.
Independent SQLite database for header-based versioning demo.
"""
import sqlite3
import os


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'payments_header.db')


def get_db_connection():
    """Get a connection to the HeaderVersioning database."""
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
    print(f"HeaderVersioning database initialized: {DB_PATH}")


def seed_sample_data():
    """Seed the database with sample payment data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM payments')
    if cursor.fetchone()[0] > 0:
        print("Database already contains data. Skipping seed.")
        conn.close()
        return
    
    sample_payments = [
        {
            'transaction_id': 'TXN-HDR-001',
            'amount': 175.50,
            'card_number': '4111-1111-1111-1111',
            'payment_token': 'TOK-h1d2r3v4e5r6',
            'status': 'SUCCESS',
            'status_code': 200,
            'code': 200
        },
        {
            'transaction_id': 'TXN-HDR-002',
            'amount': 325.00,
            'card_number': '5500-0000-0000-0004',
            'payment_token': 'TOK-a7b8c9d0e1f2',
            'status': 'SUCCESS',
            'status_code': 200,
            'code': 200
        },
        {
            'transaction_id': 'TXN-HDR-003',
            'amount': 89.99,
            'card_number': '3400-0000-0000-009',
            'payment_token': 'TOK-x3y4z5w6v7u8',
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
    print(f"Seeded {len(sample_payments)} sample payments")


def reset_db():
    """Reset the database by dropping and recreating tables."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️  Removed old database: {DB_PATH}")
    
    init_db()
    seed_sample_data()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_db()
    else:
        init_db()
        seed_sample_data()
