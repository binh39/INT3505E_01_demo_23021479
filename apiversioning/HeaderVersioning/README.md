# HeaderVersioning Payment API

> **Header-Based API Versioning Demo - Version determined by HTTP headers**

## 🎯 Concept

**Header-based versioning** sử dụng HTTP header để xác định version thay vì đưa version vào URL. Cùng một endpoint có thể trả về format khác nhau dựa trên header được gửi kèm.

### Key Characteristics

- ✅ **Clean URLs**: Không có version trong URL path
- ✅ **Same Endpoint**: Tất cả versions dùng chung endpoint
- ✅ **Flexible**: Dễ dàng thêm version mới
- ✅ **Semantic**: Hỗ trợ semantic versioning (1.0, 2.1, etc.)

---

## 📁 Project Structure

```
HeaderVersioning/
├── app.py                      # Flask application
├── routes.py                   # Single set of routes
├── test_header_versioning.py   # Test suite
├── requirements.txt            # Dependencies
├── payments_header.db          # SQLite database (auto-generated)
│
├── core/                       # Business logic layer
│   ├── __init__.py
│   ├── database.py            # Database operations
│   └── service.py             # PaymentService
│
└── handlers/                   # Version-specific handlers
    ├── __init__.py
    ├── v1_handler.py          # V1 format handler
    └── v2_handler.py          # V2 format handler
```

---

## 🔍 How It Works

### Request Flow

```
Client Request
    │
    ├─── Header: API-Version: 1
    │    or
    └─── Header: API-Version: 2
            │
            ▼
    Same Endpoint: /api/payments
            │
            ▼
    routes.py detects header
            │
            ├─────────┬─────────┐
            ▼         ▼         ▼
       V1Handler  V2Handler  Error
            │         │
            └────┬────┘
                 ▼
          PaymentService
                 ▼
            Database
```

### Version Detection Code

```python
def get_handler():
    """Get handler based on API-Version header."""
    version_header = request.headers.get('API-Version', '1')
    version = version_header.lower().replace('v', '')
    
    handlers = {
        '1': V1Handler,
        '2': V2Handler
    }
    
    return handlers.get(version)
```

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Server

```bash
cd HeaderVersioning
python app.py
```

Server runs on **http://localhost:5001**

### 3. Run Tests

```bash
# In new terminal
python test_header_versioning.py
```

---

## 📡 API Usage

### Endpoint Structure

**Single endpoint for all versions**: `/api/payments`

Version is specified via header:
- `API-Version: 1` → Returns V1 format
- `API-Version: 2` → Returns V2 format
- No header → Defaults to V1

### V1 Examples

**GET all payments (V1):**
```bash
curl -H "API-Version: 1" http://localhost:5001/api/payments
```

**Create payment (V1):**
```bash
curl -X POST \
  -H "API-Version: 1" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100.0, "card_number": "4111-1111-1111-1111", "status": "SUCCESS"}' \
  http://localhost:5001/api/payments
```

**V1 Response Format:**
```json
{
  "status_code": 200,
  "message": "Payment created successfully",
  "data": {
    "id": 1,
    "transaction_id": "TXN-ABC123",
    "amount": 100.0,
    "card_number": "4111-1111-1111-1111",
    "status": "SUCCESS",
    "created_at": "2024-11-25 10:00:00"
  }
}
```

### V2 Examples

**GET all transactions (V2):**
```bash
curl -H "API-Version: 2" http://localhost:5001/api/payments
```

**Create transaction (V2):**
```bash
curl -X POST \
  -H "API-Version: 2" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100.0, "payment_token": "TOK-ABC123", "status": "SUCCESS"}' \
  http://localhost:5001/api/payments
```

**V2 Response Format:**
```json
{
  "code": 200,
  "message": "Transaction created successfully",
  "data": {
    "id": 1,
    "amount": 100.0,
    "payment_token": "TOK-ABC123",
    "status": "SUCCESS",
    "code": 200,
    "created_at": "2024-11-25 10:00:00"
  }
}
```

---

## 🔀 Comparison: URL vs Header Versioning

### URL Versioning (Routes/AdapterTransformer projects)

```bash
# V1
GET /api/v1/payments

# V2
GET /api/v2/transactions
```

**Pros:**
- ✅ Very visible and explicit
- ✅ Easy to test in browser
- ✅ Simple caching strategies
- ✅ Bookmarkable URLs

**Cons:**
- ❌ URL changes between versions
- ❌ Multiple endpoints to maintain
- ❌ Resource name might change (payments → transactions)

---

### Header Versioning (This project)

```bash
# V1
GET /api/payments
Header: API-Version: 1

# V2
GET /api/payments
Header: API-Version: 2
```

**Pros:**
- ✅ Clean, version-independent URLs
- ✅ Same endpoint for all versions
- ✅ No URL changes when adding versions
- ✅ Supports semantic versioning (1.0, 2.1, etc.)
- ✅ Resource name stays consistent

**Cons:**
- ❌ Less visible (hidden in headers)
- ❌ Harder to test in browser
- ❌ More complex caching
- ❌ Requires client to set headers

---

## 📊 Side-by-Side Comparison

