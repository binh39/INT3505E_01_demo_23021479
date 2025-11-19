"""
V2 Transformer - Transforms data between internal format and V2 API format.
Handles V2-specific data structure (no transaction_id, payment_token, code field).
"""
from typing import Dict, Any, List
from .base_transformer import BaseTransformer
import hashlib


class V2Transformer(BaseTransformer):
    """Transformer for V2 API format."""
    
    def transform_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform V2 request to internal format.
        
        V2 Request (preferred):
        {
            "amount": 100.0,
            "payment_token": "TOK-ABC123",
            "status": "SUCCESS"
        }
        
        V2 Request (backward compatible):
        {
            "amount": 100.0,
            "card_number": "4111-1111-1111-1111",
            "status": "SUCCESS"
        }
        
        Internal Format:
        {
            "amount": 100.0,
            "payment_token": "TOK-ABC123",
            "card_number": None or "4111...",
            "status": "SUCCESS",
            "code": 200
        }
        """
        payment_token = request_data.get('payment_token')
        card_number = request_data.get('card_number')
        
        # Backward compatibility: if card_number provided but no token, generate token
        if card_number and not payment_token:
            payment_token = self.generate_payment_token(card_number)
        
        status = request_data.get('status', 'SUCCESS')
        code = self._get_status_code(status)
        
        return {
            'amount': request_data.get('amount'),
            'payment_token': payment_token,
            'card_number': card_number,  # Store for backward compat
            'status': status,
            'status_code': code,  # For DB compatibility
            'code': code
        }
    
    def transform_response(self, payment_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform internal data to V2 response format.
        
        Internal Data:
        {
            "id": 1,
            "transaction_id": "TXN-ABC",
            "amount": 100.0,
            "card_number": "4111-1111-1111-1111",
            "payment_token": "TOK-XYZ",
            "status": "SUCCESS",
            "code": 200,
            "created_at": "2024-01-01 12:00:00"
        }
        
        V2 Response:
        {
            "id": 1,
            "amount": 100.0,
            "payment_token": "TOK-XYZ",
            "status": "SUCCESS",
            "code": 200,
            "created_at": "2024-01-01 12:00:00"
        }
        """
        return {
            'id': payment_record['id'],
            'amount': payment_record['amount'],
            'payment_token': payment_record.get('payment_token'),
            'status': payment_record['status'],
            'code': payment_record.get('code', payment_record.get('status_code', 200)),
            'created_at': payment_record['created_at']
        }
    
    def transform_response_list(self, payment_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform list of records to V2 format."""
        return [self.transform_response(record) for record in payment_records]
    
    @staticmethod
    def generate_payment_token(card_number: str) -> str:
        """Generate a payment token from card number using SHA256."""
        card_clean = card_number.replace('-', '').replace(' ', '')
        hash_obj = hashlib.sha256(card_clean.encode())
        token = hash_obj.hexdigest()[:12].upper()
        return f"TOK-{token}"
    
    @staticmethod
    def _get_status_code(status: str) -> int:
        """Map status string to status code."""
        status_map = {
            'SUCCESS': 200,
            'PENDING': 202,
            'FAILED': 400
        }
        return status_map.get(status.upper(), 200)
