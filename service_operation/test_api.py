"""
Test script for Library API
Tests all endpoints and displays logs
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
API_TOKEN = "demo123"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def print_separator(title=""):
    """Print a separator line"""
    print("\n" + "=" * 70)
    if title:
        print(f" {title}")
        print("=" * 70)

def print_response(response):
    """Print response details"""
    print(f"Status Code: {response.status_code}")
    print(f"Trace ID: {response.headers.get('X-Trace-ID', 'N/A')}")
    print(f"Response Time: {response.headers.get('X-Response-Time', 'N/A')}")
    
    try:
        print(f"Response Body:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(f"Response Body: {response.text}")

def test_root():
    """Test root endpoint"""
    print_separator("TEST 1: Root Endpoint - GET /")
    
    response = requests.get(f"{BASE_URL}/")
    print_response(response)
    time.sleep(1)

def test_get_empty_books():
    """Test getting books when list is empty"""
    print_separator("TEST 2: Get Empty Books List - GET /api/books")
    
    response = requests.get(f"{BASE_URL}/api/books", headers=HEADERS)
    print_response(response)
    time.sleep(1)

def test_borrow_book():
    """Test borrowing a new book"""
    print_separator("TEST 3: Borrow New Book - POST /api/books")
    
    book_data = {
        "book_key": "B001",
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "cover_url": "http://example.com/clean-code.jpg"
    }
    
    print(f"Request Body:")
    print(json.dumps(book_data, indent=2, ensure_ascii=False))
    
    response = requests.post(f"{BASE_URL}/api/books", headers=HEADERS, json=book_data)
    print_response(response)
    time.sleep(1)

def test_borrow_duplicate():
    """Test borrowing the same book again"""
    print_separator("TEST 4: Borrow Duplicate Book - POST /api/books")
    
    book_data = {
        "book_key": "B001",
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "cover_url": "http://example.com/clean-code.jpg"
    }
    
    response = requests.post(f"{BASE_URL}/api/books", headers=HEADERS, json=book_data)
    print_response(response)
    time.sleep(1)

def test_borrow_multiple_books():
    """Test borrowing multiple books"""
    print_separator("TEST 5: Borrow Multiple Books - POST /api/books")
    
    books = [
        {
            "book_key": "B002",
            "title": "Design Patterns",
            "author": "Gang of Four",
            "cover_url": "http://example.com/design-patterns.jpg"
        },
        {
            "book_key": "B003",
            "title": "Refactoring",
            "author": "Martin Fowler",
            "cover_url": "http://example.com/refactoring.jpg"
        },
        {
            "book_key": "B004",
            "title": "The Pragmatic Programmer",
            "author": "Hunt & Thomas",
            "cover_url": "http://example.com/pragmatic.jpg"
        }
    ]
    
    for book in books:
        print(f"\nBorrowing: {book['title']}")
        response = requests.post(f"{BASE_URL}/api/books", headers=HEADERS, json=book)
        print(f"Status: {response.status_code} - Trace ID: {response.headers.get('X-Trace-ID', 'N/A')}")
        time.sleep(0.5)

def test_get_all_books():
    """Test getting all borrowed books"""
    print_separator("TEST 6: Get All Books - GET /api/books")
    
    response = requests.get(f"{BASE_URL}/api/books", headers=HEADERS)
    print_response(response)
    time.sleep(1)

def test_get_single_book():
    """Test getting a single book"""
    print_separator("TEST 7: Get Single Book - GET /api/books/B001")
    
    response = requests.get(f"{BASE_URL}/api/books/B001", headers=HEADERS)
    print_response(response)
    time.sleep(1)

def test_get_nonexistent_book():
    """Test getting a book that doesn't exist"""
    print_separator("TEST 8: Get Non-existent Book - GET /api/books/B999")
    
    response = requests.get(f"{BASE_URL}/api/books/B999", headers=HEADERS)
    print_response(response)
    time.sleep(1)

def test_cache_with_etag():
    """Test caching with ETag"""
    print_separator("TEST 9: Cache Test with ETag - GET /api/books")
    
    # First request
    print("First Request (should return 200):")
    response1 = requests.get(f"{BASE_URL}/api/books", headers=HEADERS)
    etag = response1.headers.get('ETag')
    print(f"Status: {response1.status_code}, ETag: {etag}")
    time.sleep(0.5)
    
    # Second request with ETag
    print("\nSecond Request with If-None-Match (should return 304):")
    headers_with_etag = HEADERS.copy()
    headers_with_etag['If-None-Match'] = etag
    response2 = requests.get(f"{BASE_URL}/api/books", headers=headers_with_etag)
    print(f"Status: {response2.status_code}")
    print(f"Trace ID: {response2.headers.get('X-Trace-ID', 'N/A')}")
    time.sleep(1)

def test_return_book():
    """Test returning a book"""
    print_separator("TEST 10: Return Book - DELETE /api/books/B002")
    
    response = requests.delete(f"{BASE_URL}/api/books/B002", headers=HEADERS)
    print_response(response)
    time.sleep(1)

def test_return_nonexistent_book():
    """Test returning a book that doesn't exist"""
    print_separator("TEST 11: Return Non-existent Book - DELETE /api/books/B999")
    
    response = requests.delete(f"{BASE_URL}/api/books/B999", headers=HEADERS)
    print_response(response)
    time.sleep(1)

def test_missing_book_key():
    """Test borrowing without book_key"""
    print_separator("TEST 12: Borrow Without book_key - POST /api/books")
    
    book_data = {
        "title": "Missing Key Book",
        "author": "Unknown"
    }
    
    response = requests.post(f"{BASE_URL}/api/books", headers=HEADERS, json=book_data)
    print_response(response)
    time.sleep(1)

def test_unauthorized_access():
    """Test accessing API without token"""
    print_separator("TEST 13: Unauthorized Access - GET /api/books")
    
    response = requests.get(f"{BASE_URL}/api/books")
    print_response(response)
    time.sleep(1)

def test_invalid_endpoint():
    """Test accessing non-existent endpoint"""
    print_separator("TEST 14: Invalid Endpoint - GET /api/invalid")
    
    response = requests.get(f"{BASE_URL}/api/invalid", headers=HEADERS)
    print_response(response)
    time.sleep(1)

def test_final_state():
    """Test final state of books"""
    print_separator("TEST 15: Final State - GET /api/books")
    
    response = requests.get(f"{BASE_URL}/api/books", headers=HEADERS)
    print_response(response)

def run_all_tests():
    """Run all test cases"""
    print("\n" + "=" * 70)
    print(" LIBRARY API TEST SUITE")
    print(" Testing all endpoints and viewing logs")
    print("=" * 70)
    print(f" Base URL: {BASE_URL}")
    print(f" Token: {API_TOKEN}")
    print("=" * 70)
    
    try:
        # Test sequence
        test_root()
        test_get_empty_books()
        test_borrow_book()
        test_borrow_duplicate()
        test_borrow_multiple_books()
        test_get_all_books()
        test_get_single_book()
        test_get_nonexistent_book()
        test_cache_with_etag()
        test_return_book()
        test_return_nonexistent_book()
        test_missing_book_key()
        test_unauthorized_access()
        test_invalid_endpoint()
        test_final_state()
        
        print_separator("ALL TESTS COMPLETED")
        print("\nCheck the server logs (console and api.log file) to see the trace logs!")
        print("\n" + "=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to the API server!")
        print("Make sure the server is running: python app.py")
    except Exception as e:
        print(f"\nERROR: {str(e)}")

if __name__ == "__main__":
    run_all_tests()
