from flask import Flask, jsonify, request, g
from database import init_db, seed_sample_data
import v1.routes as v1
import v2.routes as v2
app = Flask(__name__)

init_db()
seed_sample_data()


@app.before_request
def detect_version():
    """Detect API version from query parameter before processing request."""
    # Skip for root endpoint
    if request.path == '/':
        return
    
    # Get version from query parameter
    api_version = request.args.get('version', '1')
    
    # Normalize version
    if api_version in ['1', 'v1']:
        g.api_version = 'v1'
    elif api_version in ['2', 'v2']:
        g.api_version = 'v2'
    else:
        g.api_version = 'v1'  # Default to v1

# Custom routing - dispatch to correct module based on query parameter
@app.route('/api/payments', methods=['GET', 'POST'])
@app.route('/api/payments/<int:payment_id>', methods=['GET', 'DELETE'])
def route_to_version(payment_id=None):
    """Route to correct version based on ?version= query parameter."""
    if g.api_version == 'v2':
        # Call V2 endpoint
        if request.method == 'GET':
            if payment_id:
                return v2.get_transaction(payment_id)
            else:
                return v2.get_transactions()
        elif request.method == 'POST':
            return v2.create_transaction()
        elif request.method == 'DELETE':
            return v2.delete_transaction(payment_id)
    else:
        # Call V1 endpoint (default)
        if request.method == 'GET':
            if payment_id:
                return v1.get_payment(payment_id)
            else:
                return v1.get_payments()
        elif request.method == 'POST':
            return v1.create_payment()
        elif request.method == 'DELETE':
            return v1.delete_payment(payment_id)


@app.route('/')
def index():
    return jsonify({
        'message': 'Query Parameter API Versioning Demo',
        'description': 'Version is determined by the ?version= query parameter',
        'usage': {
            'v1': {
                'query_param': '?version=1',
                'endpoints': [
                    'GET /api/payments?version=1',
                    'GET /api/payments/{id}?version=1',
                    'POST /api/payments?version=1',
                    'DELETE /api/payments/{id}?version=1'
                ],
                'example': 'curl http://localhost:5003/api/payments?version=1'
            },
            'v2': {
                'query_param': '?version=2',
                'endpoints': [
                    'GET /api/payments?version=2',
                    'GET /api/payments/{id}?version=2',
                    'POST /api/payments?version=2',
                    'DELETE /api/payments/{id}?version=2'
                ],
                'example': 'curl http://localhost:5003/api/payments?version=2'
            }
        },
        'note': 'Same URL, different behavior based on query parameter!'
    })


if __name__ == '__main__':
    app.run(debug=True, port=5003)
