# 📚 Library API - Simple RESTful Backend

Backend đơn giản với Flask và SQLite để quản lý mượn trả sách.

## 🚀 Quick Start

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Chạy server
```bash
python app.py
```

Server sẽ chạy tại: **http://localhost:5000**

## 🔐 Authentication

Tất cả các endpoints (trừ `/`) yêu cầu Bearer Token trong header:

```
Authorization: Bearer demo123
```

## 📖 API Endpoints

### 1. **GET /api/books** - Lấy danh sách sách đã mượn

**Request:**
```bash
curl -H "Authorization: Bearer demo123" http://localhost:5000/api/books
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Get borrowed books successfully",
  "data": [
    {
      "book_key": "B001",
      "title": "Python Programming",
      "author": "Lewandowski",
      "cover_url": "http://example.com/cover.jpg",
      "_links": {
        "self": { "href": "/api/books/B001", "method": "GET" },
        "return": { "href": "/api/books/B001", "method": "DELETE" }
      }
    }
  ],
  "_links": {
    "self": { "href": "/api/books", "method": "GET" },
    "borrow": { "href": "/api/books", "method": "POST" }
  }
}
```

**Response (304):** Not Modified (nếu có If-None-Match header)

---

### 2. **POST /api/books** - Mượn sách mới

**Request:**
```bash
curl -X POST http://localhost:5000/api/books \
  -H "Authorization: Bearer demo123" \
  -H "Content-Type: application/json" \
  -d '{
    "book_key": "B002",
    "title": "Flask Web Development",
    "author": "Miguel Grinberg",
    "cover_url": "http://example.com/flask.jpg"
  }'
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Borrowed successfully",
  "data": {
    "book_key": "B002",
    "_links": {
      "self": { "href": "/api/books/B002", "method": "GET" },
      "return": { "href": "/api/books/B002", "method": "DELETE" },
      "all": { "href": "/api/books", "method": "GET" }
    }
  }
}
```

**Response (200):** Sách đã được mượn trước đó
```json
{
  "status": "exists",
  "message": "Already borrowed"
}
```

**Response (400 Bad Request):** Thiếu book_key
```json
{
  "status": "error",
  "message": "Missing book_key"
}
```

---

### 3. **GET /api/books/{book_key}** - Lấy thông tin chi tiết sách

**Request:**
```bash
curl -H "Authorization: Bearer demo123" http://localhost:5000/api/books/B001
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Get a borrowed book successfully",
  "data": {
    "book_key": "B001",
    "title": "Python Programming",
    "author": "Lewandowski",
    "cover_url": "http://example.com/cover.jpg",
    "_links": {
      "self": { "href": "/api/books/B001", "method": "GET" },
      "return": { "href": "/api/books/B001", "method": "DELETE" },
      "all": { "href": "/api/books", "method": "GET" }
    }
  }
}
```

**Response (404 Not Found):**
```json
{
  "status": "error",
  "message": "Book not found"
}
```

**Response (304):** Not Modified (nếu có If-None-Match header)

---

### 4. **DELETE /api/books/{book_key}** - Trả sách

**Request:**
```bash
curl -X DELETE http://localhost:5000/api/books/B001 \
  -H "Authorization: Bearer demo123"
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Returned successfully",
  "data": {
    "_links": {
      "self": { "href": "/api/books", "method": "GET" },
      "borrow": { "href": "/api/books", "method": "POST" }
    }
  }
}
```

**Response (404 Not Found):**
```json
{
  "status": "error",
  "message": "Book not found"
}
```

---

## 🔗 RESTful Design Features

✅ **Proper HTTP Methods:**
- `GET` - Lấy dữ liệu
- `POST` - Tạo mới
- `DELETE` - Xóa

✅ **HTTP Status Codes:**
- `200 OK` - Thành công
- `201 Created` - Tạo mới thành công
- `304 Not Modified` - Dữ liệu không thay đổi (cache)
- `400 Bad Request` - Lỗi validate
- `401 Unauthorized` - Thiếu authentication
- `404 Not Found` - Không tìm thấy resource
- `500 Internal Server Error` - Lỗi server

✅ **HATEOAS (Hypermedia):**
- Mỗi response có `_links` để client biết các actions có thể thực hiện

✅ **ETag Caching:**
- Header `ETag` để cache validation
- Client gửi `If-None-Match` để check cache
- Server trả `304` nếu data không đổi

✅ **Stateless:**
- Mỗi request độc lập
- Authentication qua Bearer Token

## 🗄️ Database Schema

**Table: borrowed_books**
```sql
CREATE TABLE borrowed_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_key TEXT UNIQUE NOT NULL,
    title TEXT,
    author TEXT,
    cover_url TEXT,
    borrowed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📁 Project Structure

```
service_operation/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── library.db            # SQLite database (auto-created)
├── openapi2.yaml         # OpenAPI specification
└── README.md             # Documentation
```

## 🧪 Testing với curl

### Test authentication
```bash
# Missing token - 401
curl http://localhost:5000/api/books

# Valid token - 200
curl -H "Authorization: Bearer demo123" http://localhost:5000/api/books
```

### Test CRUD operations
```bash
# 1. List books (empty)
curl -H "Authorization: Bearer demo123" http://localhost:5000/api/books

# 2. Borrow a book
curl -X POST http://localhost:5000/api/books \
  -H "Authorization: Bearer demo123" \
  -H "Content-Type: application/json" \
  -d '{"book_key": "B001", "title": "Test Book", "author": "Test Author"}'

# 3. Get book details
curl -H "Authorization: Bearer demo123" http://localhost:5000/api/books/B001

# 4. Return book
curl -X DELETE http://localhost:5000/api/books/B001 \
  -H "Authorization: Bearer demo123"
```

### Test caching
```bash
# First request - get ETag
curl -i -H "Authorization: Bearer demo123" http://localhost:5000/api/books

# Second request with ETag - should return 304
curl -i -H "Authorization: Bearer demo123" \
  -H "If-None-Match: <etag-from-previous-response>" \
  http://localhost:5000/api/books
```

## 🔧 Configuration

**app.py:**
- `DB_NAME = "library.db"` - Database file name
- `API_TOKEN = "demo123"` - Bearer token for authentication
- `port=5000` - Server port

## 📝 Notes

- Database file `library.db` được tạo tự động khi chạy lần đầu
- CORS được enable cho tất cả origins (development only)
- Debug mode được bật (development only)
- Token `demo123` chỉ dùng cho demo, không dùng trong production

## 🆚 So sánh với serverexample.py

**Giống:**
- ✅ Flask + SQLite
- ✅ Bearer token authentication
- ✅ HATEOAS links
- ✅ ETag caching
- ✅ CORS support
- ✅ RESTful endpoints

**Khác:**
- 📝 Code structure rõ ràng hơn với comments
- 🚀 Có startup banner đẹp
- 🔧 Có error handlers
- 📖 README documentation đầy đủ
- 🎯 URL `/api/books` thay vì `/api/v5/books`

## 🚀 Next Steps

1. **Testing:** Dùng Postman hoặc curl để test API
2. **Frontend:** Tích hợp với frontend application
3. **Production:** 
   - Đổi `API_TOKEN` thành biến môi trường
   - Tắt debug mode
   - Dùng production WSGI server (gunicorn)
   - Cấu hình CORS chính xác

Enjoy coding! 🎉
