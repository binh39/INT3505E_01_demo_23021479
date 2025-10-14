from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Cho phép frontend gọi từ React

DB_NAME = "books.db"

# ---------------------------
# Khởi tạo database
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
    return "Flask Library API - Version 1 Client–Server"

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
        return jsonify({"status": "exists", "message": "Already borrowed"}), 200

    # Chưa có thì thêm vào database
    c.execute(
        "INSERT INTO borrowed_books (book_key, title, author, cover_url) VALUES (?, ?, ?, ?)",
        (book_key, title, author, cover_url)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "Borrowed successfully"}), 201

# ---------------------------
# API: Lấy danh sách đã mượn
# ---------------------------
@app.route("/api/books", methods=["GET"])
def get_books():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT book_key, title, author, cover_url FROM borrowed_books")
    rows = c.fetchall()
    conn.close()

    books = [
        {"book_key": r[0], "title": r[1], "author": r[2], "cover_url": r[3]}
        for r in rows
    ]
    return jsonify(books)

# ---------------------------
# API: Trả sách
# ---------------------------
@app.route("/api/books/<book_key>", methods=["DELETE"])
def return_book(book_key):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("DELETE FROM borrowed_books WHERE book_key = ?", (book_key,))
    deleted = c.rowcount
    conn.commit()
    conn.close()

    if deleted == 0:
        return jsonify({"status": "error", "message": "Book not found"}), 404

    return jsonify({"status": "success", "message": "Returned successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)
