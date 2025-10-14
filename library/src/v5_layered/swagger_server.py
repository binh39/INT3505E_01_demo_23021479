from flask import Flask, send_from_directory, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import os, yaml

app = Flask(__name__)

# -----------------------------
# Load và cung cấp OpenAPI spec
# -----------------------------
@app.route("/openapi.yaml")
def openapi_spec():
    return send_from_directory(os.getcwd(), "openapi.yaml", mimetype="text/yaml")

# -----------------------------
# Swagger UI setup
# -----------------------------
SWAGGER_URL = "/docs"
API_URL = "/openapi.yaml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI endpoint
    API_URL,      # OpenAPI spec
    config={"app_name": "Library API Documentation"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/")
def home():
    return jsonify({"message": "Welcome to Library API - see /docs for documentation"})

if __name__ == "__main__":
    app.run(debug=True)
