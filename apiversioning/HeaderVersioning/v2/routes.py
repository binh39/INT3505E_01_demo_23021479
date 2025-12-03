"""
V2 API Routes - Header Versioning
Accessed via header: API-Version: v2
"""
from flask import Blueprint, request, jsonify
from database import get_db_connection
import uuid
import hashlib

v2_bp = Blueprint('v2', __name__)


@v2_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for V2"""
    return jsonify({
        'code': 200,
        'message': 'V2 API is running',
        'version': 'v2'
    }), 200


def generate_hateoas_links(transaction_id=None, base_url='/api/payments'):
    """Generate HATEOAS links for transaction resources."""
    links = {
        'self': base_url if transaction_id is None else f"{base_url}/{transaction_id}",
        'collection': base_url
    }
    
    if transaction_id is not None:
        links['delete'] = f"{base_url}/{transaction_id}"
    
    return links


def generate_payment_token(card_number):
    """Generate payment token from card number"""
    token = hashlib.sha256(card_number.encode()).hexdigest()[:32].upper()
    return f"TOK-{token}"


@v2_bp.route('/payments', methods=['GET'])
def get_transactions():
    """GET /api/payments with API-Version: v2"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM payments ORDER BY created_at DESC')
    transactions = cursor.fetchall()
    conn.close()
    
    transactions_list = []
    for transaction in transactions:
        transactions_list.append({
            'id': transaction['id'],
            'amount': transaction['amount'],
            'payment_token': transaction['payment_token'],
            'status': transaction['status'],
            'code': transaction['code'],
            'created_at': transaction['created_at'],
            '_links': generate_hateoas_links(transaction['id'])
        })
    
    return jsonify({
        'code': 200,
        'message': 'Transactions retrieved successfully',
        'data': transactions_list,
        '_links': generate_hateoas_links()
    }), 200


@v2_bp.route('/payments/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """GET /api/payments/{id} with API-Version: v2"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM payments WHERE id = ?', (transaction_id,))
    transaction = cursor.fetchone()
    conn.close()
    
    if transaction is None:
        return jsonify({
            'code': 404,
            'message': f'Transaction with ID {transaction_id} not found',
            '_links': generate_hateoas_links()
        }), 404
    
    return jsonify({
        'code': 200,
        'message': 'Transaction retrieved successfully',
        'data': {
            'id': transaction['id'],
            'amount': transaction['amount'],
            'payment_token': transaction['payment_token'],
            'status': transaction['status'],
            'code': transaction['code'],
            'created_at': transaction['created_at']
        },
        '_links': generate_hateoas_links(transaction_id)
    }), 200


@v2_bp.route('/payments', methods=['POST'])
def create_transaction():
    """POST /api/payments with API-Version: v2"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'code': 400,
            'message': 'Request body is required'
        }), 400
    
    required_fields = ['amount', 'status']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            'code': 400,
            'message': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400
    
    # Handle payment_token or card_number
    payment_token = data.get('payment_token')
    card_number = data.get('card_number')
    
    if not payment_token and not card_number:
        return jsonify({
            'code': 400,
            'message': 'Either payment_token or card_number is required',
            '_links': generate_hateoas_links()
        }), 400
    
    # Generate token if card_number provided
    if card_number and not payment_token:
        payment_token = generate_payment_token(card_number)
    
    if not card_number:
        card_number = "TOKENIZED"
    
    # Generate transaction ID
    transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
    
    # Map status to code
    code_map = {'SUCCESS': 200, 'PENDING': 102, 'REFUND': 204}
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
    
    return jsonify({
        'code': 201,
        'message': 'Transaction created successfully',
        'data': {
            'id': transaction['id'],
            'amount': transaction['amount'],
            'payment_token': transaction['payment_token'],
            'status': transaction['status'],
            'code': transaction['code'],
            'created_at': transaction['created_at']
        },
        '_links': generate_hateoas_links(new_transaction_id)
    }), 201


@v2_bp.route('/payments/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """DELETE /api/payments/{id} with API-Version: v2"""
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
            '_links': generate_hateoas_links()
        }), 404
    
    # Delete the transaction
    cursor.execute('DELETE FROM payments WHERE id = ?', (transaction_id,))
    conn.commit()
    conn.close()
    
    return jsonify({
        'code': 200,
        'message': f'Transaction with ID {transaction_id} deleted successfully',
        '_links': generate_hateoas_links()
    }), 200
