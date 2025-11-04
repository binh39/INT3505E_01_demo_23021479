from flask import Flask, send_from_directory, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/openapi.yaml")
def openapi_spec():
    """Serve OpenAPI specification file"""
    # Get the directory where swagger.py is located (backend folder)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(base_dir, "openapi.yaml", mimetype="text/yaml")

SWAGGER_URL = "/docs"
API_URL = "/openapi.yaml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL, 
    config={"app_name": "Library API Documentation"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/")
def home():
    """Homepage with API information"""
    return jsonify({
        "message": "Library API Documentation Server",
        "endpoints": {
            "documentation": "/docs",
            "openapi_spec": "/openapi.yaml"
        },
        "note": "This is a documentation server. Main API runs on port 5000"
    })

if __name__ == "__main__":
    # Run on different port to avoid conflict with main API server
    print("🚀 Starting Swagger UI Documentation Server...")
    print("📖 Access documentation at: http://localhost:8080/docs")
    print("📄 OpenAPI spec available at: http://localhost:8080/openapi.yaml")
    app.run(debug=True, port=8080)
