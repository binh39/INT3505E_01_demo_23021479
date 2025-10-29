import sqlite3
from werkzeug.security import generate_password_hash
from config import Config

def get_db_connection():
    """Tạo kết nối đến database"""
    conn = sqlite3.connect(Config.DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Khởi tạo database với các bảng cần thiết"""
    conn = sqlite3.connect(Config.DATABASE_NAME)
    c = conn.cursor()
    
    # Bảng users (username, password, role)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
        )
    """)
    
    # Bảng library_books (sách trong thư viện - admin quản lý)
    c.execute("""
        CREATE TABLE IF NOT EXISTS library_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_key TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            cover_url TEXT,
            quantity INTEGER DEFAULT 1,
            available INTEGER DEFAULT 1
        )
    """)
    
    # Bảng borrowed_books (sách user đã mượn)
    c.execute("""
        CREATE TABLE IF NOT EXISTS borrowed_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            book_key TEXT NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            cover_url TEXT,
            borrowed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (book_id) REFERENCES library_books (id),
            UNIQUE(user_id, book_key)
        )
    """)
    
    # Tạo 2 tài khoản mẫu nếu chưa có
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    
    if count == 0:
        # Tài khoản admin: admin/admin123
        admin_password = generate_password_hash('admin123')
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ('admin', admin_password, 'admin'))
        
        # Tài khoản user: user/user123
        user_password = generate_password_hash('user123')
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ('user', user_password, 'user'))
        
        print("✅ Đã tạo tài khoản mặc định:")
        print("   - Admin: admin/admin123")
        print("   - User: user/user123")
    
    # Thêm một số sách mẫu vào thư viện nếu chưa có
    c.execute("SELECT COUNT(*) FROM library_books")
    book_count = c.fetchone()[0]
    
    if book_count == 0:
        sample_books = [
            ('OL123456W', 'Harry Potter and the Philosophers Stone', 'J.K. Rowling', 
             'https://covers.openlibrary.org/b/id/8739161-M.jpg', 5, 5),
            ('OL123457W', 'The Lord of the Rings', 'J.R.R. Tolkien',
             'https://covers.openlibrary.org/b/id/8739162-M.jpg', 3, 3),
            ('OL123458W', '1984', 'George Orwell',
             'https://covers.openlibrary.org/b/id/8739163-M.jpg', 4, 4),
            ('OL123459W', 'To Kill a Mockingbird', 'Harper Lee',
             'https://covers.openlibrary.org/b/id/8739164-M.jpg', 2, 2),
        ]
        
        c.executemany("""
            INSERT INTO library_books (book_key, title, author, cover_url, quantity, available)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_books)
        
        print("✅ Đã thêm sách mẫu vào thư viện")
    
    conn.commit()
    conn.close()
    print("✅ Database đã được khởi tạo thành công!")

if __name__ == "__main__":
    init_db()
