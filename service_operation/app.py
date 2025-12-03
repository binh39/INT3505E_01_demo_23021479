from flask import Flask, request, jsonify, make_response, g, Response
import sqlite3
import json
import uuid
import time
from logger import API_LOGGER as logger
import metrics
from prometheus_client import CONTENT_TYPE_LATEST
from flask_cors import CORS
from datetime import datetime
from events import event_bus  # Event-driven pattern

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Configuration
DB_NAME = "library.db"

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
# Request Tracing Middleware
# ============================================
@app.before_request
def before_request_logging():
    """Generate trace ID and log incoming request"""
    # Generate unique trace ID for this request
    g.trace_id = str(uuid.uuid4())
    g.start_time = time.time()
    # increment in-progress requests
    try:
        metrics.IN_PROGRESS.inc()
    except Exception:
        pass
    
    # Structured log for incoming request
    headers = dict(request.headers)
    if 'Authorization' in headers:
        headers['Authorization'] = 'Bearer ***'

    logger.info(
        "Incoming Request",
        extra={
            'trace_id': g.trace_id,
            'method': request.method,
            'url': request.url,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'user_agent': str(request.user_agent),
            'headers': headers
        }
    )

    # Log request body for POST/PUT/PATCH requests when JSON
    if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
        try:
            body = request.get_json()
        except Exception:
            body = None
        logger.info(
            "Request Body",
            extra={
                'trace_id': g.trace_id,
                'body': body
            }
        )

@app.after_request
def after_request_logging(response):
    """Log response details and calculate request duration"""
    if hasattr(g, 'trace_id'):
        duration = (time.time() - g.start_time) * 1000  # Convert to milliseconds
        
        logger.info(
            "Outgoing Response",
            extra={
                'trace_id': g.trace_id,
                'status_code': response.status_code,
                'duration_ms': round(duration, 2)
            }
        )
        
        # Add trace ID to response headers
        response.headers['X-Trace-ID'] = g.trace_id
        response.headers['X-Response-Time'] = f"{duration:.2f}ms"
        
        # Log response body
        if response.is_json:
            try:
                resp_text = response.get_data(as_text=True)
            except Exception:
                resp_text = None
            logger.info(
                "Response Body",
                extra={
                    'trace_id': g.trace_id,
                    'response': resp_text[:500] if resp_text else None
                }
            )
        
        # Log performance warning for slow requests
        if duration > 1000:
            logger.warning(
                "Slow Request",
                extra={
                    'trace_id': g.trace_id,
                    'duration_ms': round(duration, 2)
                }
            )

        # observe prometheus metrics: latency (seconds) and request count
        try:
            metrics.REQUEST_LATENCY.labels(request.method, request.path).observe(duration / 1000.0)
            metrics.REQUEST_COUNT.labels(request.method, request.path, str(response.status_code)).inc()
        except Exception:
            pass

        # decrement in-progress requests
        try:
            metrics.IN_PROGRESS.dec()
        except Exception:
            pass
    
    return response

# ============================================
# Helper Functions
# ============================================
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
    trace_id = getattr(g, 'trace_id', 'unknown')
    logger.info("Fetching all borrowed books", extra={'trace_id': trace_id})
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT book_key, title, author, cover_url FROM borrowed_books ORDER BY borrowed_at DESC")
    rows = c.fetchall()
    conn.close()
    
    logger.info("Found books", extra={'trace_id': trace_id, 'count': len(rows)})

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

    response_data = {
        "status": "success",
        "message": "Get borrowed books successfully",
        "data": books,
        "_links": create_hateoas_links()
    }

    response = make_response(jsonify(response_data), 200)
    
    return response

