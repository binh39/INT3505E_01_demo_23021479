"""
V2 Adapter - Handles request/response formatting and business logic orchestration for V2 API.
Uses V2Transformer for data transformation.
"""
from typing import Dict, Any, List, Optional
from transformers.v2_transformer import V2Transformer


class V2Adapter:
    """Adapter for API Version 2"""
    
    def __init__(self):
        self.transformer = V2Transformer()
    
    def transform_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform V2 request using V2Transformer.
        Handles backward compatibility for card_number.
        """
        transformed = self.transformer.transform_request(request_data)
        
        # Add deprecation warning if card_number is used
        transformed['_deprecation_warning'] = None
        if 'card_number' in request_data and not request_data.get('payment_token'):
            transformed['_deprecation_warning'] = (
                "Using 'card_number' is deprecated. Please use 'payment_token' instead."
            )
        
        return transformed
    
    def transform_response(self, payment_record: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Transform single payment record to V2 format.
        Returns None if payment_record is None.
        """
        if payment_record is None:
            return None
        return self.transformer.transform_response(payment_record)
    
    def transform_response_list(self, payment_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform list of payment records to V2 format."""
        return self.transformer.transform_response_list(payment_records)
    
    @staticmethod
    def format_success_response(data: Any, message: str, code: int = 200, 
                               deprecation_warning: Optional[str] = None) -> Dict[str, Any]:
        """
        Format V2 success response.
        
        V2 Response Structure:
        {
            "code": 200,
            "message": "Success message",
            "data": {...},
            "links": {...},
            "deprecation_warning": "..." (optional)
        }
        """
        response = {
            'code': code,
            'message': message,
            'data': data,
            'links': V2Adapter.generate_links()
        }
        
        if deprecation_warning:
            response['deprecation_warning'] = deprecation_warning
        
        return response
    
    @staticmethod
    def format_error_response(message: str, code: int = 400) -> Dict[str, Any]:
        """
        Format V2 error response.
        
        V2 Error Structure:
        {
            "code": 400,
            "message": "Error message",
            "data": None,
            "links": {...}
        }
        """
        return {
            'code': code,
            'message': message,
            'data': None,
            'links': V2Adapter.generate_links()
        }
    
    @staticmethod
    def generate_links(transaction_id: Optional[int] = None) -> Dict[str, str]:
        """
        Generate HATEOAS links for V2 API.
        
        Args:
            transaction_id: Optional transaction ID for specific resource links
        
        Returns:
            Dictionary of hypermedia links
        """
        base_url = '/api/v2/transactions'
        links = {
            'self': base_url if transaction_id is None else f"{base_url}/{transaction_id}",
            'collection': base_url
        }
        if transaction_id is not None:
            links['delete'] = f"{base_url}/{transaction_id}"
        return links
