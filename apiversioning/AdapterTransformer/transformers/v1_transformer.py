"""
V1 Transformer - Transforms data between internal format and V1 API format.
Handles V1-specific data structure (transaction_id, card_number, status_code).
"""
from typing import Dict, Any, List
from .base_transformer import BaseTransformer


class V1Transformer(BaseTransformer):
    """Transformer for V1 API format."""
    
    def transform_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform V1 request to internal format.
        
        V1 Request:
        {
            "amount": 100.0,
            "card_number": "4111-1111-1111-1111",
            "status": "SUCCESS"
        }
        
        Internal Format:
        {
            "amount": 100.0,
            "card_number": "4111-1111-1111-1111",
            "payment_token": None,
            "status": "SUCCESS",
            "status_code": 200,
            "code": 200
        }
        """
        status = request_data.get('status', 'SUCCESS')
        status_code = self._get_status_code(status)
        
        return {
            'amount': request_data.get('amount'),
            'card_number': request_data.get('card_number'),
            'payment_token': None,  # V1 doesn't use tokens
            'status': status,
            'status_code': status_code,
            'code': status_code
        }
    
    def transform_response(self, payment_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform internal data to V1 response format.
        
        Internal Data:
        {
            "id": 1,
            "transaction_id": "TXN-ABC",
            "amount": 100.0,
            "card_number": "4111-1111-1111-1111",
            "payment_token": "TOK-XYZ",
            "status": "SUCCESS",
            "status_code": 200,
            "code": 200,
            "created_at": "2024-01-01 12:00:00"
        }
        
        V1 Response:
        {
            "id": 1,
            "transaction_id": "TXN-ABC",
            "amount": 100.0,
            "card_number": "4111-1111-1111-1111",
            "status": "SUCCESS",
            "created_at": "2024-01-01 12:00:00"
        }
        """
        return {
            'id': payment_record['id'],
            'transaction_id': payment_record.get('transaction_id'),
            'amount': payment_record['amount'],
            'card_number': payment_record.get('card_number'),
            'status': payment_record['status'],
            'created_at': payment_record['created_at']
        }
    
    def transform_response_list(self, payment_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform list of records to V1 format."""
        return [self.transform_response(record) for record in payment_records]
    
    @staticmethod
    def _get_status_code(status: str) -> int:
        """Map status string to status code."""
        status_map = {
            'SUCCESS': 200,
            'PENDING': 202,
            'FAILED': 400
        }
        return status_map.get(status.upper(), 200)
