from flask import Flask, request, jsonify, make_response
import sqlite3
import hashlib
import json
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Configuration
DB_NAME = "library.db"
API_TOKEN = "demo123"

# ============================================
# Database Initialization
# ============================================
def init_db():
    """Initialize SQLite database with borrowed_books table"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS borrowed_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_key TEXT UNIQUE NOT NULL,
            title TEXT,
            author TEXT,
            cover_url TEXT,
            borrowed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ============================================
# Authentication Middleware
# ============================================
def check_auth():
    """Check if request has valid Bearer token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return False
    token = auth_header.split(" ")[1]
    return token == API_TOKEN

@app.before_request
def require_auth():
    """Require authentication for all endpoints except root and OPTIONS"""
    if request.path == "/" or request.method == "OPTIONS":
        return
    if not check_auth():
        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 401

# ============================================
# Helper Functions
# ============================================
def generate_etag(data):
    """Generate ETag hash for caching"""
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

def check_etag(etag):
    """Check if client's ETag matches current ETag"""
    client_etag = request.headers.get("If-None-Match")
    return client_etag == etag

def create_hateoas_links(book_key=None):
    """Create HATEOAS links for resources"""
    if book_key:
        return {
            "self": {"href": f"/api/books/{book_key}", "method": "GET"},
            "return": {"href": f"/api/books/{book_key}", "method": "DELETE"},
            "all": {"href": "/api/books", "method": "GET"}
        }
    else:
        return {
            "self": {"href": "/api/books", "method": "GET"},
            "borrow": {"href": "/api/books", "method": "POST"}
        }

# ============================================
# Routes
# ============================================

@app.route("/")
def home():
    """API root endpoint"""
    return jsonify({
        "service": "Library API",
        "version": "1.0.0",
        "description": "Simple RESTful API for managing borrowed books",
        "_links": {
            "books": {"href": "/api/books", "method": "GET"},
            "docs": {"href": "/api-docs", "method": "GET"}
        }
    })

# ============================================
# Books Collection: /api/books
# ============================================

@app.route("/api/books", methods=["GET"])
def get_borrowed_books():
    """
    GET /api/books - Get list of all borrowed books
    Returns: List of borrowed books with HATEOAS links
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT book_key, title, author, cover_url FROM borrowed_books ORDER BY borrowed_at DESC")
    rows = c.fetchall()
    conn.close()

    # Build response data
    books = [
        {
            "book_key": row[0],
            "title": row[1],
            "author": row[2],
            "cover_url": row[3],
            "_links": create_hateoas_links(row[0])
        }
        for row in rows
    ]

    # Generate ETag for caching
    etag = generate_etag(books)
    if check_etag(etag):
        return make_response("", 304)

    # Build response
    response_data = {
        "status": "success",
        "message": "Get borrowed books successfully",
        "data": books,
        "_links": create_hateoas_links()
    }

    response = make_response(jsonify(response_data), 200)
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=60"
    response.headers["Access-Control-Expose-Headers"] = "ETag"
    
    return response

@app.route("/api/books", methods=["POST"])
def borrow_book():
    """
    POST /api/books - Borrow a new book
    Request Body: { "book_key": "B001", "title": "...", "author": "...", "cover_url": "..." }
    Returns: 201 Created or 200 if already exists
    """
    data = request.get_json()
    
    # Validate required field
    book_key = data.get("book_key")
    if not book_key:
        return jsonify({
            "status": "error",
            "message": "Missing book_key"
        }), 400

    # Optional fields
    title = data.get("title", "")
    author = data.get("author", "")
    cover_url = data.get("cover_url", "")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check if book already borrowed
    c.execute("SELECT book_key FROM borrowed_books WHERE book_key = ?", (book_key,))
    existing = c.fetchone()

    if existing:
        conn.close()
        return jsonify({
            "status": "exists",
            "message": "Already borrowed"
        }), 200

    # Insert new borrowed book
    try:
        c.execute(
            "INSERT INTO borrowed_books (book_key, title, author, cover_url) VALUES (?, ?, ?, ?)",
            (book_key, title, author, cover_url)
        )
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Borrowed successfully",
            "data": {
                "book_key": book_key,
                "_links": create_hateoas_links(book_key)
            }
        }), 201
    except Exception as e:
        conn.close()
        return jsonify({
            "status": "error",
            "message": f"Database error: {str(e)}"
        }), 500

# ============================================
# Books Item: /api/books/{book_key}
# ============================================

@app.route("/api/books/<book_key>", methods=["GET"])
def get_book(book_key):
    """
    GET /api/books/{book_key} - Get details of a specific borrowed book
    Returns: Book details with HATEOAS links
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT book_key, title, author, cover_url FROM borrowed_books WHERE book_key = ?",
        (book_key,)
    )
    book = c.fetchone()
    conn.close()

    if not book:
        return jsonify({
            "status": "error",
            "message": "Book not found"
        }), 404

    # Build book data
    book_data = {
        "book_key": book[0],
        "title": book[1],
        "author": book[2],
        "cover_url": book[3],
        "_links": create_hateoas_links(book[0])
    }

    # Generate ETag for caching
    etag = generate_etag(book_data)
    if check_etag(etag):
        return make_response("", 304)

    response_data = {
        "status": "success",
        "message": "Get a borrowed book successfully",
        "data": book_data
    }

    response = make_response(jsonify(response_data), 200)
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=60"
    response.headers["Access-Control-Expose-Headers"] = "ETag"
    
    return response

@app.route("/api/books/<book_key>", methods=["DELETE"])
def return_book(book_key):
    """
    DELETE /api/books/{book_key} - Return a borrowed book
    Returns: 200 OK or 404 if not found
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM borrowed_books WHERE book_key = ?", (book_key,))
    deleted = c.rowcount
    conn.commit()
    conn.close()

    if deleted == 0:
        return jsonify({
            "status": "error",
            "message": "Book not found"
        }), 404

    return jsonify({
        "status": "success",
        "message": "Returned successfully",
        "data": {
            "_links": create_hateoas_links()
        }
    }), 200

# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500

# ============================================
# Run Application
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Library API Server Starting...")
    print("=" * 50)
    print(f"📚 Database: {DB_NAME}")
    print(f"🔑 Auth Token: Bearer {API_TOKEN}")
    print(f"🌐 Server: http://localhost:5000")
    print("=" * 50)
    print("\n📖 Available Endpoints:")
    print("  GET    /api/books          - List all borrowed books")
    print("  POST   /api/books          - Borrow a new book")
    print("  GET    /api/books/{key}    - Get book details")
    print("  DELETE /api/books/{key}    - Return a book")
    print("=" * 50)
    print("\n✨ Starting server...\n")
    
    app.run(debug=True, host="0.0.0.0", port=5000)
