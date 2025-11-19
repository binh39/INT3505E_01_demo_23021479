"""
V1 Adapter - Handles request/response formatting and business logic orchestration for V1 API.
Uses V1Transformer for data transformation.
"""
from typing import Dict, Any, List, Optional
from transformers.v1_transformer import V1Transformer


class V1Adapter:
    """Adapter for API Version 1"""
    
    def __init__(self):
        self.transformer = V1Transformer()
    
    def transform_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform V1 request using V1Transformer.
        Delegates to transformer for data conversion.
        """
        return self.transformer.transform_request(request_data)
    
    def transform_response(self, payment_record: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Transform single payment record to V1 format.
        Returns None if payment_record is None.
        """
        if payment_record is None:
            return None
        return self.transformer.transform_response(payment_record)
    
    def transform_response_list(self, payment_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform list of payment records to V1 format."""
        return self.transformer.transform_response_list(payment_records)
    
    @staticmethod
    def format_success_response(data: Any, message: str, status_code: int = 200) -> Dict[str, Any]:
        """
        Format V1 success response.
        
        V1 Response Structure:
        {
            "status_code": 200,
            "message": "Success message",
            "data": {...},
            "links": {...}
        }
        """
        return {
            'status_code': status_code,
            'message': message,
            'data': data,
            'links': V1Adapter.generate_links()
        }
    
    @staticmethod
    def format_error_response(message: str, status_code: int = 400) -> Dict[str, Any]:
        """
        Format V1 error response.
        
        V1 Error Structure:
        {
            "status_code": 400,
            "message": "Error message",
            "data": None,
            "links": {...}
        }
        """
        return {
            'status_code': status_code,
            'message': message,
            'data': None,
            'links': V1Adapter.generate_links()
        }
    
    @staticmethod
    def generate_links(payment_id: Optional[int] = None) -> Dict[str, str]:
        """
        Generate HATEOAS links for V1 API.
        
        Args:
            payment_id: Optional payment ID for specific resource links
        
        Returns:
            Dictionary of hypermedia links
        """
        base_url = '/api/v1/payments'
        links = {
            'self': base_url if payment_id is None else f"{base_url}/{payment_id}",
            'collection': base_url
        }
        if payment_id is not None:
            links['delete'] = f"{base_url}/{payment_id}"
        return links
