# Social Media API - Post & Interaction Service

RESTful API cho dịch vụ Bài viết (Post) và Tương tác (Comment, Reaction) - xây dựng với Node.js, Express, TypeScript và MongoDB.

## 📋 Mục lục

- [Tính năng](#tính-năng)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Cấu hình](#cấu-hình)
- [Chạy ứng dụng](#chạy-ứng-dụng)
- [API Documentation](#api-documentation)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [API Endpoints](#api-endpoints)

## ✨ Tính năng

### Posts (Bài viết)
- ✅ Tạo, đọc, cập nhật, xóa bài viết (CRUD)
- ✅ Tìm kiếm bài viết theo nội dung, user, tags, status
- ✅ Phân trang (offset-based và cursor-based)
- ✅ Sắp xếp bài viết
- ✅ Kiểm soát quyền riêng tư (public, friends, private)

### Comments (Bình luận)
- ✅ Tạo, đọc, cập nhật, xóa comment
- ✅ Hỗ trợ reply comment (nested comments)
- ✅ Đếm số lượng reactions và replies
- ✅ Phân trang comments

### Reactions (Tương tác)
- ✅ Thêm/cập nhật reaction cho post và comment
- ✅ Xóa reaction
- ✅ 6 loại reaction: like, love, haha, wow, sad, angry
- ✅ Lọc reactions theo loại

### Tính năng chung
- ✅ JWT Authentication
- ✅ HATEOAS Links (RESTful Level 3)
- ✅ Validation với express-validator
- ✅ Error handling thống nhất
- ✅ Response format chuẩn
- ✅ API Documentation với Swagger
- ✅ Security với Helmet
- ✅ CORS configuration
- ✅ Request compression
- ✅ Logging với Morgan

## 🛠 Công nghệ sử dụng

- **Runtime**: Node.js
- **Language**: TypeScript
- **Framework**: Express.js
- **Database**: MongoDB với Mongoose ODM
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: express-validator
- **Documentation**: Swagger/OpenAPI
- **Security**: Helmet, CORS
- **Logging**: Morgan

## 📦 Yêu cầu hệ thống

- Node.js >= 18.x
- MongoDB >= 5.x
- npm hoặc yarn

## 🚀 Cài đặt

1. **Clone repository**
```bash
git clone <repository-url>
cd service_operation
```

2. **Cài đặt dependencies**
```bash
npm install
```

3. **Tạo file .env**
```bash
cp .env.example .env
```

## ⚙️ Cấu hình

Chỉnh sửa file `.env` với thông tin của bạn:

```env
# Server Configuration
NODE_ENV=development
PORT=3000
API_VERSION=v1

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/social_media_db

# JWT Configuration
JWT_SECRET=your_super_secret_jwt_key_change_this_in_production
JWT_EXPIRES_IN=7d

# CORS Configuration
CORS_ORIGIN=http://localhost:3000,http://localhost:3001
```

## 🏃 Chạy ứng dụng

### Development Mode
```bash
npm run dev
```

### Production Build
```bash
# Build TypeScript to JavaScript
npm run build

# Start production server
npm start
```

### Testing
```bash
# Run tests
npm test

# Run tests in watch mode
npm run test:watch
```

Server sẽ chạy tại: `http://localhost:3000`

## 📚 API Documentation

Sau khi khởi động server, truy cập Swagger UI tại:

```
http://localhost:3000/api-docs
```

Health check endpoint:
```
http://localhost:3000/v1/health
```

## 📁 Cấu trúc dự án

```
service_operation/
├── src/
│   ├── config/           # Cấu hình (env, database, swagger)
│   ├── controllers/      # Request handlers
│   ├── middlewares/      # Express middlewares (auth, error, validation)
│   ├── models/           # MongoDB models (Mongoose schemas)
│   ├── routes/           # API routes
│   ├── services/         # Business logic
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions (response, pagination, jwt)
│   ├── validators/       # Request validation schemas
│   ├── app.ts           # Express app configuration
│   └── server.ts        # Server entry point
├── .env.example         # Environment variables template
├── .gitignore
├── package.json
├── tsconfig.json
└── README.md
```

## 🔌 API Endpoints

### Posts

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/v1/posts` | Optional | Lấy danh sách bài viết |
| POST | `/v1/posts` | Required | Tạo bài viết mới |
| GET | `/v1/posts/:post_id` | Optional | Lấy chi tiết bài viết |
| PATCH | `/v1/posts/:post_id` | Required | Cập nhật bài viết |
| DELETE | `/v1/posts/:post_id` | Required | Xóa bài viết |

### Comments

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/v1/posts/:post_id/comments` | Optional | Lấy danh sách comments |
| POST | `/v1/posts/:post_id/comments` | Required | Tạo comment mới |
| GET | `/v1/posts/:post_id/comments/:comment_id` | Optional | Lấy chi tiết comment |
| PATCH | `/v1/posts/:post_id/comments/:comment_id` | Required | Cập nhật comment |
| DELETE | `/v1/posts/:post_id/comments/:comment_id` | Required | Xóa comment |

### Reactions

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/v1/posts/:post_id/reactions` | Optional | Lấy reactions của post |
| POST | `/v1/posts/:post_id/reactions` | Required | Thêm/cập nhật reaction |
| DELETE | `/v1/posts/:post_id/reactions` | Required | Xóa reaction |
| GET | `/v1/comments/:comment_id/reactions` | Optional | Lấy reactions của comment |
| POST | `/v1/comments/:comment_id/reactions` | Required | Thêm/cập nhật reaction |
| DELETE | `/v1/comments/:comment_id/reactions` | Required | Xóa reaction |

## 📝 Request/Response Examples

### Create Post
```bash
POST /v1/posts
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "content": "This is my first post!",
  "tags": ["intro", "hello"],
  "visibility": "public"
}
```

Response:
```json
{
  "status": "success",
  "message": "Post created successfully",
  "data": {
    "id": "65abc123...",
    "user_id": "user123",
    "content": "This is my first post!",
    "tags": ["intro", "hello"],
    "visibility": "public",
    "likes_count": 0,
    "comments_count": 0,
    "created_at": "2024-01-20T10:00:00.000Z",
    "updated_at": "2024-01-20T10:00:00.000Z"
  },
  "_links": {
    "self": { "href": "/v1/posts/65abc123...", "method": "GET" },
    "update": { "href": "/v1/posts/65abc123...", "method": "PATCH" },
    "delete": { "href": "/v1/posts/65abc123...", "method": "DELETE" },
    "reactions": { "href": "/v1/posts/65abc123.../reactions", "method": "GET" },
    "comments": { "href": "/v1/posts/65abc123.../comments", "method": "GET" }
  }
}
```

### Add Reaction
```bash
POST /v1/posts/:post_id/reactions
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "react_type": "love"
}
```

### Get Posts with Pagination
```bash
GET /v1/posts?limit=20&offset=0&sort_by=created_at&order=desc&q=hello
```

## 🔐 Authentication

API sử dụng JWT Bearer token để authentication. Thêm token vào header:

```
Authorization: Bearer <your_jwt_token>
```

Để test API, bạn có thể tạo JWT token với payload:
```json
{
  "id": "user_id_here",
  "email": "user@example.com"
}
```

## 🐛 Error Handling

API trả về error response theo format:

```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "Error description",
  "details": [
    {
      "field": "field_name",
      "message": "Field error message"
    }
  ]
}
```

Common error codes:
- `AUTH_REQUIRED` - Authentication required
- `INVALID_TOKEN` - Invalid or expired token
- `PERMISSION_DENIED` - No permission to access resource
- `RESOURCE_NOT_FOUND` - Resource not found
- `VALIDATION_ERROR` - Validation failed
- `INTERNAL_ERROR` - Internal server error

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- Your Name - [Your Email]

## 🙏 Acknowledgments

- OpenAPI 3.0 Specification
- RESTful API Best Practices
- HATEOAS Architectural Style
