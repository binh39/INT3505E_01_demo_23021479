from flask import Flask, jsonify, request, redirect
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

IS_V2_ENABLED = False  # Set to True to enable V2, False to force V1

@app.before_request
def feature_toggle_router():
    """
    If IS_V2_ENABLED = False: All requests use V1 only
    If IS_V2_ENABLED = True: Allow both V1 and V2 (or redirect V1 to V2)
    """
    if request.path in ['/', '/health']:
        return
    
    if not IS_V2_ENABLED and request.path.startswith('/api/v2'):
        # Redirect V2 requests to V1
        new_path = request.path.replace('/api/v2/transactions', '/api/v1/payments', 1)
        print(f"V2 is disabled. Redirecting: {request.path} → {new_path}")
        return redirect(new_path)

@app.route('/')
def index():
    """Root endpoint with API information."""
    return jsonify({
        'message': 'Payment API Demo - API Versioning with Feature Toggle',
        'feature_toggle': {
            'IS_V2_ENABLED': IS_V2_ENABLED,
            'description': 'Controls whether V2 API is accessible',
            'behavior': 'V2 blocked and redirected to V1' if not IS_V2_ENABLED else 'Both V1 and V2 accessible'
        },
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
                'status': 'enabled' if IS_V2_ENABLED else 'disabled (redirects to V1)',
                'breaking_changes': 'See /api/v2/migration-guide for details'
            }
        },
        'recommended_version': 'v2' if IS_V2_ENABLED else 'v1'
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
