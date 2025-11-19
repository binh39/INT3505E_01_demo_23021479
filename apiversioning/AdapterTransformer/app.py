"""
AdapterTransformer Payment API
A standalone Flask application demonstrating the Adapter/Transformer pattern for API versioning.
"""
from flask import Flask, jsonify
from routes.payment_routes import unified_bp
from core.database import init_db, seed_sample_data
import os


def create_app():
    """Application factory function."""
    app = Flask(__name__)
    
    # Configuration
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Initialize database
    init_db()
    seed_sample_data()
    
    # Register blueprints
    app.register_blueprint(unified_bp)
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'AdapterTransformer Payment API - Demonstrating Adapter Pattern for API Versioning',
            'architecture': {
                'pattern': 'Adapter/Transformer Pattern',
                'description': 'Single routes with version-specific adapters and transformers',
                'layers': {
                    'routes': 'HTTP request/response handling',
                    'adapters': 'Version-specific formatting and HATEOAS',
                    'transformers': 'Data structure transformation',
                    'service': 'Version-agnostic business logic',
                    'database': 'Data persistence'
                }
            },
            'versions': {
                'v1': {
                    'base_url': '/api/v1',
                    'resource': 'payments',
                    'endpoints': {
                        'list': 'GET /api/v1/payments',
                        'get': 'GET /api/v1/payments/{id}',
                        'create': 'POST /api/v1/payments',
                        'delete': 'DELETE /api/v1/payments/{id}'
                    },
                    'format': {
                        'fields': ['id', 'transaction_id', 'amount', 'card_number', 'status', 'created_at'],
                        'response_wrapper': 'status_code, message, data, links'
                    }
                },
                'v2': {
                    'base_url': '/api/v2',
                    'resource': 'transactions',
                    'endpoints': {
                        'list': 'GET /api/v2/transactions',
                        'get': 'GET /api/v2/transactions/{id}',
                        'create': 'POST /api/v2/transactions',
                        'delete': 'DELETE /api/v2/transactions/{id}'
                    },
                    'format': {
                        'fields': ['id', 'amount', 'payment_token', 'status', 'code', 'created_at'],
                        'response_wrapper': 'code, message, data, links',
                        'breaking_changes': [
                            'Removed transaction_id field',
                            'Replaced card_number with payment_token',
                            'Changed status_code to code'
                        ]
                    },
                    'backward_compatibility': {
                        'card_number': 'Still accepted but deprecated, auto-converted to payment_token'
                    }
                }
            },
            'examples': {
                'v1_create': {
                    'url': 'POST /api/v1/payments',
                    'body': {
                        'amount': 100.0,
                        'card_number': '4111-1111-1111-1111',
                        'status': 'SUCCESS'
                    }
                },
                'v2_create': {
                    'url': 'POST /api/v2/transactions',
                    'body': {
                        'amount': 100.0,
                        'payment_token': 'TOK-ABC123DEF456',
                        'status': 'SUCCESS'
                    }
                }
            },
            'database': {
                'type': 'SQLite',
                'file': 'payments_adapter.db',
                'note': 'Independent database, not shared with Routes project'
            }
        })
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'api_versions': ['v1', 'v2']
        }), 200
    
    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 80)
    print("🚀 AdapterTransformer Payment API Server Starting...")
    print("=" * 80)
    print("📚 Project Structure:")
    print("   AdapterTransformer/")
    print("   ├── app.py                    (This file - Flask application)")
    print("   ├── core/")
    print("   │   ├── database.py           (Database connection & initialization)")
    print("   │   └── service.py            (Business logic layer)")
    print("   ├── routes/")
    print("   │   └── payment_routes.py     (Unified routes for v1 & v2)")
    print("   ├── adapters/")
    print("   │   ├── v1_adapter.py         (V1 request/response formatting)")
    print("   │   └── v2_adapter.py         (V2 request/response formatting)")
    print("   └── transformers/")
    print("       ├── v1_transformer.py     (V1 data transformation)")
    print("       └── v2_transformer.py     (V2 data transformation)")
    print()
    print("🔗 Available Endpoints:")
    print("   Root:    http://localhost:5000/")
    print("   Health:  http://localhost:5000/health")
    print()
    print("   V1 API:  http://localhost:5000/api/v1/payments")
    print("   V2 API:  http://localhost:5000/api/v2/transactions")
    print()
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
