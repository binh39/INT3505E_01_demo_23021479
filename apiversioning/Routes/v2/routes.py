from flask import Blueprint, request, jsonify, url_for
from database import get_db_connection
from datetime import datetime
import uuid
import hashlib

v2_bp = Blueprint('v2', __name__, url_prefix='/api/v2')

def generate_hateoas_links(transaction_id=None, base_url='/api/v2/transactions'):
    """Generate HATEOAS links for transaction resources."""
    links = {
        'self': base_url if transaction_id is None else f"{base_url}/{transaction_id}",
        'collection': base_url
    }
    
    if transaction_id is not None:
        links['delete'] = f"{base_url}/{transaction_id}"
    
    return links

def generate_payment_token(card_number):
    """Generate a secure payment token from card number."""
    # Simple tokenization: hash the card number
    token = hashlib.sha256(card_number.encode()).hexdigest()[:32].upper()
    return f"TOK-{token}"

def format_transaction_response(transaction):
    """Format a single transaction record with HATEOAS links (v2 format)."""
    return {
        'id': transaction['id'],
        'amount': transaction['amount'],
        'payment_token': transaction['payment_token'],
        'status': transaction['status'],
        'code': transaction['code'],
        'created_at': transaction['created_at'],
    }

@v2_bp.route('/transactions', methods=['GET'])
def get_transactions():
    """
    GET /api/v2/transactions
    Retrieve all transactions.
    
    Breaking changes from v1:
    - Resource renamed from 'payments' to 'transactions'
    - Uses 'code' instead of 'status_code'
    - Uses 'payment_token' instead of 'card_number'
    - Removed 'transaction_id' (use 'id' instead)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payments ORDER BY created_at DESC')
        transactions = cursor.fetchall()
        conn.close()
        
        transactions_list = [format_transaction_response(transaction) for transaction in transactions]
        
        return jsonify({
            'code': 200,
            'message': 'Transactions retrieved successfully',
            'data': transactions_list,
            'links': generate_hateoas_links()
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'Internal server error: {str(e)}',
            'data': None,
            'links': generate_hateoas_links()
        }), 500

@v2_bp.route('/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """
    GET /api/v2/transactions/{id}
    Retrieve a specific transaction by ID.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payments WHERE id = ?', (transaction_id,))
        transaction = cursor.fetchone()
        conn.close()
        
        if transaction is None:
            return jsonify({
                'code': 404,
                'message': f'Transaction with ID {transaction_id} not found',
                'data': None,
                'links': generate_hateoas_links()
            }), 404
        
        return jsonify({
            'code': 200,
            'message': 'Transaction retrieved successfully',
            'data': format_transaction_response(transaction),
            'links': generate_hateoas_links(transaction_id)
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'Internal server error: {str(e)}',
            'data': None,
            'links': generate_hateoas_links()
        }), 500

@v2_bp.route('/transactions', methods=['POST'])
def create_transaction():
    """
    POST /api/v2/transactions
    Create a new transaction.
    
    Request body (v2):
    {
        "amount": float,
        "payment_token": string (optional, will be generated if card_number provided),
        "card_number": string (deprecated, use payment_token),
        "status": "SUCCESS" | "PENDING" | "REFUND"
    }
    
    Breaking changes:
    - Accepts 'payment_token' instead of 'card_number'
    - Returns 'code' instead of 'status_code'
    - Backward compatibility: still accepts 'card_number' for migration
    """
    try:
        data = request.get_json()
        
        # Validation
        if not data:
            return jsonify({
                'code': 400,
                'message': 'Request body is required',
                'data': None,
                'links': generate_hateoas_links()
            }), 400
        
        required_fields = ['amount', 'status']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'code': 400,
                'message': f'Missing required fields: {", ".join(missing_fields)}',
                'data': None,
                'links': generate_hateoas_links()
            }), 400
        
        # Validate status
        valid_statuses = ['SUCCESS', 'PENDING', 'REFUND']
        if data['status'] not in valid_statuses:
            return jsonify({
                'code': 400,
                'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
                'data': None,
                'links': generate_hateoas_links()
            }), 400
        
        # Handle payment_token / card_number (backward compatibility)
        payment_token = data.get('payment_token')
        card_number = data.get('card_number')
        
        if not payment_token and not card_number:
            return jsonify({
                'code': 400,
                'message': 'Either payment_token or card_number is required',
                'data': None,
                'links': generate_hateoas_links()
            }), 400
        
        # Generate payment token if card_number provided
        if card_number and not payment_token:
            payment_token = generate_payment_token(card_number)
        
        # For backward compatibility, store card_number if provided
        if not card_number and payment_token:
            card_number = "TOKENIZED"  # Placeholder for tokenized payments
        
        # Generate transaction ID (still needed for database compatibility)
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        
        # Map status to code (v2 uses 'code' instead of 'status_code')
        code_map = {
            'SUCCESS': 200,
            'PENDING': 102,
            'REFUND': 204
        }
        code = code_map.get(data['status'], 200)
        
        # Insert into database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (transaction_id, amount, card_number, status, status_code, code, payment_token)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (transaction_id, data['amount'], card_number, data['status'], code, code, payment_token))
        
        new_transaction_id = cursor.lastrowid
        conn.commit()
        
        # Fetch the created transaction
        cursor.execute('SELECT * FROM payments WHERE id = ?', (new_transaction_id,))
        transaction = cursor.fetchone()
        conn.close()
        
        response_data = format_transaction_response(transaction)
        
        # Add deprecation warning if card_number was used
        if card_number and card_number != "TOKENIZED":
            response_data['_warnings'] = [
                'The card_number field is deprecated. Please use payment_token in future requests.'
            ]
        
        return jsonify({
            'code': 201,
            'message': 'Transaction created successfully',
            'data': response_data,
            'links': generate_hateoas_links(new_transaction_id)
        }), 201
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'Internal server error: {str(e)}',
            'data': None,
            'links': generate_hateoas_links()
        }), 500

@v2_bp.route('/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """
    DELETE /api/v2/transactions/{id}
    Delete a specific transaction by ID.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if transaction exists
        cursor.execute('SELECT * FROM payments WHERE id = ?', (transaction_id,))
        transaction = cursor.fetchone()
        
        if transaction is None:
            conn.close()
            return jsonify({
                'code': 404,
                'message': f'Transaction with ID {transaction_id} not found',
                'data': None,
                'links': generate_hateoas_links()
            }), 404
        
        # Delete the transaction
        cursor.execute('DELETE FROM payments WHERE id = ?', (transaction_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'code': 200,
            'message': f'Transaction with ID {transaction_id} deleted successfully',
            'data': None,
            'links': generate_hateoas_links()
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'Internal server error: {str(e)}',
            'data': None,
            'links': generate_hateoas_links()
        }), 500