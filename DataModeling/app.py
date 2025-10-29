from flask import Flask, jsonify, request
from datetime import datetime
import base64

app = Flask(__name__)

books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "genre": "Software Engineering"},
    {"id": 7, "title": "Clean Code", "author": "Robert C. Martin", "genre": "Software Engineering"},
    {"id": 2, "title": "Harry Potter", "author": "J.K. Rowling", "genre": "Fantasy"},
    {"id": 3, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "genre": "Programming"},
    {"id": 4, "title": "Deep Work", "author": "Cal Newport", "genre": "Productivity"},
    {"id": 5, "title": "Atomic Habits", "author": "James Clear", "genre": "Self-help"},
]

readers = [
    {"id": 1, "name": "Nguyễn Đình Bình", "email": "binh@uet.com"},
    {"id": 2, "name": "Trịnh Quang Hưng", "email": "hung@uet.com"},
    {"id": 3, "name": "Nguyễn Văn A", "email": "a@uet.com"},
    {"id": 4, "name": "Trần Thị B", "email": "b@uet.com"}
]

loans = [
    {"id": 1, "book_id": 1, "reader_id": 1, "borrow_date": "2025-10-01", "due_date": "2025-10-20", "returned": False},
    {"id": 2, "book_id": 2, "reader_id": 1, "borrow_date": "2025-10-05", "due_date": "2025-10-25", "returned": True},
    {"id": 3, "book_id": 3, "reader_id": 2, "borrow_date": "2025-10-10", "due_date": "2025-10-30", "returned": False}
]

def encode_cursor(value: int) -> str:
    return base64.b64encode(str(value).encode()).decode()

def decode_cursor(cursor: str) -> int:
    try:
        return int(base64.b64decode(cursor.encode()).decode())
    except Exception:
        return 0

@app.route("/api/books", methods=["GET"])
def get_books():
    """
    Lấy danh sách sách (GET /api/books)
    - Hỗ trợ tìm kiếm (q)
    - Filter theo author/genre
    - Phân trang offset/limit hoặc cursor
    """

    query = request.args.get("q", "").strip().lower()
    author = request.args.get("author", "").strip().lower()
    genre = request.args.get("genre", "").strip().lower()
    limit = int(request.args.get("limit", 2))

    # Cursor dạng Base64
    cursor_param = request.args.get("cursor")
    offset_param = request.args.get("offset")

    filtered_books = books

    if query:
        filtered_books = [
            b for b in filtered_books
            if query in b["title"].lower() or query in b["author"].lower()
        ]

    if author:
        filtered_books = [b for b in filtered_books if author in b["author"].lower()]
    if genre:
        filtered_books = [b for b in filtered_books if genre in b["genre"].lower()]

    total = len(filtered_books)

    # Phân trang
    # Ưu tiên cursor-based nếu có cursor
    if cursor_param:
        start_index = decode_cursor(cursor_param)
    else:
        start_index = int(offset_param or 0)

    paginated = filtered_books[start_index:start_index + limit]
    next_index = start_index + limit if start_index + limit < total else None
    next_cursor = encode_cursor(next_index) if next_index is not None else None

    return jsonify({
        "status": "success",
        "message": "Books retrieved successfully",
        "pagination": {
            "method": "cursor" if cursor_param else "offset",
            "limit": limit,
            "total": total,
            "current_start": start_index,
            "next_offset": next_index,
            "next_cursor": next_cursor
        },
        "data": paginated
    })

@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book_detail(book_id):
    """Lấy chi tiết 1 sách"""
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"status": "error", "message": "Book not found"}), 404
    return jsonify({"status": "success","message": "Book retrieved successfully", "data": book})

@app.route("/api/readers", methods=["GET"])
def get_readers():
    return jsonify({"status": "success","message": "Readers retrieved successfully", "data": readers})

@app.route("/api/readers/<int:reader_id>", methods=["GET"])
def get_reader_detail(reader_id):
    reader = next((r for r in readers if r["id"] == reader_id), None)
    if not reader:
        return jsonify({"status": "error", "message": "Reader not found"}), 404
    return jsonify({"status": "success","message": "Reader retrieved successfully", "data": reader})

@app.route("/api/readers/<int:reader_id>/loans", methods=["GET"])
def get_reader_loans(reader_id):
    """Lấy danh sách sách mà bạn đọc đã mượn"""
    reader = next((r for r in readers if r["id"] == reader_id), None)
    if not reader:
        return jsonify({"status": "error", "message": "Reader not found"}), 404

    reader_loans = [l for l in loans if l["reader_id"] == reader_id]
    for l in reader_loans:
        book = next((b for b in books if b["id"] == l["book_id"]), None)
        l["book_info"] = book

    return jsonify({
        "status": "success",
        "reader": reader,
        "total_loans": len(reader_loans),
        "data": reader_loans
    })

if __name__ == "__main__":
    app.run(debug=True)
