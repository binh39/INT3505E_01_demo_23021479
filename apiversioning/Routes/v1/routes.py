from flask import Blueprint, request, jsonify, url_for
from database import get_db_connection
from datetime import datetime
import uuid

v1_bp = Blueprint('v1', __name__, url_prefix='/api/v1')

def generate_hateoas_links(payment_id=None, base_url='/api/v1/payments'):
    """Generate HATEOAS links for payment resources."""
    links = {
        'self': base_url if payment_id is None else f"{base_url}/{payment_id}",
        'collection': base_url
    }
    
    if payment_id is not None:
        links['delete'] = f"{base_url}/{payment_id}"
    
    return links

def format_payment_response(payment):
    """Format a single payment record with HATEOAS links."""
    return {
        'id': payment['id'],
        'transaction_id': payment['transaction_id'],
        'amount': payment['amount'],
        'card_number': payment['card_number'],
        'status': payment['status'],
        'created_at': payment['created_at'],
    }

@v1_bp.route('/payments', methods=['GET'])
def get_payments():
    """
    GET /api/v1/payments
    Retrieve all payments.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payments ORDER BY created_at DESC')
        payments = cursor.fetchall()
        conn.close()
        
        payments_list = [format_payment_response(payment) for payment in payments]
        
        return jsonify({
            'status_code': 200,
            'message': 'Payments retrieved successfully',
            'data': payments_list,
            'links': generate_hateoas_links()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status_code': 500,
            'message': f'Internal server error: {str(e)}',
            'data': None,
            'links': generate_hateoas_links()
        }), 500

@v1_bp.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    """
    GET /api/v1/payments/{id}
    Retrieve a specific payment by ID.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cursor.fetchone()
        conn.close()
        
        if payment is None:
            return jsonify({
                'status_code': 404,
                'message': f'Payment with ID {payment_id} not found',
                'data': None,
                'links': generate_hateoas_links()
            }), 404
        
        return jsonify({
            'status_code': 200,
            'message': 'Payment retrieved successfully',
            'data': format_payment_response(payment),
            'links': generate_hateoas_links(payment_id)
        }), 200
        
    except Exception as e:
        return jsonify({
            'status_code': 500,
            'message': f'Internal server error: {str(e)}',
            'data': None,
            'links': generate_hateoas_links()
        }), 500

@v1_bp.route('/payments', methods=['POST'])
def create_payment():
    """
    POST /api/v1/payments
    Create a new payment.
    
    Request body:
    {
        "amount": float,
        "card_number": string,
        "status": "SUCCESS" | "PENDING" | "REFUND"
    }
    """
    try:
        data = request.get_json()
        
        # Validation
        if not data:
            return jsonify({
                'status_code': 400,
                'message': 'Request body is required',
                'data': None,
                'links': generate_hateoas_links()
            }), 400
        
        required_fields = ['amount', 'card_number', 'status']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'status_code': 400,
                'message': f'Missing required fields: {", ".join(missing_fields)}',
                'data': None,
                'links': generate_hateoas_links()
            }), 400
        
        # Validate status
        valid_statuses = ['SUCCESS', 'PENDING', 'REFUND']
        if data['status'] not in valid_statuses:
            return jsonify({
                'status_code': 400,
                'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
                'data': None,
                'links': generate_hateoas_links()
            }), 400
        
        # Generate transaction ID
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        
        # Map status to status_code
        status_code_map = {
            'SUCCESS': 200,
            'PENDING': 102,
            'REFUND': 204
        }
        status_code = status_code_map.get(data['status'], 200)
        
        # Insert into database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (transaction_id, amount, card_number, status, status_code)
            VALUES (?, ?, ?, ?, ?)
        ''', (transaction_id, data['amount'], data['card_number'], data['status'], status_code))
        
        payment_id = cursor.lastrowid
        conn.commit()
        
        # Fetch the created payment
        cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cursor.fetchone()
        conn.close()
        
        return jsonify({
            'status_code': 201,
            'message': 'Payment created successfully',
            'data': format_payment_response(payment),
            'links': generate_hateoas_links(payment_id)
        }), 201
        
    except Exception as e:
        return jsonify({
            'status_code': 500,
            'message': f'Internal server error: {str(e)}',
            'data': None,
            'links': generate_hateoas_links()
        }), 500

@v1_bp.route('/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    """
    DELETE /api/v1/payments/{id}
    Delete a specific payment by ID.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if payment exists
        cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cursor.fetchone()
        
        if payment is None:
            conn.close()
            return jsonify({
                'status_code': 404,
                'message': f'Payment with ID {payment_id} not found',
                'data': None,
                'links': generate_hateoas_links()
            }), 404
        
        # Delete the payment
        cursor.execute('DELETE FROM payments WHERE id = ?', (payment_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'status_code': 200,
            'message': f'Payment with ID {payment_id} deleted successfully',
            'data': None,
            'links': generate_hateoas_links()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status_code': 500,
            'message': f'Internal server error: {str(e)}',
            'data': None,
            'links': generate_hateoas_links()
        }), 500
