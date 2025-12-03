# Query Parameter API Versioning

## 📖 Overview

Demonstrates **API versioning using Query Parameters** (`?version=1` or `?version=2`). This approach uses query strings to specify the API version while keeping the URL path clean.

## 🎯 Key Features

- ✅ **Simple versioning** via query parameter
- ✅ **Same URL path** for all versions
- ✅ **Easy to test** in browser
- ✅ **Default version** (v1) if no parameter provided
- ✅ **HATEOAS links** in all responses

## 🏗️ Architecture

```
Request: GET /api/payments?version=2
                            ↓
            Query Parameter Detector
                            ↓
                    version = 2?
                    ↙        ↘
              Yes (V2)      No (V1)
                ↓              ↓
         v2/routes.py    v1/routes.py
                ↓              ↓
           V2 Response    V1 Response
```

## 📁 Project Structure

```
QueryVersioning/
├── app.py              # Flask app with query parameter routing
├── database.py         # SQLite database (payments_query.db)
├── requirements.txt
├── v1/
│   └── routes.py      # V1 endpoints
└── v2/
    └── routes.py      # V2 endpoints
```

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python database.py
```

### 3. Start Server
```bash
python app.py
```

Server runs on: **http://localhost:5003**

## 📡 API Endpoints

### Same URL, Different Query Parameter

| Method | Endpoint | V1 | V2 |
|--------|----------|----|----|
| GET | `/api/payments` | `?version=1` | `?version=2` |
| GET | `/api/payments/{id}` | `?version=1` | `?version=2` |
| POST | `/api/payments` | `?version=1` | `?version=2` |
| DELETE | `/api/payments/{id}` | `?version=1` | `?version=2` |

## 🎮 Usage Examples

### V1 Examples

```bash
# GET all payments (V1)
curl "http://localhost:5003/api/payments?version=1"

# GET single payment (V1)
curl "http://localhost:5003/api/payments/1?version=1"

# CREATE payment (V1)
curl -X POST "http://localhost:5003/api/payments?version=1" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.0,
    "card_number": "4111-1111-1111-1111",
    "status": "SUCCESS"
  }'

# DELETE payment (V1)
curl -X DELETE "http://localhost:5003/api/payments/1?version=1"
```

### V2 Examples

```bash
# GET all transactions (V2)
curl "http://localhost:5003/api/payments?version=2"

# GET single transaction (V2)
curl "http://localhost:5003/api/payments/1?version=2"

# CREATE transaction (V2)
curl -X POST "http://localhost:5003/api/payments?version=2" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 200.0,
    "card_number": "5555-5555-5555-4444",
    "status": "SUCCESS"
  }'

# DELETE transaction (V2)
curl -X DELETE "http://localhost:5003/api/payments/1?version=2"
```

### Browser Testing

Dễ dàng test trực tiếp trong browser:
```
http://localhost:5003/api/payments?version=1
http://localhost:5003/api/payments?version=2
```

## 📊 Response Formats

### V1 Response
```json
{
  "status_code": 200,
  "message": "Payments retrieved successfully",
  "data": {
    "id": 1,
    "transaction_id": "TXN-001",
    "amount": 100.50,
    "card_number": "4532-1111-2222-3333",
    "status": "SUCCESS",
    "created_at": "2025-11-27 10:00:00"
  },
  "_links": {
    "self": "/api/payments/1",
    "collection": "/api/payments",
    "delete": "/api/payments/1"
  }
}
```

### V2 Response
```json
{
  "code": 200,
  "message": "Transactions retrieved successfully",
  "data": {
    "id": 1,
    "amount": 100.50,
    "payment_token": "TOK-ABC123...",
    "status": "SUCCESS",
    "code": 200,
    "created_at": "2025-11-27 10:00:00"
  },
  "_links": {
    "self": "/api/payments/1",
    "collection": "/api/payments",
    "delete": "/api/payments/1"
  }
}
```

## ⚖️ Pros & Cons

### ✅ Advantages
- **Easy to test in browser** - just add `?version=2` to URL
- **No header required** - simpler for quick testing
- **URL path stays clean** - no version in path
- **Default version support** - fallback to v1 if no parameter
- **Simple to understand** - obvious in URL bar

### ❌ Disadvantages
- **Pollutes URL** - query parameters can make URLs messy
- **Caching complexity** - CDNs may cache without considering query params
- **Not RESTful purist** - query parameters should be for filtering, not versioning
- **Easy to forget** - developers might forget to add version parameter
- **URL length** - longer URLs with parameters

## 🔗 Comparison with Other Strategies

| Strategy | Example | Pros | Cons |
|----------|---------|------|------|
| **URL Versioning** | `/api/v1/payments` | Clear, visible | URL changes |
| **Header Versioning** | `API-Version: v1` | Clean URLs | Hidden, harder to test |
| **Query Parameter** | `?version=1` | Easy to test | URL pollution |
| **Feature Toggle** | Server-side flags | Runtime control | Complex setup |

## 💡 Best Practices

1. **Always provide default version** - don't break existing clients
2. **Document clearly** - make version parameter obvious
3. **Validate version values** - handle invalid versions gracefully
4. **Consider caching** - configure CDN to respect version parameter
5. **Keep it simple** - use `version=1` not `v=1` or `api_version=1`

## 🎯 When to Use Query Parameter Versioning

**Good for:**
- Internal APIs
- Quick prototyping
- Testing different versions easily
- When browser testing is important

**Avoid for:**
- Public-facing APIs (use URL or Header versioning)
- Highly cached endpoints
- RESTful purist projects

## 📝 Database

- **Type:** SQLite
- **File:** `payments_query.db`
- **Independent database** for QueryVersioning project

---

**Port:** 5003  
**Default Version:** v1  
**Query Parameter:** `version`
