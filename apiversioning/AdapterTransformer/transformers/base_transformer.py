"""
Base Transformer for data transformations.
Defines the interface for all transformers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseTransformer(ABC):
    """Abstract base class for all transformers."""
    
    @abstractmethod
    def transform_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform incoming request data to internal format."""
        pass
    
    @abstractmethod
    def transform_response(self, payment_record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform internal data to API response format."""
        pass
    
    @abstractmethod
    def transform_response_list(self, payment_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform list of internal records to API response format."""
        pass
