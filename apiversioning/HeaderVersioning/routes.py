"""
Payment Routes with Header-Based Versioning.
Version is determined by the 'API-Version' header.

Supported headers:
- API-Version: 1 (or v1)
- API-Version: 2 (or v2)

Default: v1 if no header provided
"""
from flask import Blueprint, request, jsonify
from handlers.v1_handler import V1Handler
from handlers.v2_handler import V2Handler
from core.service import PaymentService


# Single blueprint for all versions
payment_bp = Blueprint('payments', __name__, url_prefix='/api/payments')


def get_handler():
    """
    Get the appropriate handler based on the API-Version header.
    
    Returns:
        Handler class (V1Handler or V2Handler)
    
    Raises:
        ValueError: If version is not supported
    """
    # Get version from header
    version_header = request.headers.get('API-Version', '1')
    
    # Normalize version (accept '1', 'v1', '2', 'v2')
    version = version_header.lower().replace('v', '')
    
    handlers = {
        '1': V1Handler,
        '2': V2Handler
    }
    
    handler_class = handlers.get(version)
    if not handler_class:
        raise ValueError(f"Unsupported API version: {version_header}")
    
    return handler_class


# ============================================================================
# Single set of routes - version determined by header
# ============================================================================

@payment_bp.route('', methods=['GET'])
def get_all_payments():
    """
    GET /api/payments
    
    Headers:
        API-Version: 1  → Returns V1 format (with transaction_id, card_number)
        API-Version: 2  → Returns V2 format (with payment_token, no transaction_id)
    """
    try:
        handler = get_handler()
        payments = PaymentService.get_all_payments()
        transformed = handler.transform_response_list(payments)
        
        if handler == V1Handler:
            return jsonify(handler.format_success_response(
                data=transformed,
                message='Payments retrieved successfully'
            )), 200
        else:  # V2Handler
            return jsonify(handler.format_success_response(
                data=transformed,
                message='Transactions retrieved successfully',
                code=200
            )), 200
        
    except ValueError as e:
        # Unsupported version
        return jsonify({
            'error': str(e),
            'supported_versions': ['1', 'v1', '2', 'v2']
        }), 400
    except Exception as e:
        handler = get_handler()
        if handler == V1Handler:
            return jsonify(handler.format_error_response(
                message=f'Error retrieving payments: {str(e)}',
                status_code=500
            )), 500
        else:
            return jsonify(handler.format_error_response(
                message=f'Error retrieving transactions: {str(e)}',
                code=500
            )), 500


