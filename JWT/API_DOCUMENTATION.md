# API Documentation - Library Management System

## Response Format (HATEOAS)

Tất cả API responses đều tuân theo format chuẩn:

```json
{
  "status": "success" | "error",
  "message": "Mô tả kết quả",
  "data": {...},           // Optional
  "links": {               // HATEOAS links
    "self": {"href": "/api/...", "method": "GET"},
    "...": {...}
  },
  "meta": {                // Metadata
    "timestamp": "2025-10-29T...",
    "..."
  }
}
```

## Authentication

### 1. Login

**POST** `/api/sessions`

Request:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Response (200):

```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "token": "eyJhbGciOiJIUzI1NiIs..."
  },
  "links": {
    "self": { "href": "/api/sessions", "method": "POST" },
    "verify": { "href": "/api/sessions/me", "method": "GET" },
    "logout": { "href": "/api/sessions/me", "method": "DELETE" },
    "books": { "href": "/api/books", "method": "GET" },
    "statistics": { "href": "/api/statistics", "method": "GET" }
  },
  "meta": {
    "token_expires_in": 3600,
    "timestamp": "2025-10-29T10:30:00Z"
  }
}
```

### 2. Verify Token

**GET** `/api/sessions/me`

Headers: `Authorization: Bearer {token}`

Response (200):

```json
{
  "status": "success",
  "message": "Token is valid",
  "data": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  },
  "links": {
    "self": { "href": "/api/sessions/me", "method": "GET" },
    "logout": { "href": "/api/sessions/me", "method": "DELETE" },
    "books": { "href": "/api/books", "method": "GET" }
  },
  "meta": {
    "token_expires_at": "2025-10-29T11:30:00Z",
    "timestamp": "2025-10-29T10:35:00Z"
  }
}
```

## Admin APIs

### 3. Get All Books (with Pagination)

**GET** `/api/books?page=1&per_page=20`

Headers: `Authorization: Bearer {admin_token}`

Response (200):

```json
{
  "status": "success",
  "message": "Retrieved all library books successfully",
  "data": [
    {
      "id": 1,
      "book_key": "OL123456W",
      "title": "Harry Potter",
      "author": "J.K. Rowling",
      "cover_url": "https://...",
      "quantity": 5,
      "available": 3,
      "borrowed": 2,
      "links": {
        "self": { "href": "/api/books/1", "method": "GET" },
        "update": { "href": "/api/books/1", "method": "PUT" },
        "delete": { "href": "/api/books/1", "method": "DELETE" },
        "collection": { "href": "/api/books", "method": "GET" }
      }
    }
  ],
  "links": {
    "self": { "href": "/api/books?page=1&per_page=20", "method": "GET" },
    "create": { "href": "/api/books", "method": "POST" },
    "next": { "href": "/api/books?page=2&per_page=20", "method": "GET" }
  },
  "meta": {
    "total_count": 50,
    "page": 1,
    "per_page": 20,
    "total_pages": 3,
    "timestamp": "2025-10-29T10:40:00Z"
  }
}
```

### 4. Get Book Detail

**GET** `/api/books/{book_id}`

Headers: `Authorization: Bearer {token}`

Response (200):

```json
{
  "status": "success",
  "message": "Book retrieved successfully",
  "data": {
    "id": 1,
    "book_key": "OL123456W",
    "title": "Harry Potter",
    "author": "J.K. Rowling",
    "cover_url": "https://...",
    "quantity": 5,
    "available": 3,
    "borrowed": 2
  },
  "links": {
    "self": { "href": "/api/books/1", "method": "GET" },
    "update": { "href": "/api/books/1", "method": "PUT" },
    "delete": { "href": "/api/books/1", "method": "DELETE" },
    "collection": { "href": "/api/books", "method": "GET" }
  },
  "meta": {
    "timestamp": "2025-10-29T10:45:00Z"
  }
}
```

### 5. Create Book

**POST** `/api/books`

Headers: `Authorization: Bearer {admin_token}`

Request:

```json
{
  "book_key": "OL789012W",
  "title": "New Book",
  "author": "Author Name",
  "cover_url": "https://...",
  "quantity": 3
}
```

Response (201):

```json
{
  "status": "success",
  "message": "Book created successfully",
  "data": {
    "id": 5,
    "book_key": "OL789012W",
    "title": "New Book",
    "author": "Author Name",
    "cover_url": "https://...",
    "quantity": 3,
    "available": 3,
    "borrowed": 0
  },
  "links": {
    "self": { "href": "/api/books/5", "method": "GET" },
    "update": { "href": "/api/books/5", "method": "PUT" },
    "delete": { "href": "/api/books/5", "method": "DELETE" },
    "collection": { "href": "/api/books", "method": "GET" }
  },
  "meta": {
    "created_at": "2025-10-29T10:50:00Z",
    "created_by": "admin"
  }
}
```