| Feature | URL Versioning | Header Versioning |
|---------|----------------|-------------------|
| **Visibility** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Clean URLs** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Ease of Testing** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Caching** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Maintainability** | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Flexibility** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **RESTful** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 When to Use Each Strategy?

### Use URL Versioning When:
- 🎯 You want maximum visibility
- 🎯 Simple caching is important
- 🎯 Different versions have different resource structures
- 🎯 Public APIs where discoverability is key
- 🎯 Clients use browsers frequently

**Example:** GitHub API uses URL versioning
```
https://api.github.com/v3/users
```

---

### Use Header Versioning When:
- 🎯 You want clean, semantic URLs
- 🎯 Versions share same resource structure
- 🎯 You need semantic versioning support (1.0, 2.1, etc.)
- 🎯 RESTful purity is important
- 🎯 Internal APIs or SDKs

**Example:** Microsoft Graph API uses headers
```
GET https://graph.microsoft.com/users
Header: Accept: application/json; version=2.0
```

---

## 🔧 Key Implementation Details

### 1. Version Detection

```python
# routes.py
def get_handler():
    version_header = request.headers.get('API-Version', '1')
    version = version_header.lower().replace('v', '')
    
    handlers = {
        '1': V1Handler,
        '2': V2Handler
    }
    
    return handlers.get(version)
```

### 2. Single Route, Multiple Versions

```python
@payment_bp.route('', methods=['GET'])
def get_all_payments():
    handler = get_handler()  # Detects version from header
    payments = PaymentService.get_all_payments()
    transformed = handler.transform_response_list(payments)
    return jsonify(handler.format_success_response(...))
```

### 3. Default Version

```python
# If no header provided, default to V1
version_header = request.headers.get('API-Version', '1')
```

---

## 🧪 Testing

### Run Full Test Suite

```bash
python test_header_versioning.py
```

### Test Coverage

- ✅ V1 operations (with header)
- ✅ V2 operations (with header)
- ✅ Default to V1 (no header)
- ✅ Invalid version handling
- ✅ Same endpoint different formats
- ✅ Backward compatibility

### Manual Testing

**Test default behavior (no header):**
```bash
curl http://localhost:5001/api/payments
# Should return V1 format
```

**Test V1 explicitly:**
```bash
curl -H "API-Version: 1" http://localhost:5001/api/payments
```

**Test V2:**
```bash
curl -H "API-Version: 2" http://localhost:5001/api/payments
```

**Test invalid version:**
```bash
curl -H "API-Version: 99" http://localhost:5001/api/payments
# Should return 400 error
```

---

## 📚 Real-World Examples

### Companies Using Header Versioning

1. **Microsoft Graph API**
   ```
   GET https://graph.microsoft.com/v1.0/users
   Accept: application/json
   ```

2. **Stripe API**
   ```
   GET https://api.stripe.com/charges
   Stripe-Version: 2023-10-16
   ```

3. **Twilio API**
   ```
   GET https://api.twilio.com/Messages
   Accept: application/json; version=2
   ```

---

## 🎓 Learning Outcomes

This project demonstrates:

1. ✅ **Header-based versioning** implementation
2. ✅ **Version negotiation** via HTTP headers
3. ✅ **Clean URL design** for APIs
4. ✅ **Backward compatibility** strategies
5. ✅ **Default version** handling
6. ✅ **Error handling** for invalid versions

---

## 🆚 Compare with Other Projects

### Routes Project
- **Strategy**: URL versioning (`/api/v1/payments`, `/api/v2/transactions`)
- **Pattern**: Blueprint-based routing
- **Best for**: Simple, visible versioning

### AdapterTransformer Project
- **Strategy**: URL versioning with design patterns
- **Pattern**: Adapter + Transformer pattern
- **Best for**: Complex transformations, scalability

### HeaderVersioning Project (This)
- **Strategy**: Header-based versioning
- **Pattern**: Handler pattern
- **Best for**: Clean URLs, semantic versioning

---

## 💡 Pro Tips

1. **Always provide a default version** if no header is sent
2. **Document header requirements** clearly in API docs
3. **Use standard header names** (e.g., `API-Version`, `Accept`)
4. **Validate version early** in request processing
5. **Return version in response headers** for confirmation

---

## 🚀 Next Steps

Want to extend this project?

1. Add **custom Accept header** support:
   ```
   Accept: application/vnd.myapi.v2+json
   ```

2. Implement **version deprecation warnings**:
   ```json
   {
     "code": 200,
     "data": {...},
     "deprecation_warning": "API version 1 will be deprecated on 2025-12-31"
   }
   ```

3. Add **version negotiation** logic to select best available version

4. Implement **multiple versioning strategies** in same API

---

## 📝 Summary

**Header-based versioning** provides:
- ✅ Clean, semantic URLs
- ✅ Same endpoint for all versions
- ✅ Flexible version management
- ✅ RESTful design principles

**Trade-offs:**
- ❌ Less visible than URL versioning
- ❌ Requires header management
- ❌ More complex caching

**Best suited for:**
- Internal APIs
- SDK-driven integrations
- When URL stability is critical
- Semantic versioning requirements

---

## 🙋 Questions?

Check the API documentation:
```bash
curl http://localhost:5001/ | json_pp
```

Happy coding! 🎉
