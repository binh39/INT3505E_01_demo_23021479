from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db_connection, init_db
from auth import generate_token, admin_required, user_required, token_required
from config import Config
import datetime

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

init_db()

# ========================================
# Helper Functions for HATEOAS
# ========================================
def create_response(status, message, data=None, links=None, meta=None, status_code=200):
    """Tạo response đồng nhất theo format chuẩn với HATEOAS"""
    response = {
        "status": status,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    if links:
        response["links"] = links
    
    if meta:
        response["meta"] = meta
    
    return jsonify(response), status_code

def get_book_links(book_id, is_admin=False):
    """Tạo HATEOAS links cho book resource"""
    links = {
        "self": {"href": f"/api/books/{book_id}", "method": "GET"}
    }
    
    if is_admin:
        links["update"] = {"href": f"/api/books/{book_id}", "method": "PUT"}
        links["delete"] = {"href": f"/api/books/{book_id}", "method": "DELETE"}
        links["collection"] = {"href": "/api/books", "method": "GET"}
    
    return links

def get_borrowed_book_links(user_id, book_id):
    """Tạo HATEOAS links cho borrowed book resource"""
    return {
        "self": {"href": f"/api/users/{user_id}/borrowed-books/{book_id}", "method": "GET"},
        "return": {"href": f"/api/users/{user_id}/borrowed-books/{book_id}", "method": "DELETE"},
        "collection": {"href": f"/api/users/{user_id}/borrowed-books", "method": "GET"}
    }

# ========================================
# API Authentication
# ========================================
@app.route("/")
def home():
    """Root endpoint với HATEOAS links"""
    return create_response(
        status="success",
        message="Library Management System with JWT Authentication",
        data={
            "version": "2.0",
            "description": "RESTful API with JWT and HATEOAS"
        },
        links={
            "self": {"href": "/", "method": "GET"},
            "login": {"href": "/api/sessions", "method": "POST"},
            "verify": {"href": "/api/sessions/me", "method": "GET"},
            "books": {"href": "/api/books", "method": "GET"},
            "statistics": {"href": "/api/statistics", "method": "GET"}
        },
        meta={
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
    )

@app.route("/api/sessions", methods=["POST"])
def login():
    """API đăng nhập - trả về JWT token"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return create_response(
            status="error",
            message="Username and password are required",
            meta={"required_fields": ["username", "password"]},
            status_code=400
        )
    
    conn = get_db_connection()
    user = conn.execute(
        "SELECT id, username, password, role FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()
    
    if not user or not check_password_hash(user['password'], password):
        return create_response(
            status="error",
            message="Invalid username or password",
            status_code=401
        )
    
    # Tạo token
    token = generate_token(user['id'], user['username'], user['role'])
    
    user_data = {
        "id": user['id'],
        "username": user['username'],
        "role": user['role'],
        "token": token
    }
    
    links = {
        "self": {"href": "/api/sessions", "method": "POST"},
        "verify": {"href": "/api/sessions/me", "method": "GET"},
        "logout": {"href": "/api/sessions/me", "method": "DELETE"}
    }
    
    if user['role'] == 'admin':
        links["books"] = {"href": "/api/books", "method": "GET"}
        links["statistics"] = {"href": "/api/statistics", "method": "GET"}
    else:
        links["borrowed_books"] = {"href": f"/api/users/{user['id']}/borrowed-books", "method": "GET"}
        links["available_books"] = {"href": "/api/books", "method": "GET"}
    
    return create_response(
        status="success",
        message="Login successful",
        data=user_data,
        links=links,
        meta={
            "token_expires_in": Config.JWT_ACCESS_TOKEN_EXPIRES,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        },
        status_code=200
    )

@app.route("/api/sessions/me", methods=["GET"])
@token_required
def verify_token(current_user):
    """API kiểm tra token còn hiệu lực không"""
    user_data = {
        "id": current_user['user_id'],
        "username": current_user['username'],
        "role": current_user['role']
    }
    
    links = {
        "self": {"href": "/api/sessions/me", "method": "GET"},
        "logout": {"href": "/api/sessions/me", "method": "DELETE"}
    }
    
    if current_user['role'] == 'admin':
        links["books"] = {"href": "/api/books", "method": "GET"}
        links["statistics"] = {"href": "/api/statistics", "method": "GET"}
    else:
        links["borrowed_books"] = {"href": f"/api/users/{current_user['user_id']}/borrowed-books", "method": "GET"}
        links["available_books"] = {"href": "/api/books", "method": "GET"}
    
    return create_response(
        status="success",
        message="Token is valid",
        data=user_data,
        links=links,
        meta={
            "token_expires_at": datetime.datetime.fromtimestamp(current_user['exp']).isoformat() + "Z",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        },
        status_code=200
    )

# ========================================
# API ADMIN - Books Management
# ========================================

@app.route("/api/books", methods=["GET"])
@admin_required
def admin_get_all_books(current_user):
    """Admin: Lấy danh sách tất cả sách trong thư viện"""
    # Lấy query parameters cho pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    
    # Đếm tổng số sách
    total_count = conn.execute("SELECT COUNT(*) as count FROM library_books").fetchone()['count']
    
    # Lấy sách với pagination
    books = conn.execute(
        "SELECT id, book_key, title, author, cover_url, quantity, available FROM library_books ORDER BY id DESC LIMIT ? OFFSET ?",
        (per_page, offset)
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
            "available": book['available'],
            "borrowed": book['quantity'] - book['available'],
            "links": get_book_links(book['id'], is_admin=True)
        }
        for book in books
    ]
    
    # Tạo pagination links
    links = {
        "self": {"href": f"/api/books?page={page}&per_page={per_page}", "method": "GET"},
        "create": {"href": "/api/books", "method": "POST"}
    }
    
    if page > 1:
        links["prev"] = {"href": f"/api/books?page={page-1}&per_page={per_page}", "method": "GET"}
    
    if offset + per_page < total_count:
        links["next"] = {"href": f"/api/books?page={page+1}&per_page={per_page}", "method": "GET"}
    
    return create_response(
        status="success",
        message="Retrieved all library books successfully",
        data=books_list,
        links=links,
        meta={
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        },
        status_code=200
    )

@app.route("/api/books", methods=["POST"])
@admin_required
def admin_add_book(current_user):
    """Admin: Thêm sách mới vào thư viện"""
    data = request.get_json()
    book_key = data.get("book_key")
    title = data.get("title")
    author = data.get("author", "Unknown")
    cover_url = data.get("cover_url", "")
    quantity = data.get("quantity", 1)
    
    # Validation
    if not book_key or not title:
        return create_response(
            status="error",
            message="book_key and title are required",
            meta={"required_fields": ["book_key", "title"]},
            status_code=400
        )
    
    if quantity < 1:
        return create_response(
            status="error",
            message="quantity must be at least 1",
            meta={"min_quantity": 1},
            status_code=400
        )
    
    conn = get_db_connection()
    
    # Kiểm tra sách đã tồn tại chưa
    existing = conn.execute(
        "SELECT id FROM library_books WHERE book_key = ?",
        (book_key,)
    ).fetchone()
    
    if existing:
        conn.close()
        return create_response(
            status="error",
            message=f"Book with book_key '{book_key}' already exists",
            links={"existing_book": {"href": f"/api/books/{existing['id']}", "method": "GET"}},
            status_code=409
        )
    
    # Thêm sách mới
    cursor = conn.execute(
        """INSERT INTO library_books (book_key, title, author, cover_url, quantity, available)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (book_key, title, author, cover_url, quantity, quantity)
    )
    conn.commit()
    book_id = cursor.lastrowid
    conn.close()
    
    book_data = {
        "id": book_id,
        "book_key": book_key,
        "title": title,
        "author": author,
        "cover_url": cover_url,
        "quantity": quantity,
        "available": quantity,
        "borrowed": 0
    }
    
    return create_response(
        status="success",
        message="Book created successfully",
        data=book_data,
        links=get_book_links(book_id, is_admin=True),
        meta={
            "created_at": datetime.datetime.utcnow().isoformat() + "Z",
            "created_by": current_user['username']
        },
        status_code=201
    )

@app.route("/api/books/<int:book_id>", methods=["GET"])
@token_required
def get_book_detail(current_user, book_id):
    """Lấy thông tin chi tiết một cuốn sách"""
    conn = get_db_connection()
    book = conn.execute(
        "SELECT * FROM library_books WHERE id = ?",
        (book_id,)
    ).fetchone()
    conn.close()
    
    if not book:
        return create_response(
            status="error",
            message=f"Book with id {book_id} not found",
            links={"all_books": {"href": "/api/books", "method": "GET"}},
            status_code=404
        )
    
    book_data = {
        "id": book['id'],
        "book_key": book['book_key'],
        "title": book['title'],
        "author": book['author'],
        "cover_url": book['cover_url'],
        "quantity": book['quantity'],
        "available": book['available'],
        "borrowed": book['quantity'] - book['available']
    }
    
    is_admin = current_user['role'] == 'admin'
    
    return create_response(
        status="success",
        message="Book retrieved successfully",
        data=book_data,
        links=get_book_links(book_id, is_admin=is_admin),
        meta={
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        },
        status_code=200
    )

@app.route("/api/books/<int:book_id>", methods=["PUT"])
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
        return create_response(
            status="error",
            message=f"Book with id {book_id} not found",
            links={"all_books": {"href": "/api/books", "method": "GET"}},
            status_code=404
        )
    
    # Cập nhật các trường
    title = data.get("title", book['title'])
    author = data.get("author", book['author'])
    cover_url = data.get("cover_url", book['cover_url'])
    quantity = data.get("quantity", book['quantity'])
    
    # Validation
    if quantity < 1:
        conn.close()
        return create_response(
            status="error",
            message="quantity must be at least 1",
            meta={"min_quantity": 1},
            status_code=400
        )
    
    # Tính toán available mới
    borrowed_count = book['quantity'] - book['available']
    new_available = quantity - borrowed_count
    
    if new_available < 0:
        conn.close()
        return create_response(
            status="error",
            message=f"Cannot reduce quantity. {borrowed_count} copies are currently borrowed",
            meta={
                "current_quantity": book['quantity'],
                "borrowed_count": borrowed_count,
                "min_required_quantity": borrowed_count
            },
            status_code=400
        )
    
    conn.execute(
        """UPDATE library_books 
           SET title = ?, author = ?, cover_url = ?, quantity = ?, available = ?
           WHERE id = ?""",
        (title, author, cover_url, quantity, new_available, book_id)
    )
    conn.commit()
    conn.close()
    
    book_data = {
        "id": book_id,
        "book_key": book['book_key'],
        "title": title,
        "author": author,
        "cover_url": cover_url,
        "quantity": quantity,
        "available": new_available,
        "borrowed": borrowed_count
    }
    
    return create_response(
        status="success",
        message="Book updated successfully",
        data=book_data,
        links=get_book_links(book_id, is_admin=True),
        meta={
            "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "updated_by": current_user['username']
        },
        status_code=200
    )

@app.route("/api/books/<int:book_id>", methods=["DELETE"])
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
        return create_response(
            status="error",
            message=f"Book with id {book_id} not found",
            links={"all_books": {"href": "/api/books", "method": "GET"}},
            status_code=404
        )
    
    # Kiểm tra xem có ai đang mượn không
    borrowed_count = book['quantity'] - book['available']
    if borrowed_count > 0:
        conn.close()
        return create_response(
            status="error",
            message=f"Cannot delete book. {borrowed_count} copies are currently borrowed",
            data={
                "book_id": book_id,
                "title": book['title'],
                "borrowed_count": borrowed_count
            },
            links={
                "self": {"href": f"/api/books/{book_id}", "method": "GET"}
            },
            status_code=409
        )
    
    # Lưu thông tin trước khi xóa
    deleted_book = {
        "id": book['id'],
        "book_key": book['book_key'],
        "title": book['title'],
        "author": book['author']
    }
    
    conn.execute("DELETE FROM library_books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    
    return create_response(
        status="success",
        message="Book deleted successfully",
        data=deleted_book,
        links={
            "all_books": {"href": "/api/books", "method": "GET"},
            "create_new": {"href": "/api/books", "method": "POST"}
        },
        meta={
            "deleted_at": datetime.datetime.utcnow().isoformat() + "Z",
            "deleted_by": current_user['username']
        },
        status_code=200
    )

# API Statistics (Admin only)
@app.route("/api/statistics", methods=["GET"])
@admin_required
def admin_get_statistics(current_user):
    """Admin: Xem thống kê thư viện"""
    conn = get_db_connection()

    total_books = conn.execute("SELECT COUNT(*) as count FROM library_books").fetchone()['count']
    total_copies = conn.execute("SELECT SUM(quantity) as total FROM library_books").fetchone()['total'] or 0
    total_available = conn.execute("SELECT SUM(available) as total FROM library_books").fetchone()['total'] or 0
    borrowed_count = conn.execute("SELECT COUNT(*) as count FROM borrowed_books").fetchone()['count']
    user_count = conn.execute("SELECT COUNT(*) as count FROM users WHERE role = 'user'").fetchone()['count']
    admin_count = conn.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'").fetchone()['count']
    
    # Top 5 sách được mượn nhiều nhất
    top_borrowed = conn.execute("""
        SELECT lb.id, lb.title, lb.author, COUNT(bb.id) as borrow_count
        FROM library_books lb
        LEFT JOIN borrowed_books bb ON lb.id = bb.book_id
        GROUP BY lb.id
        ORDER BY borrow_count DESC
        LIMIT 5
    """).fetchall()
    
    conn.close()
    
    statistics = {
        "library": {
            "total_unique_books": total_books,
            "total_copies": total_copies,
            "total_available": total_available,
            "total_borrowed": total_copies - total_available
        },
        "borrowing": {
            "total_borrowed_transactions": borrowed_count
        },
        "users": {
            "total_users": user_count,
            "total_admins": admin_count
        },
        "top_borrowed_books": [
            {
                "id": book['id'],
                "title": book['title'],
                "author": book['author'],
                "times_borrowed": book['borrow_count']
            }
            for book in top_borrowed
        ]
    }
    
    return create_response(
        status="success",
        message="Statistics retrieved successfully",
        data=statistics,
        links={
            "self": {"href": "/api/statistics", "method": "GET"},
            "books": {"href": "/api/books", "method": "GET"}
        },
        meta={
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "requested_by": current_user['username']
        },
        status_code=200
    )

# ========================================
# API USER - Borrowing Books
# ========================================

@app.route("/api/users/<int:user_id>/borrowed-books", methods=["GET"])
@user_required
def user_get_borrowed_books(current_user, user_id):
    """User: Xem danh sách sách đã mượn của mình"""
    # Kiểm tra user chỉ có thể xem sách của chính mình
    if current_user['user_id'] != user_id and current_user['role'] != 'admin':
        return create_response(
            status="error",
            message="Access denied. You can only view your own borrowed books",
            status_code=403
        )
    
    conn = get_db_connection()
    books = conn.execute(
        """SELECT bb.id, bb.book_id, bb.book_key, bb.title, bb.author, bb.cover_url, bb.borrowed_date,
                  lb.available
           FROM borrowed_books bb
           LEFT JOIN library_books lb ON bb.book_id = lb.id
           WHERE bb.user_id = ?
           ORDER BY bb.borrowed_date DESC""",
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
            "borrowed_date": book['borrowed_date'],
            "links": get_borrowed_book_links(user_id, book['book_id'])
        }
        for book in books
    ]
    
    return create_response(
        status="success",
        message="Retrieved borrowed books successfully",
        data=books_list,
        links={
            "self": {"href": f"/api/users/{user_id}/borrowed-books", "method": "GET"},
            "available_books": {"href": "/api/books", "method": "GET"}
        },
        meta={
            "total_borrowed": len(books_list),
            "user_id": user_id,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        },
        status_code=200
    )

@app.route("/api/users/<int:user_id>/borrowed-books", methods=["POST"])
@user_required
def user_borrow_book(current_user, user_id):
    """User: Mượn sách"""
    # Kiểm tra user chỉ có thể mượn cho chính mình
    if current_user['user_id'] != user_id:
        return create_response(
            status="error",
            message="Access denied. You can only borrow books for yourself",
            status_code=403
        )
    
    data = request.get_json()
    book_id = data.get("book_id")
    
    if not book_id:
        return create_response(
            status="error",
            message="book_id is required",
            meta={"required_fields": ["book_id"]},
            status_code=400
        )
    
    conn = get_db_connection()
    
    # Kiểm tra sách có tồn tại và còn không
    book = conn.execute(
        "SELECT * FROM library_books WHERE id = ?",
        (book_id,)
    ).fetchone()
    
    if not book:
        conn.close()
        return create_response(
            status="error",
            message=f"Book with id {book_id} not found",
            links={"available_books": {"href": "/api/books", "method": "GET"}},
            status_code=404
        )
    
    if book['available'] < 1:
        conn.close()
        return create_response(
            status="error",
            message=f"Book '{book['title']}' is not available for borrowing",
            data={
                "book_id": book_id,
                "title": book['title'],
                "available": 0
            },
            links={"book_details": {"href": f"/api/books/{book_id}", "method": "GET"}},
            status_code=409
        )
    
    # Kiểm tra user đã mượn sách này chưa
    already_borrowed = conn.execute(
        "SELECT id FROM borrowed_books WHERE user_id = ? AND book_id = ?",
        (user_id, book_id)
    ).fetchone()
    
    if already_borrowed:
        conn.close()
        return create_response(
            status="error",
            message=f"You have already borrowed this book",
            links={
                "borrowed_books": {"href": f"/api/users/{user_id}/borrowed-books", "method": "GET"},
                "return_book": {"href": f"/api/users/{user_id}/borrowed-books/{book_id}", "method": "DELETE"}
            },
            status_code=409
        )
    
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
    
    borrowed_data = {
        "id": borrowed_id,
        "book_id": book['id'],
        "book_key": book['book_key'],
        "title": book['title'],
        "author": book['author'],
        "cover_url": book['cover_url'],
        "borrowed_date": datetime.datetime.utcnow().isoformat() + "Z"
    }
    
    return create_response(
        status="success",
        message="Book borrowed successfully",
        data=borrowed_data,
        links=get_borrowed_book_links(user_id, book_id),
        meta={
            "borrowed_at": datetime.datetime.utcnow().isoformat() + "Z",
            "borrowed_by": current_user['username']
        },
        status_code=201
    )

@app.route("/api/users/<int:user_id>/borrowed-books/<int:book_id>", methods=["DELETE"])
@user_required
def user_return_book(current_user, user_id, book_id):
    """User: Trả sách"""
    # Kiểm tra user chỉ có thể trả sách của chính mình
    if current_user['user_id'] != user_id and current_user['role'] != 'admin':
        return create_response(
            status="error",
            message="Access denied. You can only return your own borrowed books",
            status_code=403
        )
    
    conn = get_db_connection()
    
    # Kiểm tra bản ghi mượn sách
    borrowed = conn.execute(
        "SELECT * FROM borrowed_books WHERE book_id = ? AND user_id = ?",
        (book_id, user_id)
    ).fetchone()
    
    if not borrowed:
        conn.close()
        return create_response(
            status="error",
            message=f"No borrowed record found for book_id {book_id}",
            links={
                "borrowed_books": {"href": f"/api/users/{user_id}/borrowed-books", "method": "GET"},
                "available_books": {"href": "/api/books", "method": "GET"}
            },
            status_code=404
        )
    
    # Lưu thông tin trước khi xóa
    returned_book = {
        "id": borrowed['id'],
        "book_id": borrowed['book_id'],
        "book_key": borrowed['book_key'],
        "title": borrowed['title'],
        "author": borrowed['author'],
        "borrowed_date": borrowed['borrowed_date']
    }
    
    # Xóa khỏi borrowed_books
    conn.execute("DELETE FROM borrowed_books WHERE book_id = ? AND user_id = ?", (book_id, user_id))
    
    # Tăng available
    conn.execute(
        "UPDATE library_books SET available = available + 1 WHERE id = ?",
        (borrowed['book_id'],)
    )
    
    conn.commit()
    conn.close()
    
    return create_response(
        status="success",
        message="Book returned successfully",
        data=returned_book,
        links={
            "borrowed_books": {"href": f"/api/users/{user_id}/borrowed-books", "method": "GET"},
            "available_books": {"href": "/api/books", "method": "GET"},
            "borrow_again": {"href": f"/api/users/{user_id}/borrowed-books", "method": "POST"}
        },
        meta={
            "returned_at": datetime.datetime.utcnow().isoformat() + "Z",
            "returned_by": current_user['username']
        },
        status_code=200
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
