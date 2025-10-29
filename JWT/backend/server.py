from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db_connection, init_db
from auth import generate_token, admin_required, user_required, token_required
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Khởi tạo database
init_db()

# ========================================
# API Authentication
# ========================================

@app.route("/")
def home():
    return jsonify({
        "message": "Library Management System with JWT",
        "version": "2.0",
        "endpoints": {
            "auth": "/api/auth/login",
            "admin": "/api/admin/*",
            "user": "/api/user/*"
        }
    })

@app.route("/api/auth/login", methods=["POST"])
def login():
    """API đăng nhập - trả về JWT token"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({
            "status": "error",
            "message": "Username and password are required"
        }), 400
    
    conn = get_db_connection()
    user = conn.execute(
        "SELECT id, username, password, role FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()
    
    if not user or not check_password_hash(user['password'], password):
        return jsonify({
            "status": "error",
            "message": "Invalid username or password"
        }), 401
    
    # Tạo token
    token = generate_token(user['id'], user['username'], user['role'])
    
    return jsonify({
        "status": "success",
        "message": "Login successful",
        "data": {
            "token": token,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "role": user['role']
            }
        }
    }), 200

@app.route("/api/auth/verify", methods=["GET"])
@token_required
def verify_token(current_user):
    """API kiểm tra token còn hiệu lực không"""
    return jsonify({
        "status": "success",
        "message": "Token is valid",
        "data": {
            "user": {
                "id": current_user['user_id'],
                "username": current_user['username'],
                "role": current_user['role']
            }
        }
    }), 200

# ========================================
# API ADMIN - Quản lý sách trong thư viện
# ========================================

@app.route("/api/admin/books", methods=["GET"])
@admin_required
def admin_get_all_books(current_user):
    """Admin: Lấy danh sách tất cả sách trong thư viện"""
    conn = get_db_connection()
    books = conn.execute(
        "SELECT id, book_key, title, author, cover_url, quantity, available FROM library_books ORDER BY id DESC"
    ).fetchall()
    conn.close()
    
    books_list = [
        {
            "id": book['id'],
            "book_key": book['book_key'],
            "title": book['title'],
            "author": book['author'],
            "cover_url": book['cover_url'],
            "quantity": book['quantity'],
            "available": book['available']
        }
        for book in books
    ]
    
    return jsonify({
        "status": "success",
        "message": "Get all library books successfully",
        "data": books_list
    }), 200

@app.route("/api/admin/books", methods=["POST"])
@admin_required
def admin_add_book(current_user):
    """Admin: Thêm sách mới vào thư viện"""
    data = request.get_json()
    book_key = data.get("book_key")
    title = data.get("title")
    author = data.get("author", "")
    cover_url = data.get("cover_url", "")
    quantity = data.get("quantity", 1)
    
    if not book_key or not title:
        return jsonify({
            "status": "error",
            "message": "book_key and title are required"
        }), 400
    
    if quantity < 1:
        return jsonify({
            "status": "error",
            "message": "quantity must be at least 1"
        }), 400
    
    conn = get_db_connection()
    
    # Kiểm tra sách đã tồn tại chưa
    existing = conn.execute(
        "SELECT id FROM library_books WHERE book_key = ?",
        (book_key,)
    ).fetchone()
    
    if existing:
        conn.close()
        return jsonify({
            "status": "error",
            "message": "Book with this book_key already exists"
        }), 400
    
    # Thêm sách mới
    cursor = conn.execute(
        """INSERT INTO library_books (book_key, title, author, cover_url, quantity, available)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (book_key, title, author, cover_url, quantity, quantity)
    )
    conn.commit()
    book_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        "status": "success",
        "message": "Book added successfully",
        "data": {
            "id": book_id,
            "book_key": book_key,
            "title": title,
            "author": author,
            "cover_url": cover_url,
            "quantity": quantity,
            "available": quantity
        }
    }), 201