### 6. Update Book

**PUT** `/api/books/{book_id}`

Headers: `Authorization: Bearer {admin_token}`

Request:

```json
{
  "title": "Updated Title",
  "author": "Updated Author",
  "quantity": 10
}
```

Response (200):

```json
{
  "status": "success",
  "message": "Book updated successfully",
  "data": {
    "id": 1,
    "book_key": "OL123456W",
    "title": "Updated Title",
    "author": "Updated Author",
    "cover_url": "https://...",
    "quantity": 10,
    "available": 8,
    "borrowed": 2
  },
  "links": {
    "self": { "href": "/api/books/1", "method": "GET" },
    "update": { "href": "/api/books/1", "method": "PUT" },
    "delete": { "href": "/api/books/1", "method": "DELETE" },
    "collection": { "href": "/api/books", "method": "GET" }
  },
  "meta": {
    "updated_at": "2025-10-29T10:55:00Z",
    "updated_by": "admin"
  }
}
```

### 7. Delete Book

**DELETE** `/api/books/{book_id}`

Headers: `Authorization: Bearer {admin_token}`

Response (200):

```json
{
  "status": "success",
  "message": "Book deleted successfully",
  "data": {
    "id": 5,
    "book_key": "OL789012W",
    "title": "New Book",
    "author": "Author Name"
  },
  "links": {
    "all_books": { "href": "/api/books", "method": "GET" },
    "create_new": { "href": "/api/books", "method": "POST" }
  },
  "meta": {
    "deleted_at": "2025-10-29T11:00:00Z",
    "deleted_by": "admin"
  }
}
```

Error (409 - Book is borrowed):

```json
{
  "status": "error",
  "message": "Cannot delete book. 2 copies are currently borrowed",
  "data": {
    "book_id": 1,
    "title": "Harry Potter",
    "borrowed_count": 2
  },
  "links": {
    "self": { "href": "/api/books/1", "method": "GET" }
  },
  "status_code": 409
}
```

### 8. Get Statistics

**GET** `/api/statistics`

Headers: `Authorization: Bearer {admin_token}`

Response (200):

```json
{
  "status": "success",
  "message": "Statistics retrieved successfully",
  "data": {
    "library": {
      "total_unique_books": 10,
      "total_copies": 50,
      "total_available": 35,
      "total_borrowed": 15
    },
    "borrowing": {
      "total_borrowed_transactions": 25
    },
    "users": {
      "total_users": 5,
      "total_admins": 2
    },
    "top_borrowed_books": [
      {
        "id": 1,
        "title": "Harry Potter",
        "author": "J.K. Rowling",
        "times_borrowed": 10
      }
    ]
  },
  "links": {
    "self": { "href": "/api/statistics", "method": "GET" },
    "books": { "href": "/api/books", "method": "GET" }
  },
  "meta": {
    "timestamp": "2025-10-29T11:05:00Z",
    "requested_by": "admin"
  }
}
```

## User APIs

### 9. Get Borrowed Books

**GET** `/api/users/{user_id}/borrowed-books`

Headers: `Authorization: Bearer {user_token}`

Response (200):

```json
{
  "status": "success",
  "message": "Retrieved borrowed books successfully",
  "data": [
    {
      "id": 1,
      "book_id": 1,
      "book_key": "OL123456W",
      "title": "Harry Potter",
      "author": "J.K. Rowling",
      "cover_url": "https://...",
      "borrowed_date": "2025-10-28T15:30:00",
      "links": {
        "self": { "href": "/api/users/2/borrowed-books/1", "method": "GET" },
        "return": {
          "href": "/api/users/2/borrowed-books/1",
          "method": "DELETE"
        },
        "collection": { "href": "/api/users/2/borrowed-books", "method": "GET" }
      }
    }
  ],
  "links": {
    "self": { "href": "/api/users/2/borrowed-books", "method": "GET" },
    "available_books": { "href": "/api/books", "method": "GET" }
  },
  "meta": {
    "total_borrowed": 3,
    "user_id": 2,
    "timestamp": "2025-10-29T11:10:00Z"
  }
}
```

### 10. Borrow Book

**POST** `/api/users/{user_id}/borrowed-books`

Headers: `Authorization: Bearer {user_token}`

Request:

```json
{
  "book_id": 1
}
```

Response (201):

