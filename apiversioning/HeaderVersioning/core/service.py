"""
Payment Service - Core business logic for HeaderVersioning.
Version-agnostic service layer.
"""
from typing import List, Dict, Any, Optional
from .database import get_db_connection
import hashlib
import uuid


class PaymentService:
    """Service layer for payment business logic."""
    
    @staticmethod
    def get_all_payments() -> List[Dict[str, Any]]:
        """Retrieve all payments from the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payments ORDER BY created_at DESC')
        payments = cursor.fetchall()
        conn.close()
        return [dict(payment) for payment in payments]
    
    @staticmethod
    def get_payment_by_id(payment_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific payment by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cursor.fetchone()
        conn.close()
        return dict(payment) if payment else None
    
    @staticmethod
    def create_payment(amount: float, card_number: Optional[str] = None, 
                      payment_token: Optional[str] = None, status: str = 'SUCCESS') -> Dict[str, Any]:
        """Create a new payment record."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        transaction_id = f"TXN-{str(uuid.uuid4())[:12].upper()}"
        status_code = PaymentService._get_status_code(status)
        
        cursor.execute('''
            INSERT INTO payments (transaction_id, amount, card_number, payment_token, status, status_code, code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (transaction_id, amount, card_number, payment_token, status, status_code, status_code))
        
        conn.commit()
        payment_id = cursor.lastrowid
        
        cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cursor.fetchone()
        conn.close()
        
        return dict(payment)
    
    @staticmethod
    def delete_payment(payment_id: int) -> bool:
        """Delete a payment by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM payments WHERE id = ?', (payment_id,))
        if cursor.fetchone() is None:
            conn.close()
            return False
        
        cursor.execute('DELETE FROM payments WHERE id = ?', (payment_id,))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def generate_payment_token(card_number: str) -> str:
        """Generate a secure payment token from card number."""
        card_clean = card_number.replace('-', '').replace(' ', '')
        hash_obj = hashlib.sha256(card_clean.encode())
        token = hash_obj.hexdigest()[:12].upper()
        return f"TOK-{token}"
    
    @staticmethod
    def _get_status_code(status: str) -> int:
        """Map status string to HTTP status code."""
        status_map = {
            'SUCCESS': 200,
            'PENDING': 202,
            'FAILED': 400
        }
        return status_map.get(status.upper(), 200)
