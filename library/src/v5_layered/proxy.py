from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests, time
from collections import defaultdict

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# server.py
BACKEND_URL = "http://127.0.0.1:5000"

# ----------------------------
# RATE LIMITING - Ngăn spam mượn sách
# ----------------------------
# Cấu trúc: {ip: [timestamps]}
request_counts = defaultdict(list)
RATE_LIMIT = 5      # tối đa 5 request
WINDOW = 60         # trong 60 giây

@app.before_request
def rate_limit():
    if request.method == "POST" and "/api/books" in request.path:
        ip = request.remote_addr
        now = time.time()
        # Xóa các request quá cũ (hết hạn 60 giây)
        request_counts[ip] = [t for t in request_counts[ip] if now - t < WINDOW]
        if len(request_counts[ip]) >= RATE_LIMIT:
            return jsonify({
                "error": "Too many borrow attempts. Please wait a bit.",
                "message": "You have reached the borrow limit (5 books/min). Please wait a bit before trying again."
            }), 429
        request_counts[ip].append(now)

@app.route("/")
def home():
    return "Proxy Layer (Port 5001) - Cache + Rate Limiting + Forwarding"


# ----------------------------
# ETag CACHE
# ----------------------------
etag_cache = None
data_cache = None

@app.route("/api/books", methods=["GET"])
def proxy_books_list():
    global etag_cache, data_cache

    headers = {}
    if etag_cache:
        headers["If-None-Match"] = etag_cache
    auth_header = request.headers.get("Authorization")
    if auth_header:
        headers["Authorization"] = auth_header

    resp = requests.get(f"{BACKEND_URL}/api/books", headers=headers)

    if resp.status_code == 304 and data_cache:
        print("Proxy: ETag matched, return cached data")
        return Response(data_cache, status=200, mimetype="application/json")

    if resp.status_code == 200:
        etag_cache = resp.headers.get("ETag")
        data_cache = resp.content
        print(f"Proxy: updated cache with new ETag: {etag_cache}")

    # Forward toàn bộ response xuống client
    return Response(resp.content, resp.status_code, resp.headers.items())

# ----------------------------
# DELETE - Trả sách → Xóa cache
# ----------------------------
@app.route("/api/books/<book_key>", methods=["DELETE"])
def proxy_return_book(book_key):
    global data_cache, etag_cache

    headers = {}
    auth_header = request.headers.get("Authorization")
    if auth_header:
        headers["Authorization"] = auth_header

    resp = requests.delete(f"{BACKEND_URL}/api/books/{book_key}", headers=headers)

    if resp.status_code == 200:
        data_cache = None
        etag_cache = None
        print(f"Cache invalidated after returning book: {book_key}")

    return Response(resp.content, resp.status_code, resp.headers.items())

# ----------------------------
# Forward các route khác (POST borrow, GET /api/books/<id> ...)
# ----------------------------
@app.route("/api/<path:path>", methods=["GET", "POST", "PUT", "PATCH"])
def forward(path):
    url = f"{BACKEND_URL}/api/{path}"
    resp = requests.request(
        method=request.method,
        url=url,
        headers={k: v for k, v in request.headers if k != "Host"},
        data=request.get_data(),
        allow_redirects=False
    )

    # Nếu là POST /api/books (mượn sách thành công) → xóa cache
    global cache_data, cache_time
    if request.method == "POST" and "/api/books" in request.path and resp.status_code in (200, 201):
        cache_data = None
        cache_time = 0
        print("Cache invalidated after borrowing a new book")
    
    return Response(resp.content, resp.status_code, resp.headers.items())

if __name__ == "__main__":
    app.run(port=5001, debug=True)
