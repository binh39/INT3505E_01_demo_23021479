"""
Unified Payment Routes - Single set of routes handling multiple API versions.
Uses Adapter pattern to delegate version-specific logic.
"""
from flask import Blueprint, request, jsonify
from typing import Type
from adapters.v1_adapter import V1Adapter
from adapters.v2_adapter import V2Adapter
from core.service import PaymentService


# Create unified blueprint
unified_bp = Blueprint('unified', __name__, url_prefix='/api')


def get_adapter(version: str):
    """
    Factory function to get the appropriate adapter for the API version.
    
    Args:
        version: API version string ('v1' or 'v2')
        
    Returns:
        Adapter instance for the specified version
        
    Raises:
        ValueError: If version is not supported
    """
    adapters = {
        'v1': V1Adapter,
        'v2': V2Adapter
    }
    
    adapter_class = adapters.get(version)
    if not adapter_class:
        raise ValueError(f"Unsupported API version: {version}")
    
    return adapter_class()


# ============================================================================
# V1 Routes: /api/v1/payments
# ============================================================================

@unified_bp.route('/v1/payments', methods=['GET'])
def get_all_payments_v1():
    """GET /api/v1/payments - Retrieve all payments (V1 format)"""
    try:
        adapter = get_adapter('v1')
        payments = PaymentService.get_all_payments()
        transformed = adapter.transform_response_list(payments)
        
        return jsonify(adapter.format_success_response(
            data=transformed,
            message='Payments retrieved successfully'
        )), 200
        
    except Exception as e:
        adapter = get_adapter('v1')
        return jsonify(adapter.format_error_response(
            message=f'Error retrieving payments: {str(e)}',
            status_code=500
        )), 500


@unified_bp.route('/v1/payments/<int:payment_id>', methods=['GET'])
def get_payment_v1(payment_id):
    """GET /api/v1/payments/<id> - Retrieve specific payment (V1 format)"""
    try:
        adapter = get_adapter('v1')
        payment = PaymentService.get_payment_by_id(payment_id)
        
        if not payment:
            return jsonify(adapter.format_error_response(
                message=f'Payment with id {payment_id} not found',
                status_code=404
            )), 404
        
        transformed = adapter.transform_response(payment)
        return jsonify(adapter.format_success_response(
            data=transformed,
            message='Payment retrieved successfully'
        )), 200
        
    except Exception as e:
        adapter = get_adapter('v1')
        return jsonify(adapter.format_error_response(
            message=f'Error retrieving payment: {str(e)}',
            status_code=500
        )), 500


@unified_bp.route('/v1/payments', methods=['POST'])
def create_payment_v1():
    """POST /api/v1/payments - Create new payment (V1 format)"""
    try:
        adapter = get_adapter('v1')
        data = request.get_json()
        
        # Validate required fields
        if not data or 'amount' not in data or 'card_number' not in data:
            return jsonify(adapter.format_error_response(
                message='Missing required fields: amount, card_number',
                status_code=400
            )), 400
        
        # Transform request
        transformed_data = adapter.transform_request(data)
        
        # Create payment
        payment = PaymentService.create_payment(
            amount=transformed_data['amount'],
            card_number=transformed_data['card_number'],
            payment_token=transformed_data.get('payment_token'),
            status=transformed_data.get('status', 'SUCCESS')
        )
        
        # Transform response
        transformed = adapter.transform_response(payment)
        return jsonify(adapter.format_success_response(
            data=transformed,
            message='Payment created successfully',
            status_code=201
        )), 201
        
    except Exception as e:
        adapter = get_adapter('v1')
        return jsonify(adapter.format_error_response(
            message=f'Error creating payment: {str(e)}',
            status_code=500
        )), 500


