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

# Kích hoạt venv
.\venv\Scripts\Activate

# Cài đặt dependencies
pip install -r requirements.txt

### 2. Khởi tạo database
python database.py

### 3. Chạy ứng dụng
python app.py

Server sẽ chạy tại: `http://localhost:5000`

# Chạy test script
python test_api.py

### Reset database
rm payments.db
python database.py
