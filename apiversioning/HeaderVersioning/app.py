"""
HeaderVersioning Payment API
A Flask application demonstrating Header-Based API Versioning.
Version is determined by the 'API-Version' HTTP header.
"""
from flask import Flask, jsonify, request
from routes import payment_bp
from core.database import init_db, seed_sample_data


def create_app():
    """Application factory function."""
    app = Flask(__name__)
    
    # Configuration
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Initialize database
    init_db()
    seed_sample_data()
    
    # Register blueprint
    app.register_blueprint(payment_bp)
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'HeaderVersioning Payment API - Header-Based API Versioning',
            'description': 'Version is determined by the API-Version HTTP header',
            'versioning_strategy': {
                'type': 'Header-Based Versioning',
                'header_name': 'API-Version',
                'supported_versions': ['1', 'v1', '2', 'v2'],
                'default_version': '1 (if no header provided)',
                'benefits': [
                    'Clean URLs - no version in path',
                    'Same endpoint for all versions',
                    'Easy to add new versions without URL changes',
                    'Semantic versioning support'
                ]
            },
            'usage': {
                'v1': {
                    'header': 'API-Version: 1',
                    'resource': 'payments',
                    'format': {
                        'request': {
                            'amount': 100.0,
                            'card_number': '4111-1111-1111-1111',
                            'status': 'SUCCESS'
                        },
                        'response': {
                            'status_code': 200,
                            'message': '...',
                            'data': {
                                'id': 1,
                                'transaction_id': 'TXN-ABC123',
                                'amount': 100.0,
                                'card_number': '4111-1111-1111-1111',
                                'status': 'SUCCESS',
                                'created_at': '...'
                            }
                        }
                    }
                },
                'v2': {
                    'header': 'API-Version: 2',
                    'resource': 'transactions',
                    'format': {
                        'request': {
                            'amount': 100.0,
                            'payment_token': 'TOK-ABC123',
                            'status': 'SUCCESS'
                        },
                        'response': {
                            'code': 200,
                            'message': '...',
                            'data': {
                                'id': 1,
                                'amount': 100.0,
                                'payment_token': 'TOK-ABC123',
                                'status': 'SUCCESS',
                                'code': 200,
                                'created_at': '...'
                            }
                        }
                    },
                    'breaking_changes': [
                        'Removed transaction_id field',
                        'Replaced card_number with payment_token',
                        'Changed status_code to code'
                    ]
                }
            },
            'endpoints': {
                'base_url': '/api/payments',
                'operations': {
                    'list': 'GET /api/payments',
                    'get': 'GET /api/payments/{id}',
                    'create': 'POST /api/payments',
                    'delete': 'DELETE /api/payments/{id}'
                },
                'note': 'All endpoints use the same URL. Version determined by API-Version header.'
            },
            'examples': {
                'curl_v1': {
                    'list': 'curl -H "API-Version: 1" http://localhost:5001/api/payments',
                    'create': 'curl -X POST -H "API-Version: 1" -H "Content-Type: application/json" -d \'{"amount": 100.0, "card_number": "4111-1111-1111-1111", "status": "SUCCESS"}\' http://localhost:5001/api/payments'
                },
                'curl_v2': {
                    'list': 'curl -H "API-Version: 2" http://localhost:5001/api/payments',
                    'create': 'curl -X POST -H "API-Version: 2" -H "Content-Type: application/json" -d \'{"amount": 100.0, "payment_token": "TOK-ABC123", "status": "SUCCESS"}\' http://localhost:5001/api/payments'
                }
            },
            'comparison': {
                'url_versioning': {
                    'example': '/api/v1/payments vs /api/v2/transactions',
                    'pros': ['Clear and visible', 'Easy to understand', 'Cacheable'],
                    'cons': ['URL changes between versions', 'Multiple endpoints to maintain']
                },
                'header_versioning': {
                    'example': '/api/payments with API-Version header',
                    'pros': ['Clean URLs', 'Same endpoint', 'Flexible versioning'],
                    'cons': ['Less visible', 'Harder to test in browser', 'Caching complexity']
                }
            },
            'database': {
                'type': 'SQLite',
                'file': 'payments_header.db',
                'note': 'Independent database for HeaderVersioning project'
            }
        })
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        api_version = request.headers.get('API-Version', 'not specified')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'requested_version': api_version,
            'supported_versions': ['1', 'v1', '2', 'v2']
        }), 200
    
    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 80)
    print("🚀 HeaderVersioning Payment API Server Starting...")
    print("=" * 80)
    print("📚 Versioning Strategy: HEADER-BASED")
    print("   Version determined by 'API-Version' HTTP header")
    print()
    print("📁 Project Structure:")
    print("   HeaderVersioning/")
    print("   ├── app.py                (Flask application)")
    print("   ├── routes.py             (Single set of routes)")
    print("   ├── core/")
    print("   │   ├── database.py       (Database layer)")
    print("   │   └── service.py        (Business logic)")
    print("   └── handlers/")
    print("       ├── v1_handler.py     (V1 format handler)")
    print("       └── v2_handler.py     (V2 format handler)")
    print()
    print("🔗 Endpoints (same URL, different headers):")
    print("   Root:     http://localhost:5001/")
    print("   Health:   http://localhost:5001/health")
    print("   Payments: http://localhost:5001/api/payments")
    print()
    print("📋 Usage Examples:")
    print("   V1: curl -H 'API-Version: 1' http://localhost:5001/api/payments")
    print("   V2: curl -H 'API-Version: 2' http://localhost:5001/api/payments")
    print()
    print("💡 Supported Headers:")
    print("   API-Version: 1   (or v1) → Returns V1 format")
    print("   API-Version: 2   (or v2) → Returns V2 format")
    print("   (no header)              → Defaults to V1")
    print()
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