@unified_bp.route('/v1/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment_v1(payment_id):
    """DELETE /api/v1/payments/<id> - Delete payment (V1 format)"""
    try:
        adapter = get_adapter('v1')
        success = PaymentService.delete_payment(payment_id)
        
        if not success:
            return jsonify(adapter.format_error_response(
                message=f'Payment with id {payment_id} not found',
                status_code=404
            )), 404
        
        return jsonify(adapter.format_success_response(
            data=None,
            message='Payment deleted successfully'
        )), 200
        
    except Exception as e:
        adapter = get_adapter('v1')
        return jsonify(adapter.format_error_response(
            message=f'Error deleting payment: {str(e)}',
            status_code=500
        )), 500


# ============================================================================
# V2 Routes: /api/v2/transactions
# ============================================================================

@unified_bp.route('/v2/transactions', methods=['GET'])
def get_all_transactions_v2():
    """GET /api/v2/transactions - Retrieve all transactions (V2 format)"""
    try:
        adapter = get_adapter('v2')
        payments = PaymentService.get_all_payments()
        transformed = adapter.transform_response_list(payments)
        
        return jsonify(adapter.format_success_response(
            data=transformed,
            message='Transactions retrieved successfully',
            code=200
        )), 200
        
    except Exception as e:
        adapter = get_adapter('v2')
        return jsonify(adapter.format_error_response(
            message=f'Error retrieving transactions: {str(e)}',
            code=500
        )), 500


@unified_bp.route('/v2/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction_v2(transaction_id):
    """GET /api/v2/transactions/<id> - Retrieve specific transaction (V2 format)"""
    try:
        adapter = get_adapter('v2')
        payment = PaymentService.get_payment_by_id(transaction_id)
        
        if not payment:
            return jsonify(adapter.format_error_response(
                message=f'Transaction with id {transaction_id} not found',
                code=404
            )), 404
        
        transformed = adapter.transform_response(payment)
        return jsonify(adapter.format_success_response(
            data=transformed,
            message='Transaction retrieved successfully',
            code=200
        )), 200
        
    except Exception as e:
        adapter = get_adapter('v2')
        return jsonify(adapter.format_error_response(
            message=f'Error retrieving transaction: {str(e)}',
            code=500
        )), 500


@unified_bp.route('/v2/transactions', methods=['POST'])
def create_transaction_v2():
    """POST /api/v2/transactions - Create new transaction (V2 format)"""
    try:
        adapter = get_adapter('v2')
        data = request.get_json()
        
        # Validate required fields
        if not data or 'amount' not in data:
            return jsonify(adapter.format_error_response(
                message='Missing required field: amount',
                code=400
            )), 400
        
        # V2 requires either payment_token or card_number
        if 'payment_token' not in data and 'card_number' not in data:
            return jsonify(adapter.format_error_response(
                message='Either payment_token or card_number is required',
                code=400
            )), 400
        
        # Transform request
        transformed_data = adapter.transform_request(data)
        deprecation_warning = transformed_data.pop('_deprecation_warning', None)
        
        # Create payment
        payment = PaymentService.create_payment(
            amount=transformed_data['amount'],
            card_number=transformed_data.get('card_number'),
            payment_token=transformed_data.get('payment_token'),
            status=transformed_data.get('status', 'SUCCESS')
        )
        
        # Transform response
        transformed = adapter.transform_response(payment)
        return jsonify(adapter.format_success_response(
            data=transformed,
            message='Transaction created successfully',
            code=201,
            deprecation_warning=deprecation_warning
        )), 201
        
    except Exception as e:
        adapter = get_adapter('v2')
        return jsonify(adapter.format_error_response(
            message=f'Error creating transaction: {str(e)}',
            code=500
        )), 500


@unified_bp.route('/v2/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction_v2(transaction_id):
    """DELETE /api/v2/transactions/<id> - Delete transaction (V2 format)"""
    try:
        adapter = get_adapter('v2')
        success = PaymentService.delete_payment(transaction_id)
        
        if not success:
            return jsonify(adapter.format_error_response(
                message=f'Transaction with id {transaction_id} not found',
                code=404
            )), 404
        
        return jsonify(adapter.format_success_response(
            data=None,
            message='Transaction deleted successfully',
            code=200
        )), 200
        
    except Exception as e:
        adapter = get_adapter('v2')
        return jsonify(adapter.format_error_response(
            message=f'Error deleting transaction: {str(e)}',
            code=500
        )), 500