@app.route("/api/admin/books/<int:book_id>", methods=["PUT"])
@admin_required
def admin_update_book(current_user, book_id):
    """Admin: Cập nhật thông tin sách"""
    data = request.get_json()
    
    conn = get_db_connection()
    book = conn.execute(
        "SELECT * FROM library_books WHERE id = ?",
        (book_id,)
    ).fetchone()
    
    if not book:
        conn.close()
        return jsonify({
            "status": "error",
            "message": "Book not found"
        }), 404
    
    # Cập nhật các trường
    title = data.get("title", book['title'])
    author = data.get("author", book['author'])
    cover_url = data.get("cover_url", book['cover_url'])
    quantity = data.get("quantity", book['quantity'])
    
    if quantity < 1:
        conn.close()
        return jsonify({
            "status": "error",
            "message": "quantity must be at least 1"
        }), 400
    
    # Tính toán available mới
    borrowed_count = book['quantity'] - book['available']
    new_available = quantity - borrowed_count
    
    if new_available < 0:
        conn.close()
        return jsonify({
            "status": "error",
            "message": f"Cannot reduce quantity. {borrowed_count} books are currently borrowed"
        }), 400
    
    conn.execute(
        """UPDATE library_books 
           SET title = ?, author = ?, cover_url = ?, quantity = ?, available = ?
           WHERE id = ?""",
        (title, author, cover_url, quantity, new_available, book_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        "status": "success",
        "message": "Book updated successfully",
        "data": {
            "id": book_id,
            "book_key": book['book_key'],
            "title": title,
            "author": author,
            "cover_url": cover_url,
            "quantity": quantity,
            "available": new_available
        }
    }), 200

