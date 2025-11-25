"""
V1 Handler - Handles V1 API format and responses.
"""
from typing import Dict, Any, List, Optional


class V1Handler:
    """Handler for API Version 1."""
    
    @staticmethod
    def transform_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform V1 request to internal format.
        
        V1 uses: card_number, amount, status
        """
        status = request_data.get('status', 'SUCCESS')
        status_code = V1Handler._get_status_code(status)
        
        return {
            'amount': request_data.get('amount'),
            'card_number': request_data.get('card_number'),
            'payment_token': None,  # V1 doesn't use tokens
            'status': status,
            'status_code': status_code,
            'code': status_code
        }
    
    @staticmethod
    def transform_response(payment_record: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Transform internal data to V1 response format.
        
        V1 returns: id, transaction_id, amount, card_number, status, created_at
        """
        if payment_record is None:
            return None
        
        return {
            'id': payment_record['id'],
            'transaction_id': payment_record.get('transaction_id'),
            'amount': payment_record['amount'],
            'card_number': payment_record.get('card_number'),
            'status': payment_record['status'],
            'created_at': payment_record['created_at']
        }
    
    @staticmethod
    def transform_response_list(payment_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform list of records to V1 format."""
        return [V1Handler.transform_response(record) for record in payment_records]
    
    @staticmethod
    def format_success_response(data: Any, message: str, status_code: int = 200) -> Dict[str, Any]:
        """
        Format V1 success response.
        
        V1 Response Structure:
        {
            "status_code": 200,
            "message": "...",
            "data": {...}
        }
        """
        return {
            'status_code': status_code,
            'message': message,
            'data': data
        }
    
    @staticmethod
    def format_error_response(message: str, status_code: int = 400) -> Dict[str, Any]:
        """Format V1 error response."""
        return {
            'status_code': status_code,
            'message': message,
            'data': None
        }
    
    @staticmethod
    def _get_status_code(status: str) -> int:
        """Map status string to status code."""
        status_map = {
            'SUCCESS': 200,
            'PENDING': 202,
            'FAILED': 400
        }
        return status_map.get(status.upper(), 200)
