# Payment API Versioning Demo

Demo API versioning cho hệ thống thanh toán đơn giản với Flask và SQLite.

## 🎯 Mục tiêu

Demo về:
- **API Versioning**: v1 và v2 chạy song song
- **Breaking Changes**: Thay đổi không tương thích ngược
- **Deprecation**: Cảnh báo các field/API đã lỗi thời
- **Migration**: Hướng dẫn chuyển từ v1 sang v2
- **RESTful Standards**: Tuân thủ chuẩn REST (nouns, HATEOAS)

## 📊 Tổng quan phiên bản

| Phiên bản | Trạng thái | Resource | Endpoint | Deprecation Date | Sunset Date |
|-----------|-----------|----------|----------|------------------|-------------|
| **v1** | ⚠️ Deprecated | `payments` | `/api/v1/payments` | 2026-01-19 | 2026-06-19 |
| **v2** | ✅ Current | `transactions` | `/api/v2/transactions` | - | - |

## 🔄 Breaking Changes (v1 → v2)

### 1. **Resource đổi tên**: `payments` → `transactions`
```
v1: /api/v1/payments
v2: /api/v2/transactions
```

### 2. **Field bị xóa**: `transaction_id`
```json
// v1: Có transaction_id riêng
{"id": 1, "transaction_id": "TXN-ABC123"}

// v2: Chỉ dùng id
{"id": 1}
```

### 3. **Field đổi tên**: `card_number` → `payment_token`
```json
// v1: Card number dạng plain text
{"card_number": "4532-1234-5678-9010"}

// v2: Payment token đã được mã hóa
{"payment_token": "TOK-ABC123DEF456GHI789"}
```

### 4. **Field đổi tên**: `status_code` → `code`
```json
// v1
{"status": "SUCCESS", "status_code": 200}

// v2
{"status": "SUCCESS", "code": 200}
```

## 🚀 Quick Start

### 1. Setup môi trường

```bash
# Tạo venv
python -m venv venv

# Kích hoạt venv (Windows)
.\venv\Scripts\Activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 2. Khởi tạo database
```bash
python database.py
```

### 3. Chạy ứng dụng
```bash
python app.py
```

Server sẽ chạy tại: `http://localhost:5000`

## 🧪 Testing

### Test nhanh (so sánh v1 vs v2)
```powershell
.\quick_test.ps1
```

### Test đầy đủ v1
```powershell
.\test_api.ps1
```

### Test đầy đủ v2
```powershell
.\test_v2_api.ps1
```

## 📚 Documentation

- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)**: Chi tiết về breaking changes và migration steps
- **[QUICKSTART.md](QUICKSTART.md)**: Hướng dẫn chạy nhanh

## 🔗 API Endpoints

### v1 API (Deprecated)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/payments` | Lấy tất cả payments |
| GET | `/api/v1/payments/{id}` | Lấy payment theo ID |
| POST | `/api/v1/payments` | Tạo payment mới |
| DELETE | `/api/v1/payments/{id}` | Xóa payment |

**Request body (POST)**:
```json
{
  "amount": 100.00,
  "card_number": "4532-1234-5678-9010",
  "status": "SUCCESS"
}
```

**Response format**:
```json
{
  "status_code": 200,
  "message": "Success message",
  "data": {
    "id": 1,
    "transaction_id": "TXN-ABC123",
    "amount": 100.00,
    "card_number": "4532-1234-5678-9010",
    "created_at": "2025-11-19 10:30:00"
  },
  "links": {
    "self": "/api/v1/payments/1",
    "collection": "/api/v1/payments"
  }
}
```

### v2 API (Current)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/transactions` | Lấy tất cả transactions |
| GET | `/api/v2/transactions/{id}` | Lấy transaction theo ID |
| POST | `/api/v2/transactions` | Tạo transaction mới |
| DELETE | `/api/v2/transactions/{id}` | Xóa transaction |
| GET | `/api/v2/migration-guide` | Hướng dẫn migration |

**Request body (POST)** - Cách mới (khuyến nghị):
```json
{
  "amount": 100.00,
  "payment_token": "TOK-ABC123DEF456GHI789",
  "status": "SUCCESS"
}
```

