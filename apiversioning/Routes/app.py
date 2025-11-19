from flask import Flask, jsonify
from flask_cors import CORS
from v1.routes import v1_bp
from v2.routes import v2_bp
from database import init_db, migrate_db
import os

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(v1_bp)
app.register_blueprint(v2_bp)

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
                'status': 'active',
                'deprecation_warning': 'This version will be deprecated on 2026-01-19 and sunset on 2026-06-19'
            },
            'v2': {
                'base_url': '/api/v2',
                'endpoints': {
                    'transactions': '/api/v2/transactions',
                    'transaction_by_id': '/api/v2/transactions/{id}',
                    'migration_guide': '/api/v2/migration-guide'
                },
                'status': 'current',
                'breaking_changes': 'See /api/v2/migration-guide for details'
            }
        },
        'recommended_version': 'v2'
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
    
    # Run migration to add new columns for v2
    print("Running database migration...")
    migrate_db()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