@app.route("/api/books", methods=["POST"])
def borrow_book():
    """
    POST /api/books - Borrow a new book
    Request Body: { "book_key": "B001", "title": "...", "author": "...", "cover_url": "..." }
    Returns: 201 Created or 200 if already exists
    """
    trace_id = getattr(g, 'trace_id', 'unknown')
    data = request.get_json()
    
    # Validate required field
    book_key = data.get("book_key")
    if not book_key:
        logger.error("Validation error: Missing book_key", extra={'trace_id': trace_id})
        return jsonify({
            "status": "error",
            "message": "Missing book_key",
            "trace_id": trace_id
        }), 400
    
    logger.info("Attempting to borrow book", extra={'trace_id': trace_id, 'book_key': book_key})

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
        logger.info("Book already borrowed", extra={'trace_id': trace_id, 'book_key': book_key})
        return jsonify({
            "status": "exists",
            "message": "Already borrowed",
            "trace_id": trace_id
        }), 200

    # Insert new borrowed book
    try:
        c.execute(
            "INSERT INTO borrowed_books (book_key, title, author, cover_url) VALUES (?, ?, ?, ?)",
            (book_key, title, author, cover_url)
        )
        conn.commit()
        conn.close()
        
        logger.info("Book borrowed successfully", extra={'trace_id': trace_id, 'book_key': book_key})
        try:
            metrics.BOOKS_BORROWED.inc()
        except Exception:
            pass
        
        # Publish event asynchronously (non-blocking)
        event_bus.publish('book.borrowed', {
            'book_key': book_key,
            'title': title,
            'author': author,
            'trace_id': trace_id
        })
        
        return jsonify({
            "status": "success",
            "message": "Borrowed successfully",
            "data": {
                "book_key": book_key,
                "_links": create_hateoas_links(book_key)
            },
            "trace_id": trace_id
        }), 201
    except Exception as e:
        conn.close()
        logger.error("Database error", extra={'trace_id': trace_id, 'error': str(e)})
        try:
            metrics.ERRORS.labels('database').inc()
        except Exception:
            pass
        return jsonify({
            "status": "error",
            "message": f"Database error: {str(e)}",
            "trace_id": trace_id
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
    trace_id = getattr(g, 'trace_id', 'unknown')
    logger.info("Looking up book", extra={'trace_id': trace_id, 'book_key': book_key})
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT book_key, title, author, cover_url FROM borrowed_books WHERE book_key = ?",
        (book_key,)
    )
    book = c.fetchone()
    conn.close()

    if not book:
        logger.warning("Book not found", extra={'trace_id': trace_id, 'book_key': book_key})
        return jsonify({
            "status": "error",
            "message": "Book not found",
            "trace_id": trace_id
        }), 404
    
    logger.info("Book found", extra={'trace_id': trace_id, 'book_key': book_key})

    # Build book data
    book_data = {
        "book_key": book[0],
        "title": book[1],
        "author": book[2],
        "cover_url": book[3],
        "_links": create_hateoas_links(book[0])
    }

    response_data = {
        "status": "success",
        "message": "Get a borrowed book successfully",
        "data": book_data
    }

    response = make_response(jsonify(response_data), 200)
    return response

@app.route("/api/books/<book_key>", methods=["DELETE"])
def return_book(book_key):
    """
    DELETE /api/books/{book_key} - Return a borrowed book
    Returns: 200 OK or 404 if not found
    """
    trace_id = getattr(g, 'trace_id', 'unknown')
    logger.info("Attempting to return book", extra={'trace_id': trace_id, 'book_key': book_key})
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM borrowed_books WHERE book_key = ?", (book_key,))
    deleted = c.rowcount
    conn.commit()
    conn.close()

    if deleted == 0:
        logger.warning("Book not found for deletion", extra={'trace_id': trace_id, 'book_key': book_key})
        return jsonify({
            "status": "error",
            "message": "Book not found",
            "trace_id": trace_id
        }), 404

    logger.info("Book returned successfully", extra={'trace_id': trace_id, 'book_key': book_key})
    try:
        metrics.BOOKS_RETURNED.inc()
    except Exception:
        pass
    
    # Publish event asynchronously (non-blocking)
    event_bus.publish('book.returned', {
        'book_key': book_key,
        'trace_id': trace_id
    })
    
    return jsonify({
        "status": "success",
        "message": "Returned successfully",
        "data": {
            "_links": create_hateoas_links()
        },
        "trace_id": trace_id
    }), 200

# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    trace_id = getattr(g, 'trace_id', 'unknown')
    logger.error("404 Error", extra={'trace_id': trace_id, 'url': request.url})
    try:
        metrics.ERRORS.labels('404').inc()
    except Exception:
        pass
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "trace_id": trace_id
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    trace_id = getattr(g, 'trace_id', 'unknown')
    logger.error("500 Error", extra={'trace_id': trace_id, 'error': str(error)})
    try:
        metrics.ERRORS.labels('500').inc()
    except Exception:
        pass
    return jsonify({
        "status": "error",
        "message": "Internal server error",
        "trace_id": trace_id
    }), 500


@app.route('/metrics', methods=['GET'])
def metrics_endpoint():
    """Expose Prometheus metrics"""
    try:
        data, content_type = metrics.metrics_response()
        return Response(data, mimetype=content_type)
    except Exception as e:
        logger.error("Metrics endpoint error", extra={'error': str(e)})
        return jsonify({"status":"error","message":"Metrics unavailable"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