**Request body (POST)** - Backward compatibility (deprecated):
```json
{
  "amount": 100.00,
  "card_number": "4532-1234-5678-9010",
  "status": "SUCCESS"
}
```
⚠️ Sẽ nhận cảnh báo deprecation và tự động tạo payment_token.

**Response format**:
```json
{
  "status_code": 200,
  "message": "Success message",
  "data": {
    "id": 1,
    "amount": 100.00,
    "payment_token": "TOK-ABC123DEF456GHI789",
    "status": "SUCCESS",
    "code": 200,
    "created_at": "2025-11-19 10:30:00",
    "_deprecated": {
      "message": "Fields transaction_id, card_number, and status_code are deprecated.",
      "migration_guide": "/api/v2/migration-guide"
    }
  },
  "links": {
    "self": "/api/v2/transactions/1",
    "collection": "/api/v2/transactions"
  }
}
```

## 🗄️ Database Schema

```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT UNIQUE NOT NULL,        -- Deprecated in v2
    amount REAL NOT NULL,
    card_number TEXT NOT NULL,                  -- Deprecated in v2
    status TEXT NOT NULL,                       -- SUCCESS, PENDING, REFUND
    status_code INTEGER NOT NULL,               -- Deprecated in v2
    code INTEGER,                                -- NEW in v2
    payment_token TEXT,                          -- NEW in v2
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Note**: Các field deprecated vẫn giữ trong database để tương thích với v1 API.

## 🔐 Security Improvements (v2)

- **Tokenization**: v2 sử dụng `payment_token` thay vì plain text `card_number`
- **PCI DSS Compliance**: Giảm nguy cơ rò rỉ thông tin thẻ
- **Hash-based tokens**: Token được tạo từ SHA256 hash

## 📝 Status Values

| Status | Code (v1: status_code, v2: code) | Description |
|--------|----------------------------------|-------------|
| SUCCESS | 200 | Thanh toán thành công |
| PENDING | 102 | Đang xử lý |
| REFUND | 204 | Đã hoàn tiền |

## 🔄 Migration Timeline

| Ngày | Sự kiện | Hành động |
|------|---------|-----------|
| 2025-11-19 | v2 Release | Bắt đầu migrate sang v2 |
| 2026-01-19 | v1 Deprecated | Hoàn thành migration |
| 2026-06-19 | v1 Sunset | v1 API sẽ bị tắt |

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **API Design**: RESTful, HATEOAS
- **Versioning**: URL-based versioning

## 📖 HATEOAS Links

Mọi response đều có HATEOAS links:
```json
{
  "links": {
    "self": "/api/v2/transactions/1",     // Link đến resource hiện tại
    "collection": "/api/v2/transactions",  // Link đến collection
    "delete": "/api/v2/transactions/1"     // Link để xóa resource
  }
}
```

## 🧹 Maintenance

### Reset database
```bash
rm payments.db
python database.py
```

### Re-run migration
```bash
python database.py
```

## 📋 Examples

### Tạo payment trong v1
```bash
curl -X POST http://localhost:5000/api/v1/payments \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.00,
    "card_number": "4532-1234-5678-9010",
    "status": "SUCCESS"
  }'
```

### Tạo transaction trong v2 (cách mới)
```bash
curl -X POST http://localhost:5000/api/v2/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.00,
    "payment_token": "TOK-ABC123DEF456GHI789",
    "status": "SUCCESS"
  }'
```

### Xem migration guide
```bash
curl http://localhost:5000/api/v2/migration-guide
```

## ⚠️ Important Notes

1. **Cả v1 và v2 đều hoạt động**: Trong thời gian migration
2. **v1 sắp deprecated**: Hãy migrate sang v2 trước 2026-01-19
3. **Backward compatibility**: v2 vẫn accept `card_number` nhưng sẽ có warning
4. **Database changes**: Thêm 2 cột mới (`code`, `payment_token`) nhưng không xóa cột cũ

## 📞 Support

- Migration guide: `GET /api/v2/migration-guide`
- Full documentation: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
