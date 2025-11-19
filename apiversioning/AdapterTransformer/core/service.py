"""
Payment Service - Core business logic layer for payment operations.
This service is version-agnostic and handles all database operations.
"""
from typing import List, Dict, Any, Optional
from core.database import get_db_connection
import hashlib


class PaymentService:
    """Service layer for payment business logic."""
    
    @staticmethod
    def get_all_payments() -> List[Dict[str, Any]]:
        """
        Retrieve all payments from the database.
        
        Returns:
            List of payment records as dictionaries
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payments ORDER BY created_at DESC')
        payments = cursor.fetchall()
        conn.close()
        
        # Convert Row objects to dictionaries
        return [dict(payment) for payment in payments]
    
    @staticmethod
    def get_payment_by_id(payment_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific payment by ID.
        
        Args:
            payment_id: The ID of the payment to retrieve
            
        Returns:
            Payment record as dictionary, or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cursor.fetchone()
        conn.close()
        
        return dict(payment) if payment else None
    
    @staticmethod
    def create_payment(amount: float, card_number: Optional[str] = None, 
                      payment_token: Optional[str] = None, status: str = 'SUCCESS') -> Dict[str, Any]:
        """
        Create a new payment record.
        
        Args:
            amount: Payment amount
            card_number: Card number (for v1 compatibility)
            payment_token: Payment token (for v2)
            status: Payment status (SUCCESS, PENDING, FAILED)
            
        Returns:
            Created payment record as dictionary
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate transaction_id for v1 compatibility
        transaction_id = PaymentService._generate_transaction_id()
        
        # Map status to codes
        status_code = PaymentService._get_status_code(status)
        
        cursor.execute('''
            INSERT INTO payments (transaction_id, amount, card_number, payment_token, status, status_code, code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (transaction_id, amount, card_number, payment_token, status, status_code, status_code))
        
        conn.commit()
        payment_id = cursor.lastrowid
        
        # Retrieve the created payment
        cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cursor.fetchone()
        conn.close()
        
        return dict(payment)
    
    @staticmethod
    def delete_payment(payment_id: int) -> bool:
        """
        Delete a payment by ID.
        
        Args:
            payment_id: The ID of the payment to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if payment exists
        cursor.execute('SELECT id FROM payments WHERE id = ?', (payment_id,))
        if cursor.fetchone() is None:
            conn.close()
            return False
        
        # Delete the payment
        cursor.execute('DELETE FROM payments WHERE id = ?', (payment_id,))
        conn.commit()
        conn.close()
        
        return True
    
    @staticmethod
    def generate_payment_token(card_number: str) -> str:
        """
        Generate a secure payment token from card number using SHA256.
        
        Args:
            card_number: Card number to tokenize
            
        Returns:
            Payment token string (format: TOK-XXXXXXXXXXXX)
        """
        # Remove dashes and spaces
        card_clean = card_number.replace('-', '').replace(' ', '')
        
        # Generate SHA256 hash
        hash_obj = hashlib.sha256(card_clean.encode())
        token = hash_obj.hexdigest()[:12].upper()
        
        return f"TOK-{token}"
    
    @staticmethod
    def _generate_transaction_id() -> str:
        """
        Generate a unique transaction ID.
        
        Returns:
            Transaction ID string (format: TXN-XXXXXXXXXXXX)
        """
        import uuid
        unique_id = str(uuid.uuid4())[:12].upper()
        return f"TXN-{unique_id}"
    
    @staticmethod
    def _get_status_code(status: str) -> int:
        """
        Map status string to HTTP status code.
        
        Args:
            status: Status string (SUCCESS, PENDING, FAILED)
            
        Returns:
            HTTP status code
        """
        status_map = {
            'SUCCESS': 200,
            'PENDING': 202,
            'FAILED': 400
        }
        return status_map.get(status.upper(), 200)
