"""
Test script for AdapterTransformer Payment API
Tests both V1 and V2 endpoints using the unified adapter pattern.
"""
import requests
import json
from typing import Dict, Any


BASE_URL = 'http://localhost:5000'


def print_test_header(test_name: str):
    """Print formatted test header."""
    print("\n" + "=" * 80)
    print(f"🧪 TEST: {test_name}")
    print("=" * 80)


def print_response(response: requests.Response, label: str = "Response"):
    """Print formatted response."""
    print(f"\n{label}:")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Body: {response.text}")


def test_root_endpoint():
    """Test root endpoint to see API documentation."""
    print_test_header("Root Endpoint - API Documentation")
    response = requests.get(f"{BASE_URL}/")
    print_response(response)
    assert response.status_code == 200, "Root endpoint should return 200"


def test_health_check():
    """Test health check endpoint."""
    print_test_header("Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    assert response.status_code == 200, "Health check should return 200"


# ============================================================================
# V1 API Tests
# ============================================================================

def test_v1_get_all_payments():
    """Test V1: GET all payments."""
    print_test_header("V1 - GET All Payments")
    response = requests.get(f"{BASE_URL}/api/v1/payments")
    print_response(response)
    assert response.status_code == 200, "Should return 200"
    data = response.json()
    assert 'status_code' in data, "V1 should have status_code"
    assert 'data' in data, "Should have data field"
    assert isinstance(data['data'], list), "Data should be a list"


def test_v1_create_payment():
    """Test V1: POST create payment."""
    print_test_header("V1 - Create Payment")
    
    payload = {
        "amount": 299.99,
        "card_number": "4532-1234-5678-9010",
        "status": "SUCCESS"
    }
    
    print(f"\nRequest Payload: {json.dumps(payload, indent=2)}")
    response = requests.post(f"{BASE_URL}/api/v1/payments", json=payload)
    print_response(response, "Create Payment Response")
    
    assert response.status_code == 201, "Should return 201 Created"
    data = response.json()
    assert 'status_code' in data, "V1 should have status_code"
    assert data['status_code'] == 201, "Status code should be 201"
    
    # Check V1 specific fields
    payment = data['data']
    assert 'transaction_id' in payment, "V1 should have transaction_id"
    assert 'card_number' in payment, "V1 should have card_number"
    assert payment['card_number'] == payload['card_number'], "Card number should match"
    
    return payment['id']


def test_v1_get_payment_by_id(payment_id: int):
    """Test V1: GET payment by ID."""
    print_test_header(f"V1 - GET Payment by ID: {payment_id}")
    response = requests.get(f"{BASE_URL}/api/v1/payments/{payment_id}")
    print_response(response)
    
    assert response.status_code == 200, "Should return 200"
    data = response.json()
    assert 'status_code' in data, "V1 should have status_code"
    assert data['data']['id'] == payment_id, "Should return correct payment"


def test_v1_delete_payment(payment_id: int):
    """Test V1: DELETE payment."""
    print_test_header(f"V1 - DELETE Payment ID: {payment_id}")
    response = requests.delete(f"{BASE_URL}/api/v1/payments/{payment_id}")
    print_response(response)
    
    assert response.status_code == 200, "Should return 200"
    data = response.json()
    assert 'status_code' in data, "V1 should have status_code"


# ============================================================================
# V2 API Tests
# ============================================================================

def test_v2_get_all_transactions():
    """Test V2: GET all transactions."""
    print_test_header("V2 - GET All Transactions")
    response = requests.get(f"{BASE_URL}/api/v2/transactions")
    print_response(response)
    
    assert response.status_code == 200, "Should return 200"
    data = response.json()
    assert 'code' in data, "V2 should have code (not status_code)"
    assert 'data' in data, "Should have data field"
    assert isinstance(data['data'], list), "Data should be a list"


def test_v2_create_transaction_with_token():
    """Test V2: POST create transaction with payment_token."""
    print_test_header("V2 - Create Transaction (with payment_token)")
    
    payload = {
        "amount": 499.99,
        "payment_token": "TOK-ABC123DEF456",
        "status": "SUCCESS"
    }
    
    print(f"\nRequest Payload: {json.dumps(payload, indent=2)}")
    response = requests.post(f"{BASE_URL}/api/v2/transactions", json=payload)
    print_response(response, "Create Transaction Response")
    
    assert response.status_code == 201, "Should return 201 Created"
    data = response.json()
    assert 'code' in data, "V2 should have code"
    assert data['code'] == 201, "Code should be 201"
    
    # Check V2 specific fields
    transaction = data['data']
    assert 'transaction_id' not in transaction, "V2 should NOT have transaction_id"
    assert 'payment_token' in transaction, "V2 should have payment_token"
    assert 'code' in transaction, "V2 transaction should have code field"
    
    return transaction['id']


def test_v2_create_transaction_with_card_number():
    """Test V2: POST create transaction with card_number (backward compatibility)."""
    print_test_header("V2 - Create Transaction (with card_number - deprecated)")
    
    payload = {
        "amount": 199.99,
        "card_number": "5500-0000-0000-0004",
        "status": "PENDING"
    }
    
    print(f"\nRequest Payload: {json.dumps(payload, indent=2)}")
    response = requests.post(f"{BASE_URL}/api/v2/transactions", json=payload)
    print_response(response, "Create Transaction Response")
    
    assert response.status_code == 201, "Should return 201 Created"
    data = response.json()
    
    # Should have deprecation warning
    if 'deprecation_warning' in data:
        print(f"\n⚠️  Deprecation Warning: {data['deprecation_warning']}")
    
    transaction = data['data']
    assert 'payment_token' in transaction, "Should auto-generate payment_token"
    print(f"\n✅ Auto-generated token: {transaction['payment_token']}")
    
    return transaction['id']


def test_v2_get_transaction_by_id(transaction_id: int):
    """Test V2: GET transaction by ID."""
    print_test_header(f"V2 - GET Transaction by ID: {transaction_id}")
    response = requests.get(f"{BASE_URL}/api/v2/transactions/{transaction_id}")
    print_response(response)
    
    assert response.status_code == 200, "Should return 200"
    data = response.json()
    assert 'code' in data, "V2 should have code"
    assert data['data']['id'] == transaction_id, "Should return correct transaction"


def test_v2_delete_transaction(transaction_id: int):
    """Test V2: DELETE transaction."""
    print_test_header(f"V2 - DELETE Transaction ID: {transaction_id}")
    response = requests.delete(f"{BASE_URL}/api/v2/transactions/{transaction_id}")
    print_response(response)
    
    assert response.status_code == 200, "Should return 200"
    data = response.json()
    assert 'code' in data, "V2 should have code"


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_error_handling_v1():
    """Test V1 error handling."""
    print_test_header("V1 - Error Handling (Invalid Request)")
    
    payload = {
        "amount": 100.0
        # Missing card_number
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/payments", json=payload)
    print_response(response)
    
    assert response.status_code == 400, "Should return 400 Bad Request"
    data = response.json()
    assert 'status_code' in data, "Error should have status_code"
    assert data['status_code'] == 400, "Status code should be 400"


def test_error_handling_v2():
    """Test V2 error handling."""
    print_test_header("V2 - Error Handling (Invalid Request)")
    
    payload = {
        "amount": 100.0
        # Missing payment_token or card_number
    }
    
    response = requests.post(f"{BASE_URL}/api/v2/transactions", json=payload)
    print_response(response)
    
    assert response.status_code == 400, "Should return 400 Bad Request"
    data = response.json()
    assert 'code' in data, "Error should have code"
    assert data['code'] == 400, "Code should be 400"


# ============================================================================
# Main Test Runner
# ============================================================================

def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "🎯" * 40)
    print("STARTING ADAPTERTRANSFORMER API TESTS")
    print("🎯" * 40)
    
    try:
        # Basic tests
        test_root_endpoint()
        test_health_check()
        
        # V1 API tests
        test_v1_get_all_payments()
        v1_payment_id = test_v1_create_payment()
        test_v1_get_payment_by_id(v1_payment_id)
        test_v1_delete_payment(v1_payment_id)
        
        # V2 API tests
        test_v2_get_all_transactions()
        v2_transaction_id_1 = test_v2_create_transaction_with_token()
        v2_transaction_id_2 = test_v2_create_transaction_with_card_number()
        test_v2_get_transaction_by_id(v2_transaction_id_1)
        test_v2_delete_transaction(v2_transaction_id_1)
        test_v2_delete_transaction(v2_transaction_id_2)
        
        # Error handling tests
        test_error_handling_v1()
        test_error_handling_v2()
        
        # Summary
        print("\n" + "✅" * 40)
        print("ALL TESTS PASSED!")
        print("✅" * 40)
        print("\n📊 Test Summary:")
        print("   ✅ Root & Health endpoints")
        print("   ✅ V1 API (payments) - CRUD operations")
        print("   ✅ V2 API (transactions) - CRUD operations")
        print("   ✅ V2 Backward compatibility (card_number → token)")
        print("   ✅ Error handling for both versions")
        print("\n🎉 AdapterTransformer pattern working perfectly!")
        
    except AssertionError as e:
        print("\n" + "❌" * 40)
        print(f"TEST FAILED: {e}")
        print("❌" * 40)
        raise
    except requests.exceptions.ConnectionError:
        print("\n" + "⚠️" * 40)
        print("ERROR: Cannot connect to server!")
        print("Please start the server first:")
        print("  cd AdapterTransformer")
        print("  python app.py")
        print("⚠️" * 40)


if __name__ == '__main__':
    run_all_tests()
