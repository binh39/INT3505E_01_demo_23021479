# API Documentation Setup

## 📚 Tổng quan

Project này bao gồm:

- ✅ **OpenAPI 3.0 Specification**: `openapi.yaml` - Định nghĩa đầy đủ tất cả API endpoints
- ✅ **Swagger UI Standalone**: `docs.html` - Interactive API documentation
- ✅ **Chi tiết từ backend**: Bám sát 100% code trong `backend/server.py`

## 🚀 Cách sử dụng

### Option 1: Mở trực tiếp (Recommended)

```bash
# Mở file docs.html bằng browser
start docs.html   # Windows
open docs.html    # macOS
xdg-open docs.html # Linux
```

**Lưu ý**: Cần phải mở từ local web server hoặc allow CORS để load `openapi.yaml`.

### Option 2: Dùng Python HTTP Server

```bash
# Khởi động simple HTTP server tại thư mục project
python -m http.server 8080

# Mở browser
http://localhost:8080/docs.html
```

### Option 3: Dùng Live Server (VS Code)

1. Cài extension "Live Server" trong VS Code
2. Right-click `docs.html` → "Open with Live Server"
3. Browser tự động mở tại `http://127.0.0.1:5500/docs.html`

## 📖 Tính năng Swagger UI

### 1. Authentication

- Click nút **"Authorize"** ở góc phải trên
- Login bằng API `/api/sessions` để lấy access_token
- Paste token vào ô `Value` (không cần thêm "Bearer ")
- Click "Authorize" → Token sẽ tự động gắn vào tất cả requests

### 2. Try It Out

- Mở bất kỳ endpoint nào
- Click **"Try it out"**
- Điền parameters/body
- Click **"Execute"**
- Xem response thực tế từ backend

### 3. Demo Accounts

```
Admin: admin / admin123
User:  user / user123
```

### 4. Test Flow ví dụ

1. **Login** (POST /api/sessions)

   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```

   → Copy `access_token` từ response

2. **Authorize**
   → Paste token vào Swagger UI

3. **Get Statistics** (GET /api/statistics)
   → Click Execute với token đã authorize

4. **Create Book** (POST /api/books)

   ```json
   {
     "book_key": "TEST123",
     "title": "Test Book",
     "author": "Test Author",
     "quantity": 3
   }
   ```

5. **List Books** (GET /api/books?page=1&per_page=20)

6. **Logout** (DELETE /api/sessions)
   ```json
   {
     "refresh_token": "<your_refresh_token>"
   }
   ```

## 📋 Nội dung OpenAPI Spec

### Đã document đầy đủ:

#### Authentication APIs

- ✅ POST `/api/sessions` - Login (access + refresh tokens)
- ✅ POST `/api/sessions/refresh` - Refresh access token
- ✅ DELETE `/api/sessions` - Logout (blacklist + revoke)
- ✅ GET `/api/sessions/me` - Verify token

#### Admin - Books APIs

- ✅ GET `/api/books` - List all books (pagination)
- ✅ POST `/api/books` - Create book
- ✅ GET `/api/books/{book_id}` - Get book detail
- ✅ PUT `/api/books/{book_id}` - Update book
- ✅ DELETE `/api/books/{book_id}` - Delete book

#### Admin - Statistics

- ✅ GET `/api/statistics` - Get library statistics

#### User - Borrowing

- ✅ GET `/api/users/{user_id}/borrowed-books` - List borrowed books
- ✅ POST `/api/users/{user_id}/borrowed-books` - Borrow book
- ✅ DELETE `/api/users/{user_id}/borrowed-books/{book_id}` - Return book

### Thông tin chi tiết mỗi endpoint:

- ✅ Request schemas (body, parameters, headers)
- ✅ Response schemas (200, 201, 400, 401, 403, 404, 409)
- ✅ HATEOAS links structure
- ✅ Meta information (pagination, timestamps, etc.)
- ✅ Error responses với examples
- ✅ Security requirements (Bearer JWT)
- ✅ Scopes theo role (admin/user)
- ✅ Token expiry times (access: 5min, refresh: 1h)

## 🎨 Customization

### Thay đổi màu sắc brand

Chỉnh CSS trong `docs.html`:

```css
.topbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

### Thay đổi server URL

Chỉnh trong `openapi.yaml`:

```yaml
servers:
  - url: http://localhost:5000
    description: Development server
  - url: https://api.library.com
    description: Production server
```

## 🔧 Validation

### Check spec với Swagger Editor Online

```
https://editor.swagger.io/
```

→ Copy nội dung `openapi.yaml` vào để validate

### Hoặc dùng CLI

```bash
npm install -g @apidevtools/swagger-cli
swagger-cli validate openapi.yaml
```

## 📝 File Structure

```
JWT/
├── openapi.yaml          # OpenAPI 3.0 specification
├── docs.html            # Swagger UI standalone
├── backend/
│   ├── server.py        # Flask API (source of truth)
│   ├── auth.py          # JWT logic
│   ├── database.py      # DB schema
│   └── config.py        # Config (token expiry)
├── frontend/
│   ├── login.html
│   ├── admin.html
│   ├── user.html
│   └── auth.js
└── test_api.ps1         # PowerShell test script
```

## 🎯 So sánh với Backend

| Spec trong openapi.yaml    | Code trong server.py                                                          |
| -------------------------- | ----------------------------------------------------------------------------- |
| JWT Access Token (5 min)   | Config.JWT_ACCESS_TOKEN_EXPIRES = 300                                         |
| JWT Refresh Token (1 hour) | Config.JWT_REFRESH_TOKEN_EXPIRES = 3600                                       |
| Scopes admin               | `["read:books", "write:books", "manage:users", "read:stats", "borrow:write"]` |
| Scopes user                | `["read:books", "borrow:write"]`                                              |
| Response format            | `create_response(status, message, data, links, meta)`                         |
| Pagination default         | page=1, per_page=20                                                           |
| Demo accounts              | admin/admin123, user/user123                                                  |

## ✅ Quality Checklist

- [x] Tất cả endpoints từ backend đã được document
- [x] Request/Response schemas đầy đủ
- [x] HTTP status codes chính xác (200, 201, 400, 401, 403, 404, 409)
- [x] HATEOAS links structure
- [x] JWT Authentication flow (login → refresh → logout)
- [x] Token expiry times đúng (5 phút access, 1 giờ refresh)
- [x] Scopes theo role
- [x] Pagination parameters
- [x] Error responses với examples
- [x] Demo accounts documented
- [x] Security schemes (Bearer JWT)

## 🚀 Next Steps

1. **Test API**: Mở `docs.html` và test từng endpoint
2. **Validate**: Check spec với Swagger Editor
3. **Share**: Gửi `openapi.yaml` cho team/clients
4. **Generate SDK**: Dùng OpenAPI Generator để tạo client SDKs

## 📞 Support

Nếu có vấn đề:

1. Check backend server đang chạy: `http://localhost:5000`
2. Check CORS settings trong `server.py`
3. Check browser console for errors
4. Validate `openapi.yaml` syntax

---

**Created**: November 4, 2025  
**Version**: 2.0.0  
**Spec**: OpenAPI 3.0.3
