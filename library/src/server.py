from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Cho phép React frontend gọi API

DB_NAME = "books.db"

# ---------------------------
# Khởi tạo database nếu chưa có
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS borrowed_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_key TEXT UNIQUE,
            title TEXT,
            author TEXT,
            cover_url TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return "Flask server is running!"

# ---------------------------
# API: Mượn sách
# ---------------------------
@app.route("/api/books", methods=["POST"])
def borrow_book():
    data = request.get_json()
    book_key = data.get("book_key")
    title = data.get("title")
    author = data.get("author")
    cover_url = data.get("cover_url")

    if not book_key:
        return jsonify({"status": "error", "message": "Missing book_key"}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Kiểm tra xem đã mượn chưa 
    c.execute("SELECT * FROM borrowed_books WHERE book_key = ?", (book_key,))
    existing = c.fetchone()

    if existing:
        conn.close()
        return jsonify({"status": "exists", "message": "You have already borrowed this book"}), 200

    # Chưa có thì thêm vào database
    c.execute(
        "INSERT INTO borrowed_books (book_key, title, author, cover_url) VALUES (?, ?, ?, ?)",
        (book_key, title, author, cover_url)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Borrowed book successfully",
        "data": {
            "book_key": book_key,
            "_links": {
                "self": {"href": f"/api/books/{book_key}"},
                "return": {"href": f"/api/books/{book_key}", "method": "DELETE"},
                "all_books": {"href": "/api/books", "method": "GET"}
            }
        }
    }), 201

# ---------------------------
# API lấy danh sách đã mượn
# ---------------------------
@app.route("/api/books", methods=["GET"])
def get_borrowed():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT book_key, title, author, cover_url FROM borrowed_books")
    rows = c.fetchall()
    conn.close()

    books = [
        {
            "book_key": r[0],
            "title": r[1],
            "author": r[2],
            "cover_url": r[3],
            "_links": {
                "self": {"href": f"/api/books/{r[0]}"},
                "return": {"href": f"/api/books/{r[0]}", "method": "DELETE"}
            }
        }
        for r in rows
    ]

    response = jsonify({
        "status": "success",
        "message": "Get borrowed books successfully",
        "data": books,
        "_links": {
            "self": {"href": "/api/books"},
            "borrow": {"href": "/api/book", "method": "POST"}
        }
    })

    # --- Header cache và ETag ---
    import hashlib, json
    etag = hashlib.md5(json.dumps(books, sort_keys=True).encode()).hexdigest()
    response.headers["Cache-Control"] = "public, max-age=60"
    response.headers["ETag"] = etag

    # --- xử lý điều kiện "If-None-Match" từ client ---
    client_etag = request.headers.get("If-None-Match")
    if client_etag == etag:
        # Dữ liệu chưa thay đổi → không cần gửi lại toàn bộ
        return "", 304

    return response

# ---------------------------
# API: Trả sách (DELETE)
# ---------------------------
@app.route("/api/books/<book_key>", methods=["DELETE"])
def return_book(book_key):
    print(f"Request to return book with key: {book_key}")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("DELETE FROM borrowed_books WHERE book_key = ?", (book_key,))
    deleted = c.rowcount
    conn.commit()
    conn.close()

    if deleted == 0:
        return jsonify({"status": "error", "message": "Cannot find book to return"}), 404
    return jsonify({"status": "success", "message": "Returned book successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)