@payment_bp.route('/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    """
    GET /api/payments/{id}
    
    Headers:
        API-Version: 1  → Returns V1 format
        API-Version: 2  → Returns V2 format
    """
    try:
        handler = get_handler()
        payment = PaymentService.get_payment_by_id(payment_id)
        
        if not payment:
            if handler == V1Handler:
                return jsonify(handler.format_error_response(
                    message=f'Payment with id {payment_id} not found',
                    status_code=404
                )), 404
            else:
                return jsonify(handler.format_error_response(
                    message=f'Transaction with id {payment_id} not found',
                    code=404
                )), 404
        
        transformed = handler.transform_response(payment)
        
        if handler == V1Handler:
            return jsonify(handler.format_success_response(
                data=transformed,
                message='Payment retrieved successfully'
            )), 200
        else:
            return jsonify(handler.format_success_response(
                data=transformed,
                message='Transaction retrieved successfully',
                code=200
            )), 200
        
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'supported_versions': ['1', 'v1', '2', 'v2']
        }), 400
    except Exception as e:
        handler = get_handler()
        if handler == V1Handler:
            return jsonify(handler.format_error_response(
                message=f'Error retrieving payment: {str(e)}',
                status_code=500
            )), 500
        else:
            return jsonify(handler.format_error_response(
                message=f'Error retrieving transaction: {str(e)}',
                code=500
            )), 500


@payment_bp.route('', methods=['POST'])
def create_payment():
    """
    POST /api/payments
    
    Headers:
        API-Version: 1  → Expects V1 format (card_number required)
        API-Version: 2  → Expects V2 format (payment_token or card_number)
    
    V1 Request Body:
    {
        "amount": 100.0,
        "card_number": "4111-1111-1111-1111",
        "status": "SUCCESS"
    }
    
    V2 Request Body:
    {
        "amount": 100.0,
        "payment_token": "TOK-ABC123",
        "status": "SUCCESS"
    }
    """
    try:
        handler = get_handler()
        data = request.get_json()
        
        # Validate based on version
        if handler == V1Handler:
            # V1 requires amount and card_number
            if not data or 'amount' not in data or 'card_number' not in data:
                return jsonify(handler.format_error_response(
                    message='Missing required fields: amount, card_number',
                    status_code=400
                )), 400
        else:  # V2Handler
            # V2 requires amount and (payment_token OR card_number)
            if not data or 'amount' not in data:
                return jsonify(handler.format_error_response(
                    message='Missing required field: amount',
                    code=400
                )), 400
            
            if 'payment_token' not in data and 'card_number' not in data:
                return jsonify(handler.format_error_response(
                    message='Either payment_token or card_number is required',
                    code=400
                )), 400
        
        # Transform request
        transformed_data = handler.transform_request(data)
        deprecation_warning = transformed_data.pop('_deprecation_warning', None)
        
        # Create payment
        payment = PaymentService.create_payment(
            amount=transformed_data['amount'],
            card_number=transformed_data.get('card_number'),
            payment_token=transformed_data.get('payment_token'),
            status=transformed_data.get('status', 'SUCCESS')
        )
        
        # Transform response
        transformed = handler.transform_response(payment)
        
        if handler == V1Handler:
            return jsonify(handler.format_success_response(
                data=transformed,
                message='Payment created successfully',
                status_code=201
            )), 201
        else:
            return jsonify(handler.format_success_response(
                data=transformed,
                message='Transaction created successfully',
                code=201,
                deprecation_warning=deprecation_warning
            )), 201
        
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'supported_versions': ['1', 'v1', '2', 'v2']
        }), 400
    except Exception as e:
        handler = get_handler()
        if handler == V1Handler:
            return jsonify(handler.format_error_response(
                message=f'Error creating payment: {str(e)}',
                status_code=500
            )), 500
        else:
            return jsonify(handler.format_error_response(
                message=f'Error creating transaction: {str(e)}',
                code=500
            )), 500


@payment_bp.route('/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    """
    DELETE /api/payments/{id}
    
    Headers:
        API-Version: 1  → Returns V1 format
        API-Version: 2  → Returns V2 format
    """
    try:
        handler = get_handler()
        success = PaymentService.delete_payment(payment_id)
        
        if not success:
            if handler == V1Handler:
                return jsonify(handler.format_error_response(
                    message=f'Payment with id {payment_id} not found',
                    status_code=404
                )), 404
            else:
                return jsonify(handler.format_error_response(
                    message=f'Transaction with id {payment_id} not found',
                    code=404
                )), 404
        
        if handler == V1Handler:
            return jsonify(handler.format_success_response(
                data=None,
                message='Payment deleted successfully'
            )), 200
        else:
            return jsonify(handler.format_success_response(
                data=None,
                message='Transaction deleted successfully',
                code=200
            )), 200
        
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'supported_versions': ['1', 'v1', '2', 'v2']
        }), 400
    except Exception as e:
        handler = get_handler()
        if handler == V1Handler:
            return jsonify(handler.format_error_response(
                message=f'Error deleting payment: {str(e)}',
                status_code=500
            )), 500
        else:
            return jsonify(handler.format_error_response(
                message=f'Error deleting transaction: {str(e)}',
                code=500
            )), 500
