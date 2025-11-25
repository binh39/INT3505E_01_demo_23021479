"""
V2 Handler - Handles V2 API format and responses.
"""
from typing import Dict, Any, List, Optional
import hashlib


class V2Handler:
    """Handler for API Version 2."""
    
    @staticmethod
    def transform_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform V2 request to internal format.
        
        V2 uses: payment_token (or card_number for backward compat), amount, status
        """
        payment_token = request_data.get('payment_token')
        card_number = request_data.get('card_number')
        
        # Backward compatibility: if card_number provided but no token, generate token
        deprecation_warning = None
        if card_number and not payment_token:
            payment_token = V2Handler.generate_payment_token(card_number)
            deprecation_warning = "Using 'card_number' is deprecated. Please use 'payment_token' instead."
        
        status = request_data.get('status', 'SUCCESS')
        code = V2Handler._get_status_code(status)
        
        return {
            'amount': request_data.get('amount'),
            'payment_token': payment_token,
            'card_number': card_number,
            'status': status,
            'status_code': code,
            'code': code,
            '_deprecation_warning': deprecation_warning
        }
    
    @staticmethod
    def transform_response(payment_record: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Transform internal data to V2 response format.
        
        V2 returns: id, amount, payment_token, status, code, created_at
        (NO transaction_id, NO card_number)
        """
        if payment_record is None:
            return None
        
        return {
            'id': payment_record['id'],
            'amount': payment_record['amount'],
            'payment_token': payment_record.get('payment_token'),
            'status': payment_record['status'],
            'code': payment_record.get('code', payment_record.get('status_code', 200)),
            'created_at': payment_record['created_at']
        }
    
    @staticmethod
    def transform_response_list(payment_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform list of records to V2 format."""
        return [V2Handler.transform_response(record) for record in payment_records]
    
    @staticmethod
    def format_success_response(data: Any, message: str, code: int = 200, 
                               deprecation_warning: Optional[str] = None) -> Dict[str, Any]:
        """
        Format V2 success response.
        
        V2 Response Structure:
        {
            "code": 200,
            "message": "...",
            "data": {...},
            "deprecation_warning": "..." (optional)
        }
        """
        response = {
            'code': code,
            'message': message,
            'data': data
        }
        
        if deprecation_warning:
            response['deprecation_warning'] = deprecation_warning
        
        return response
    
    @staticmethod
    def format_error_response(message: str, code: int = 400) -> Dict[str, Any]:
        """Format V2 error response."""
        return {
            'code': code,
            'message': message,
            'data': None
        }
    
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
