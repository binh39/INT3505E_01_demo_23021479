# 🚀 HƯỚNG DẪN CHẠY PROJECT

## ✅ Đã hoàn thành

- ✅ Backend Flask với JWT authentication
- ✅ Database đã được khởi tạo
- ✅ Server đang chạy tại http://localhost:5000
- ✅ Frontend HTML/CSS/JS đã sẵn sàng

## 📂 Cấu trúc Project

```
JWT/
├── backend/
│   ├── server.py           # Main Flask application
│   ├── database.py         # Database initialization
│   ├── auth.py            # JWT authentication
│   ├── config.py          # Configuration
│   ├── requirements.txt   # Python dependencies
│   └── library.db         # SQLite database (tự động tạo)
├── frontend/
│   ├── index.html         # Redirect to login
│   ├── login.html         # Trang đăng nhập
│   ├── admin.html         # Dashboard admin
│   └── user.html          # Dashboard user
└── README.md              # Tài liệu đầy đủ
```

## 🎯 CÁCH MỞ FRONTEND

### Cách 1: Sử dụng Live Server (Khuyến nghị)

1. Cài đặt extension "Live Server" trong VS Code
2. Right-click vào file `frontend/login.html`
3. Chọn "Open with Live Server"
4. Browser sẽ tự động mở tại http://127.0.0.1:5500/login.html

### Cách 2: Python HTTP Server

```powershell
cd frontend
python -m http.server 8080
```

Sau đó mở: http://localhost:8080/login.html

### Cách 3: Mở trực tiếp file

Mở file `frontend/login.html` trong browser (có thể có lỗi CORS)

## 👥 TÀI KHOẢN DEMO

### Admin

- Username: `admin`
- Password: `admin123`
- Quyền: Quản lý thư viện (thêm/sửa/xóa sách)

### User

- Username: `user`
- Password: `user123`
- Quyền: Mượn và trả sách

## 🧪 TEST WORKFLOW

### Test Admin:

1. Đăng nhập với admin/admin123
2. Xem thống kê thư viện
3. Thêm sách mới: Click "➕ Thêm sách mới"
4. Sửa sách: Click "✏️ Sửa" trên bất kỳ sách nào
5. Xóa sách: Click "🗑️ Xóa"

### Test User:

1. Logout admin
2. Đăng nhập với user/user123
3. Tab "Thư viện": Xem sách có sẵn
4. Click "📤 Mượn sách" để mượn
5. Tab "Sách đã mượn": Xem sách đã mượn
6. Click "📥 Trả sách" để trả

## 🔧 KIỂM TRA

### Backend đã chạy chưa?

```powershell
curl http://localhost:5000
```

Phải trả về JSON với message "Library Management System with JWT"

### Database có dữ liệu chưa?

```powershell
cd backend
python -c "import sqlite3; conn = sqlite3.connect('library.db'); print('Users:', conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]); print('Books:', conn.execute('SELECT COUNT(*) FROM library_books').fetchone()[0])"
```

## 📡 API ENDPOINTS

### Test Login API:

```powershell
$body = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method POST -Body $body -ContentType "application/json"
$response
```

### Test Admin API (cần token):

```powershell
$token = "YOUR_TOKEN_HERE"
$headers = @{
    "Authorization" = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:5000/api/admin/books" -Headers $headers
```

## 🐛 TROUBLESHOOTING

### Backend không chạy:

- Kiểm tra port 5000 có bị chiếm không
- Chạy lại: `python backend/server.py`

### Frontend lỗi CORS:

- Dùng Live Server hoặc HTTP Server
- KHÔNG mở trực tiếp file:// trong browser

### Token hết hạn:

- Login lại để lấy token mới
- Token hết hạn sau 1 giờ

### Không thể mượn sách:

- Kiểm tra sách còn available > 0
- Kiểm tra đã đăng nhập với role user

## 📊 CHỨC NĂNG CHI TIẾT

### Admin có thể:

✅ Xem thống kê: tổng sách, bản sao, lượt mượn, số user
✅ Thêm sách: book_key, title, author, cover_url, quantity
✅ Sửa sách: title, author, cover_url, quantity
✅ Xóa sách: chỉ khi không có ai mượn
✅ Quản lý số lượng: quantity và available tự động cập nhật

### User có thể:

✅ Xem thư viện: danh sách sách available > 0
✅ Mượn sách: mỗi user chỉ mượn 1 bản của mỗi sách
✅ Xem sách đã mượn: với thời gian mượn
✅ Trả sách: available tự động tăng

## 🎨 GIAO DIỆN

- **Login**: Form đẹp với gradient tím, có nút quick login
- **Admin Dashboard**: Card thống kê + grid sách với ảnh bìa
- **User Dashboard**: 2 tabs (Thư viện & Sách đã mượn)
- **Responsive**: Tự động điều chỉnh theo màn hình

## 🔐 BẢO MẬT

- ✅ JWT token authentication
- ✅ Password hashing (werkzeug)
- ✅ Role-based access control
- ✅ Token expiration (1 hour)
- ✅ Protected API endpoints

## 📈 DỮ LIỆU MẪU

Database đã có sẵn:

- 2 users (admin, user)
- 4 sách mẫu (Harry Potter, LOTR, 1984, To Kill a Mockingbird)

## 🚀 DEMO WORKFLOW ĐẦY ĐỦ

1. **Khởi động backend**: `python backend/server.py`
2. **Mở frontend**: Dùng Live Server mở `frontend/login.html`
3. **Login admin**: admin/admin123
4. **Thêm 2-3 sách mới**
5. **Logout → Login user**: user/user123
6. **Mượn 2-3 sách**
7. **Kiểm tra tab "Sách đã mượn"**
8. **Trả 1 sách**
9. **Logout → Login admin lại**
10. **Xem thống kê đã thay đổi**

## ✨ TÍNH NĂNG NỔI BẬT

1. **JWT Authentication**: Secure token-based auth
2. **Role-based Authorization**: Admin/User phân quyền rõ ràng
3. **Real-time Statistics**: Admin thấy thống kê real-time
4. **Inventory Management**: Số lượng sách tự động cập nhật khi mượn/trả
5. **Beautiful UI**: Gradient design, responsive, modern
6. **Error Handling**: Xử lý lỗi đầy đủ với thông báo rõ ràng

## 📞 HỖ TRỢ

Nếu gặp vấn đề:

1. Kiểm tra backend đang chạy
2. Kiểm tra frontend mở từ HTTP server
3. Check browser console (F12) để xem lỗi
4. Đọc README.md để biết thêm chi tiết

---

🎉 **PROJECT HOÀN CHỈNH VÀ SẴN SÀNG SỬ DỤNG!**