@app.route("/api/admin/books/<int:book_id>", methods=["DELETE"])
@admin_required
def admin_delete_book(current_user, book_id):
    """Admin: Xóa sách khỏi thư viện"""
    conn = get_db_connection()
    book = conn.execute(
        "SELECT * FROM library_books WHERE id = ?",
        (book_id,)
    ).fetchone()
    
    if not book:
        conn.close()
        return jsonify({
            "status": "error",
            "message": "Book not found"
        }), 404
    
    # Kiểm tra xem có ai đang mượn không
    borrowed_count = book['quantity'] - book['available']
    if borrowed_count > 0:
        conn.close()
        return jsonify({
            "status": "error",
            "message": f"Cannot delete. {borrowed_count} copies are currently borrowed"
        }), 400
    
    conn.execute("DELETE FROM library_books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    
    return jsonify({
        "status": "success",
        "message": "Book deleted successfully"
    }), 200

# ========================================
# API USER - Mượn và trả sách
# ========================================

@app.route("/api/user/library", methods=["GET"])
@user_required
def user_get_library(current_user):
    """User: Xem danh sách sách có sẵn trong thư viện"""
    conn = get_db_connection()
    books = conn.execute(
        "SELECT id, book_key, title, author, cover_url, quantity, available FROM library_books WHERE available > 0 ORDER BY title"
    ).fetchall()
    conn.close()
    
    books_list = [
        {
            "id": book['id'],
            "book_key": book['book_key'],
            "title": book['title'],
            "author": book['author'],
            "cover_url": book['cover_url'],
            "available": book['available']
        }
        for book in books
    ]
    
    return jsonify({
        "status": "success",
        "message": "Get available books successfully",
        "data": books_list
    }), 200

@app.route("/api/user/borrowed", methods=["GET"])
@user_required
def user_get_borrowed_books(current_user):
    """User: Xem danh sách sách đã mượn của mình"""
    user_id = current_user['user_id']
    
    conn = get_db_connection()
    books = conn.execute(
        """SELECT id, book_id, book_key, title, author, cover_url, borrowed_date
           FROM borrowed_books 
           WHERE user_id = ?
           ORDER BY borrowed_date DESC""",
        (user_id,)
    ).fetchall()
    conn.close()
    
    books_list = [
        {
            "id": book['id'],
            "book_id": book['book_id'],
            "book_key": book['book_key'],
            "title": book['title'],
            "author": book['author'],
            "cover_url": book['cover_url'],
            "borrowed_date": book['borrowed_date']
        }
        for book in books
    ]
    
    return jsonify({
        "status": "success",
        "message": "Get borrowed books successfully",
        "data": books_list
    }), 200

@app.route("/api/user/borrow/<int:book_id>", methods=["POST"])
@user_required
def user_borrow_book(current_user, book_id):
    """User: Mượn sách"""
    user_id = current_user['user_id']
    
    conn = get_db_connection()
    
    # Kiểm tra sách có tồn tại và còn không
    book = conn.execute(
        "SELECT * FROM library_books WHERE id = ?",
        (book_id,)
    ).fetchone()
    
    if not book:
        conn.close()
        return jsonify({
            "status": "error",
            "message": "Book not found"
        }), 404
    
    if book['available'] < 1:
        conn.close()
        return jsonify({
            "status": "error",
            "message": "Book is not available"
        }), 400
    
    # Kiểm tra user đã mượn sách này chưa
    already_borrowed = conn.execute(
        "SELECT id FROM borrowed_books WHERE user_id = ? AND book_key = ?",
        (user_id, book['book_key'])
    ).fetchone()
    
    if already_borrowed:
        conn.close()
        return jsonify({
            "status": "error",
            "message": "You have already borrowed this book"
        }), 400
    
    # Thêm vào borrowed_books
    cursor = conn.execute(
        """INSERT INTO borrowed_books (user_id, book_id, book_key, title, author, cover_url)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, book['id'], book['book_key'], book['title'], book['author'], book['cover_url'])
    )
    
    # Giảm available
    conn.execute(
        "UPDATE library_books SET available = available - 1 WHERE id = ?",
        (book_id,)
    )
    
    conn.commit()
    borrowed_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        "status": "success",
        "message": "Book borrowed successfully",
        "data": {
            "id": borrowed_id,
            "book_key": book['book_key'],
            "title": book['title']
        }
    }), 201

@app.route("/api/user/return/<int:borrowed_id>", methods=["DELETE"])
@user_required
def user_return_book(current_user, borrowed_id):
    """User: Trả sách"""
    user_id = current_user['user_id']
    
    conn = get_db_connection()
    
    # Kiểm tra bản ghi mượn sách
    borrowed = conn.execute(
        "SELECT * FROM borrowed_books WHERE id = ? AND user_id = ?",
        (borrowed_id, user_id)
    ).fetchone()
    
    if not borrowed:
        conn.close()
        return jsonify({
            "status": "error",
            "message": "Borrowed record not found"
        }), 404
    
    # Xóa khỏi borrowed_books
    conn.execute("DELETE FROM borrowed_books WHERE id = ?", (borrowed_id,))
    
    # Tăng available
    conn.execute(
        "UPDATE library_books SET available = available + 1 WHERE id = ?",
        (borrowed['book_id'],)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "status": "success",
        "message": "Book returned successfully"
    }), 200

# API Statistics (Admin only)
@app.route("/api/admin/statistics", methods=["GET"])
@admin_required
def admin_get_statistics(current_user):
    """Admin: Xem thống kê"""
    conn = get_db_connection()

    total_books = conn.execute("SELECT COUNT(*) as count FROM library_books").fetchone()['count']
    total_copies = conn.execute("SELECT SUM(quantity) as total FROM library_books").fetchone()['total'] or 0
    borrowed_count = conn.execute("SELECT COUNT(*) as count FROM borrowed_books").fetchone()['count']
    user_count = conn.execute("SELECT COUNT(*) as count FROM users WHERE role = 'user'").fetchone()['count']
    
    conn.close()
    
    return jsonify({
        "status": "success",
        "data": {
            "total_books": total_books,
            "total_copies": total_copies,
            "borrowed_count": borrowed_count,
            "user_count": user_count
        }
    }), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
