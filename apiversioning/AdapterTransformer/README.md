# AdapterTransformer Payment API

> **Standalone project demonstrating the Adapter/Transformer pattern for API versioning**

## 📁 Project Structure

```
AdapterTransformer/
├── app.py                      # Flask application entry point
├── test_adapter.py             # Comprehensive test suite
├── requirements.txt            # Python dependencies
├── payments_adapter.db         # SQLite database (auto-generated)
│
├── core/                       # Core business logic layer
│   ├── __init__.py
│   ├── database.py            # Database connection & initialization
│   └── service.py             # PaymentService (version-agnostic)
│
├── routes/                     # HTTP routing layer
│   ├── __init__.py
│   └── payment_routes.py      # Unified routes for v1 & v2
│
├── adapters/                   # Version-specific formatting
│   ├── __init__.py
│   ├── v1_adapter.py          # V1 request/response formatting
│   └── v2_adapter.py          # V2 request/response formatting
│
└── transformers/               # Data transformation layer
    ├── __init__.py
    ├── base_transformer.py    # Abstract transformer interface
    ├── v1_transformer.py      # V1 data transformation
    └── v2_transformer.py      # V2 data transformation
```

---

## 🎯 Architecture Overview

### Layer Separation

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Request                           │
│              (V1 or V2 via URL path)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  ROUTES LAYER                               │
│              (routes/payment_routes.py)                     │
│  • HTTP request/response handling                          │
│  • Route registration (/api/v1/* or /api/v2/*)            │
│  • Adapter selection based on version                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 ADAPTERS LAYER                              │
│          (adapters/v1_adapter.py & v2_adapter.py)          │
│  • Version-specific response formatting                    │
│  • HATEOAS links generation                               │
│  • Deprecation warnings (V2)                              │
│  • Delegates transformation to transformers                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               TRANSFORMERS LAYER                            │
│      (transformers/v1_transformer.py & v2_transformer.py)  │
│  • Data structure transformation                           │
│  • Request → Internal format                               │
│  • Internal format → Response format                       │
│  • Token generation (V2)                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  SERVICE LAYER                              │
│                (core/service.py)                            │
│  • Version-agnostic business logic                         │
│  • Database operations (CRUD)                              │
│  • Payment processing                                      │
│  • Transaction ID generation                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 DATABASE LAYER                              │
│               (core/database.py)                            │
│  • SQLite connection management                            │
│  • Database initialization                                 │
│  • Schema migration                                        │
│  • Sample data seeding                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow Example

### V1 Request: `POST /api/v1/payments`

```python
# 1. Client sends V1 request
{
  "amount": 100.0,
  "card_number": "4111-1111-1111-1111",
  "status": "SUCCESS"
}

# 2. Routes layer receives and routes to V1Adapter
routes/payment_routes.py → get_adapter('v1') → V1Adapter

# 3. V1Adapter delegates to V1Transformer
V1Adapter.transform_request() → V1Transformer.transform_request()

# 4. Transformer converts to internal format
{
  "amount": 100.0,
  "card_number": "4111-1111-1111-1111",
  "payment_token": None,  # V1 doesn't use tokens
  "status": "SUCCESS",
  "status_code": 200,
  "code": 200
}

# 5. Service layer creates payment (version-agnostic)
PaymentService.create_payment(...) → Database INSERT

# 6. Transformer converts DB record to V1 format
V1Transformer.transform_response() → V1 format

# 7. Adapter formats final response
V1Adapter.format_success_response() → V1 response structure

# 8. Client receives V1 response
{
  "status_code": 201,
  "message": "Payment created successfully",
  "data": {
    "id": 1,
    "transaction_id": "TXN-ABC123",
    "amount": 100.0,
    "card_number": "4111-1111-1111-1111",
    "status": "SUCCESS",
    "created_at": "2024-11-19 10:00:00"
  },
  "links": {...}
}
```

### V2 Request: `POST /api/v2/transactions`

```python
# 1. Client sends V2 request
{
  "amount": 100.0,
  "payment_token": "TOK-XYZ789",
  "status": "SUCCESS"
}

# 2. Routes layer routes to V2Adapter
routes/payment_routes.py → get_adapter('v2') → V2Adapter

# 3. V2Adapter delegates to V2Transformer
V2Adapter.transform_request() → V2Transformer.transform_request()

# 4. Service creates payment
PaymentService.create_payment(...) → Database INSERT

# 5. Transformer converts to V2 format
V2Transformer.transform_response() → V2 format (no transaction_id!)

# 6. Client receives V2 response
{
  "code": 201,  # ⚠️ Different from V1 (status_code)
  "message": "Transaction created successfully",
  "data": {
    "id": 1,
    "amount": 100.0,
    "payment_token": "TOK-XYZ789",  # ⚠️ Tokenized
    "status": "SUCCESS",
    "code": 201,  # ⚠️ Code in data too
    "created_at": "2024-11-19 10:00:00"
    # ⚠️ No transaction_id!
  },
  "links": {...}
}
```

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install flask requests
```

Or create `requirements.txt`:
```txt
Flask==3.0.0
requests==2.31.0
```

Then:
```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
# Option 1: Run database script directly
cd AdapterTransformer
python core/database.py

# Option 2: Database auto-initializes when starting app
python app.py  # Will create payments_adapter.db automatically
```

### 3. Start Server

```bash
cd AdapterTransformer
python app.py
```

Server will start on `http://localhost:5000`

### 4. Run Tests

```bash
# In a new terminal (while server is running)
cd AdapterTransformer
python test_adapter.py
```

---

## 📡 API Endpoints

### Root & Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API documentation and architecture info |
| GET | `/health` | Health check |

### V1 API (Payments)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/payments` | List all payments |
| GET | `/api/v1/payments/{id}` | Get payment by ID |
| POST | `/api/v1/payments` | Create new payment |
| DELETE | `/api/v1/payments/{id}` | Delete payment |

**V1 Request Format:**
```json
{
  "amount": 100.0,
  "card_number": "4111-1111-1111-1111",
  "status": "SUCCESS"
}
```

**V1 Response Format:**
```json
{
  "status_code": 200,
  "message": "...",
  "data": {
    "id": 1,
    "transaction_id": "TXN-ABC123",
    "amount": 100.0,
    "card_number": "4111-1111-1111-1111",
    "status": "SUCCESS",
    "created_at": "..."
  },
  "links": {...}
}
```

### V2 API (Transactions)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v2/transactions` | List all transactions |
| GET | `/api/v2/transactions/{id}` | Get transaction by ID |
| POST | `/api/v2/transactions` | Create new transaction |
| DELETE | `/api/v2/transactions/{id}` | Delete transaction |

**V2 Request Format:**
```json
{
  "amount": 100.0,
  "payment_token": "TOK-ABC123DEF456",
  "status": "SUCCESS"
}
```

**V2 Response Format:**
```json
{
  "code": 200,
  "message": "...",
  "data": {
    "id": 1,
    "amount": 100.0,
    "payment_token": "TOK-ABC123DEF456",
    "status": "SUCCESS",
    "code": 200,
    "created_at": "..."
  },
  "links": {...}
}
```

---

## 🔍 Key Differences: V1 vs V2

| Feature | V1 | V2 |
|---------|----|----|
| **Resource Name** | `payments` | `transactions` |
| **Response Wrapper** | `status_code` | `code` |
| **Transaction ID** | ✅ Has `transaction_id` | ❌ Removed |
| **Card Number** | ✅ Plain text `card_number` | ❌ Uses `payment_token` |
| **Backward Compat** | N/A | ✅ Accepts `card_number` (deprecated) |
| **Code Field** | Only in response wrapper | In wrapper AND data object |

---

## 🎨 Design Pattern Benefits

### 1. **Separation of Concerns**
- **Routes**: HTTP handling only
- **Adapters**: Version-specific formatting
- **Transformers**: Data transformation logic
- **Service**: Business logic (version-agnostic)
- **Database**: Data persistence

### 2. **Easy to Extend**
Adding V3 is simple:
```python
# 1. Create transformers/v3_transformer.py
# 2. Create adapters/v3_adapter.py
# 3. Add routes in routes/payment_routes.py
# 4. Update get_adapter() factory

# NO changes to service or database layers!
```

### 3. **Single Source of Truth**
- Business logic lives in ONE place (`PaymentService`)
- No code duplication across versions
- Fix bug once, all versions benefit

### 4. **Testability**
- Test each layer independently
- Mock transformers to test adapters
- Mock service to test routes

---

## 🧪 Testing

### Run Full Test Suite
```bash
python test_adapter.py
```

### Test Coverage
- ✅ Root & Health endpoints
- ✅ V1 CRUD operations
- ✅ V2 CRUD operations
- ✅ V2 backward compatibility (card_number → token)
- ✅ Error handling (both versions)
- ✅ Deprecation warnings

### Manual Testing with cURL

**V1 - Create Payment:**
```bash
curl -X POST http://localhost:5000/api/v1/payments \
  -H "Content-Type: application/json" \
  -d '{"amount": 100.0, "card_number": "4111-1111-1111-1111", "status": "SUCCESS"}'
```

**V2 - Create Transaction:**
```bash
curl -X POST http://localhost:5000/api/v2/transactions \
  -H "Content-Type: application/json" \
  -d '{"amount": 100.0, "payment_token": "TOK-ABC123", "status": "SUCCESS"}'
```

**V2 - Backward Compatible (with card_number):**
```bash
curl -X POST http://localhost:5000/api/v2/transactions \
  -H "Content-Type: application/json" \
  -d '{"amount": 100.0, "card_number": "4111-1111-1111-1111", "status": "SUCCESS"}'
# Returns deprecation_warning in response
```

---

## 🗄️ Database

### Schema
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT,           -- For V1 compatibility
    amount REAL NOT NULL,
    card_number TEXT,              -- For V1 and V2 backward compat
    payment_token TEXT,            -- For V2
    status TEXT NOT NULL,
    status_code INTEGER,           -- For V1
    code INTEGER,                  -- For V2
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Reset Database
```bash
python core/database.py --reset
```

---

## 📚 Further Reading

- [Adapter Pattern](https://refactoring.guru/design-patterns/adapter)
- [Transformer Pattern](https://www.martinfowler.com/eaaCatalog/dataTransferObject.html)
- [API Versioning Best Practices](https://www.troyhunt.com/your-api-versioning-is-wrong/)

---

## 🎓 Educational Value

This project demonstrates:
1. ✅ **Clean Architecture** - Clear layer separation
2. ✅ **SOLID Principles** - Single Responsibility, Open/Closed
3. ✅ **Design Patterns** - Adapter, Factory, Strategy
4. ✅ **API Versioning** - Real-world versioning challenges
5. ✅ **Backward Compatibility** - Deprecation strategies
6. ✅ **RESTful Design** - HATEOAS, resource naming

Perfect for:
- 📖 Learning API versioning strategies
- 🎯 Understanding design patterns in practice
- 🏗️ Building maintainable REST APIs
- 📝 Academic projects and demos

---

## 📝 License

This is a demo project for educational purposes.

---

## 🙋 Questions?

Check the detailed architecture explanation in the root endpoint:
```bash
curl http://localhost:5000/ | json_pp
```

Or view the code - it's heavily commented! 🎉
