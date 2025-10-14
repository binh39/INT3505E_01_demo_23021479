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

# ----------------------------
# CACHING - Cache danh sách sách đã mượn
# ----------------------------
cache_data = None
cache_time = 0
CACHE_TTL = 600  # cache 600 giây

@app.route("/api/books", methods=["GET"])
def proxy_books_list():
    global cache_data, cache_time
    now = time.time()

    # Nếu cache còn hiệu lực, return cache
    if cache_data and now - cache_time < CACHE_TTL:
        print("Proxy return cache data")
        return Response(cache_data, status=200, mimetype="application/json")

    # Nếu cache hết hạn, gọi backend thật
    resp = requests.get(f"{BACKEND_URL}/api/books")
    cache_data = resp.content
    cache_time = now
    print("Proxy call backend to get new data")

    return Response(resp.content, resp.status_code, resp.headers.items())

# ----------------------------
# DELETE - Khi trả sách → xóa cache
# ----------------------------
@app.route("/api/books/<book_key>", methods=["DELETE"])
def proxy_return_book(book_key):
    global cache_data, cache_time
    url = f"{BACKEND_URL}/api/books/{book_key}"

    # Gọi backend thật
    resp = requests.delete(url)

    # Nếu trả sách thành công → xóa cache để đồng bộ
    if resp.status_code == 200:
        cache_data = None
        cache_time = 0
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
