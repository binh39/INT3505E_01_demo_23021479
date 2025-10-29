# Library Management System với JWT Authentication

Hệ thống quản lý thư viện với xác thực JWT và phân quyền Admin/User.

## 📋 Tính năng

### 🔐 Authentication

- Đăng nhập với JWT token
- Phân quyền rõ ràng: Admin và User
- Token tự động hết hạn sau 1 giờ

### 👑 Admin

- ✅ Xem thống kê thư viện
- ✅ Thêm sách mới vào thư viện
- ✅ Sửa thông tin sách (tiêu đề, tác giả, số lượng)
- ✅ Xóa sách khỏi thư viện
- ✅ Quản lý số lượng và tình trạng sách

### 👤 User

- ✅ Xem danh sách sách có sẵn trong thư viện
- ✅ Mượn sách
- ✅ Xem sách đã mượn
- ✅ Trả sách

## 🛠️ Cài đặt

### Backend (Flask)

1. Di chuyển vào thư mục backend:

```powershell
cd backend
```

2. Cài đặt các thư viện:

```powershell
pip install -r requirements.txt
```

3. Khởi tạo database (tự động tạo tài khoản mẫu):

```powershell
python database.py
```

4. Chạy server:

```powershell
python server.py
```

Server sẽ chạy tại: `http://localhost:5000`

### Frontend

1. Mở file `frontend/login.html` trong trình duyệt
2. Hoặc sử dụng Live Server trong VS Code

## 👥 Tài khoản mặc định

Sau khi khởi tạo database, hệ thống tự động tạo 2 tài khoản:

| Role  | Username | Password |
| ----- | -------- | -------- |
| Admin | admin    | admin123 |
| User  | user     | user123  |

## 📡 API Endpoints

### Authentication

- `POST /api/auth/login` - Đăng nhập
- `GET /api/auth/verify` - Kiểm tra token

### Admin APIs (Yêu cầu quyền admin)

- `GET /api/admin/books` - Lấy danh sách tất cả sách
- `POST /api/admin/books` - Thêm sách mới
- `PUT /api/admin/books/<id>` - Cập nhật sách
- `DELETE /api/admin/books/<id>` - Xóa sách
- `GET /api/admin/statistics` - Xem thống kê

### User APIs (Yêu cầu đăng nhập)

- `GET /api/user/library` - Xem sách có sẵn
- `GET /api/user/borrowed` - Xem sách đã mượn
- `POST /api/user/borrow/<id>` - Mượn sách
- `DELETE /api/user/return/<id>` - Trả sách

## 🗄️ Database Schema

### Bảng `users`

- id (INTEGER PRIMARY KEY)
- username (TEXT UNIQUE)
- password (TEXT) - Mã hóa bằng werkzeug
- role (TEXT) - 'admin' hoặc 'user'

### Bảng `library_books`

- id (INTEGER PRIMARY KEY)
- book_key (TEXT UNIQUE)
- title (TEXT)
- author (TEXT)
- cover_url (TEXT)
- quantity (INTEGER) - Tổng số lượng
- available (INTEGER) - Số lượng còn lại

### Bảng `borrowed_books`

- id (INTEGER PRIMARY KEY)
- user_id (INTEGER) - Foreign key đến users
- book_id (INTEGER) - Foreign key đến library_books
- book_key (TEXT)
- title (TEXT)
- author (TEXT)
- cover_url (TEXT)
- borrowed_date (TIMESTAMP)

## 🔒 Bảo mật

1. **JWT Authentication**: Tất cả API (trừ login) đều yêu cầu token
2. **Role-based Access Control**: Admin và User có quyền truy cập khác nhau
3. **Password Hashing**: Mật khẩu được mã hóa bằng werkzeug.security
4. **Token Expiration**: Token tự động hết hạn sau 1 giờ

## 📱 Giao diện

### Login Page

- Form đăng nhập đẹp mắt
- Hiển thị tài khoản demo để test
- Tự động chuyển hướng theo role

### Admin Dashboard

- Thống kê tổng quan (số sách, số bản sao, số lượt mượn, số user)
- Quản lý sách với form thêm/sửa/xóa
- Giao diện card hiển thị sách đẹp mắt

### User Dashboard

- Tab "Thư viện" để xem và mượn sách
- Tab "Sách đã mượn" để quản lý sách đã mượn
- Thống kê cá nhân

## 🎨 Công nghệ sử dụng

**Backend:**

- Flask 3.0.0 - Web framework
- Flask-CORS - Xử lý CORS
- PyJWT 2.8.0 - JWT authentication
- SQLite3 - Database
- Werkzeug - Password hashing

**Frontend:**

- HTML5, CSS3, JavaScript (Vanilla)
- Responsive design
- Gradient UI với màu sắc đẹp

## 🚀 Hướng dẫn sử dụng

1. **Đăng nhập với tài khoản admin**

   - Vào trang login
   - Nhập: admin / admin123
   - Thấy Admin Dashboard

2. **Quản lý sách (Admin)**

   - Click "➕ Thêm sách mới"
   - Điền thông tin sách
   - Click "Lưu"
   - Có thể sửa/xóa sách bất kỳ

3. **Đăng nhập với tài khoản user**

   - Logout admin
   - Login với: user / user123
   - Thấy User Dashboard

4. **Mượn sách (User)**

   - Tab "Thư viện"
   - Click "📤 Mượn sách"
   - Sách sẽ chuyển sang tab "Sách đã mượn"

5. **Trả sách (User)**
   - Tab "Sách đã mượn"
   - Click "📥 Trả sách"
   - Sách trở lại thư viện

## ⚙️ Configuration

File `backend/config.py`:

```python
SECRET_KEY = 'your-secret-key-change-in-production'
JWT_SECRET_KEY = 'jwt-secret-key-change-in-production'
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
DATABASE_NAME = 'library.db'
```

## 📝 Notes

- Thay đổi SECRET_KEY và JWT_SECRET_KEY trong production
- Database được tạo tự động khi chạy server lần đầu
- Frontend cần chạy từ HTTP server (không chạy trực tiếp file://)
- CORS đã được config cho phép tất cả origins (chỉ dùng development)

## 🐛 Troubleshooting

**Lỗi CORS:**

- Đảm bảo backend đang chạy trên port 5000
- Frontend phải chạy từ HTTP server

**Không kết nối được server:**

- Kiểm tra backend đã chạy: `python server.py`
- Kiểm tra port 5000 không bị chiếm

**Token hết hạn:**

- Login lại để lấy token mới
- Token mặc định hết hạn sau 1 giờ

## 📧 Contact

Nếu có vấn đề, vui lòng liên hệ hoặc tạo issue.
