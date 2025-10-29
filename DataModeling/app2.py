from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Reader(db.Model):
    __tablename__ = 'readers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    reader_id = db.Column(db.Integer, db.ForeignKey('readers.id'), nullable=False)
    borrow_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    returned = db.Column(db.Boolean, default=False)

    book = db.relationship('Book', backref='loans')
    reader = db.relationship('Reader', backref='loans')

def encode_cursor(value: int) -> str:
    return base64.b64encode(str(value).encode()).decode()

def decode_cursor(cursor: str) -> int:
    try:
        return int(base64.b64decode(cursor.encode()).decode())
    except Exception:
        return 0

@app.route("/api/books", methods=["GET"])
def get_books():
    query = request.args.get("q", "").strip().lower()
    author = request.args.get("author", "").strip().lower()
    genre = request.args.get("genre", "").strip().lower()
    limit = int(request.args.get("limit", 2))
    cursor_param = request.args.get("cursor")
    offset_param = request.args.get("offset")

    books_query = Book.query

    if query:
        books_query = books_query.filter(
            db.or_(Book.title.ilike(f"%{query}%"), Book.author.ilike(f"%{query}%"))
        )
    if author:
        books_query = books_query.filter(Book.author.ilike(f"%{author}%"))
    if genre:
        books_query = books_query.filter(Book.genre.ilike(f"%{genre}%"))

    total = books_query.count()

    if cursor_param:
        start_index = decode_cursor(cursor_param)
    else:
        start_index = int(offset_param or 0)

    paginated_books = books_query.offset(start_index).limit(limit).all()
    next_index = start_index + limit if start_index + limit < total else None
    next_cursor = encode_cursor(next_index) if next_index else None

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
        "data": [
            {"id": b.id, "title": b.title, "author": b.author, "genre": b.genre}
            for b in paginated_books
        ]
    })

@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book_detail(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"status": "error", "message": "Book not found"}), 404
    return jsonify({
        "status": "success",
        "message": "Book retrieved successfully",
        "data": {"id": book.id, "title": book.title, "author": book.author, "genre": book.genre}
    })

@app.route("/api/readers", methods=["GET"])
def get_readers():
    readers = Reader.query.all()
    return jsonify({
        "status": "success",
        "message": "Readers retrieved successfully",
        "data": [{"id": r.id, "name": r.name, "email": r.email} for r in readers]
    })

@app.route("/api/readers/<int:reader_id>/loans", methods=["GET"])
def get_reader_loans(reader_id):
    reader = Reader.query.get(reader_id)
    if not reader:
        return jsonify({"status": "error", "message": "Reader not found"}), 404

    reader_loans = Loan.query.filter_by(reader_id=reader_id).all()
    data = []
    for l in reader_loans:
        data.append({
            "id": l.id,
            "book_id": l.book_id,
            "book_title": l.book.title,
            "borrow_date": l.borrow_date.strftime("%Y-%m-%d"),
            "due_date": l.due_date.strftime("%Y-%m-%d"),
            "returned": l.returned
        })

    return jsonify({
        "status": "success",
        "reader": {"id": reader.id, "name": reader.name, "email": reader.email},
        "total_loans": len(data),
        "data": data
    })

if __name__ == "__main__": 
    import os
    print("SQLite DB Path:", os.path.abspath("library.db"))
    print("Working directory:", os.getcwd())
    print("SQLite path Flask dùng:", os.path.abspath("library.db"))
    print("File tồn tại?", os.path.exists("library.db"))
    with app.app_context():
        db.create_all()
        print("Số lượng sách trong DB:", Book.query.count())

    app.run(debug=True)