```json
{
  "status": "success",
  "message": "Book borrowed successfully",
  "data": {
    "id": 10,
    "book_id": 1,
    "book_key": "OL123456W",
    "title": "Harry Potter",
    "author": "J.K. Rowling",
    "cover_url": "https://...",
    "borrowed_date": "2025-10-29T11:15:00Z"
  },
  "links": {
    "self": { "href": "/api/users/2/borrowed-books/1", "method": "GET" },
    "return": { "href": "/api/users/2/borrowed-books/1", "method": "DELETE" },
    "collection": { "href": "/api/users/2/borrowed-books", "method": "GET" }
  },
  "meta": {
    "borrowed_at": "2025-10-29T11:15:00Z",
    "borrowed_by": "user"
  }
}
```

Error (409 - Already borrowed):

```json
{
  "status": "error",
  "message": "You have already borrowed this book",
  "links": {
    "borrowed_books": {
      "href": "/api/users/2/borrowed-books",
      "method": "GET"
    },
    "return_book": {
      "href": "/api/users/2/borrowed-books/1",
      "method": "DELETE"
    }
  },
  "status_code": 409
}
```

### 11. Return Book

**DELETE** `/api/users/{user_id}/borrowed-books/{book_id}`

Headers: `Authorization: Bearer {user_token}`

Response (200):

```json
{
  "status": "success",
  "message": "Book returned successfully",
  "data": {
    "id": 10,
    "book_id": 1,
    "book_key": "OL123456W",
    "title": "Harry Potter",
    "author": "J.K. Rowling",
    "borrowed_date": "2025-10-28T15:30:00"
  },
  "links": {
    "borrowed_books": {
      "href": "/api/users/2/borrowed-books",
      "method": "GET"
    },
    "available_books": { "href": "/api/books", "method": "GET" },
    "borrow_again": { "href": "/api/users/2/borrowed-books", "method": "POST" }
  },
  "meta": {
    "returned_at": "2025-10-29T11:20:00Z",
    "returned_by": "user"
  }
}
```

## Error Responses

### 400 Bad Request

```json
{
  "status": "error",
  "message": "book_key and title are required",
  "meta": {
    "required_fields": ["book_key", "title"]
  }
}
```

### 401 Unauthorized

```json
{
  "status": "error",
  "message": "Token is missing"
}
```

### 403 Forbidden

```json
{
  "status": "error",
  "message": "Admin access required"
}
```

### 404 Not Found

```json
{
  "status": "error",
  "message": "Book with id 999 not found",
  "links": {
    "all_books": { "href": "/api/books", "method": "GET" }
  }
}
```

### 409 Conflict

```json
{
  "status": "error",
  "message": "Book with book_key 'OL123' already exists",
  "links": {
    "existing_book": { "href": "/api/books/5", "method": "GET" }
  }
}
```

## Testing với PowerShell

### Login

```powershell
$body = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/api/sessions" -Method POST -Body $body -ContentType "application/json"
$token = $response.data.token
```

### Get Books

```powershell
$headers = @{
    "Authorization" = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:5000/api/books" -Headers $headers | ConvertTo-Json -Depth 10
```

### Create Book

```powershell
$bookData = @{
    book_key = "TEST001"
    title = "Test Book"
    author = "Test Author"
    quantity = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/books" -Method POST -Headers $headers -Body $bookData -ContentType "application/json" | ConvertTo-Json -Depth 10
```

### Borrow Book (User)

```powershell
# Login as user first
$userBody = @{
    username = "user"
    password = "user123"
} | ConvertTo-Json

$userResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/sessions" -Method POST -Body $userBody -ContentType "application/json"
$userToken = $userResponse.data.token
$userId = $userResponse.data.id

$userHeaders = @{
    "Authorization" = "Bearer $userToken"
}

$borrowData = @{
    book_id = 1
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/users/$userId/borrowed-books" -Method POST -Headers $userHeaders -Body $borrowData -ContentType "application/json" | ConvertTo-Json -Depth 10
```

## HATEOAS Benefits

1. **Self-Documenting**: Clients discover available actions through links
2. **Decoupling**: URLs can change without breaking clients
3. **State Transitions**: Links guide users through application workflow
4. **Discoverability**: New features are automatically exposed through links

## Best Practices

1. Always include `links.self` for current resource
2. Include action links based on current state (e.g., only show "delete" if resource can be deleted)
3. Use appropriate HTTP methods (GET, POST, PUT, DELETE)
4. Return proper HTTP status codes
5. Include pagination meta for collections
6. Provide timestamps in ISO 8601 format
7. Use descriptive messages for errors
