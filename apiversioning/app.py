from flask import Flask, jsonify
from flask_cors import CORS
from v1.routes import v1_bp
from database import init_db
import os

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(v1_bp)

@app.route('/')
def index():
    """Root endpoint with API information."""
    return jsonify({
        'message': 'Payment API Demo - API Versioning',
        'versions': {
            'v1': {
                'base_url': '/api/v1',
                'endpoints': {
                    'payments': '/api/v1/payments',
                    'payment_by_id': '/api/v1/payments/{id}'
                },
                'status': 'active'
            }
        }
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running'
    }), 200

if __name__ == '__main__':
    # Initialize database if it doesn't exist
    if not os.path.exists('payments.db'):
        print("Initializing database...")
        init_db()
    
    print("\n" + "="*50)
    print("Payment API Server Starting...")
    print("="*50)
    print("Available endpoints:")
    print("  - GET    /api/v1/payments")
    print("  - GET    /api/v1/payments/{id}")
    print("  - POST   /api/v1/payments")
    print("  - DELETE /api/v1/payments/{id}")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
