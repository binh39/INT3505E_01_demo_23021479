"""
Test script for HeaderVersioning Payment API
Tests V1 and V2 endpoints using HTTP headers for versioning.
"""
import requests
import json


BASE_URL = 'http://localhost:5001'


def print_test_header(test_name: str):
    """Print formatted test header."""
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)


def print_response(response: requests.Response, label: str = "Response"):
    """Print formatted response."""
    print(f"\n{label}:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: API-Version = {response.request.headers.get('API-Version', 'not set')}")
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Body: {response.text}")


def test_root_endpoint():
    """Test root endpoint to see API documentation."""
    print_test_header("Root Endpoint - API Documentation")
    response = requests.get(f"{BASE_URL}/")
    print_response(response)
    assert response.status_code == 200


def test_health_check_v1():
    """Test health check with V1 header."""
    print_test_header("Health Check - V1")
    headers = {'API-Version': '1'}
    response = requests.get(f"{BASE_URL}/health", headers=headers)
    print_response(response)
    assert response.status_code == 200


def test_health_check_v2():
    """Test health check with V2 header."""
    print_test_header("Health Check - V2")
    headers = {'API-Version': '2'}
    response = requests.get(f"{BASE_URL}/health", headers=headers)
    print_response(response)
    assert response.status_code == 200


# ============================================================================
# V1 Tests (API-Version: 1)
# ============================================================================

def test_v1_get_all_payments():
    """Test V1: GET all payments with header."""
    print_test_header("V1 - GET All Payments (Header: API-Version: 1)")
    
    headers = {'API-Version': '1'}
    response = requests.get(f"{BASE_URL}/api/payments", headers=headers)
    print_response(response)
    
    assert response.status_code == 200
    data = response.json()
    assert 'status_code' in data, "V1 should have status_code"
    assert 'data' in data
    print("\nV1 format confirmed: has 'status_code'")


def test_v1_create_payment():
    """Test V1: POST create payment."""
    print_test_header("V1 - Create Payment (Header: API-Version: 1)")
    
    headers = {'API-Version': '1', 'Content-Type': 'application/json'}
    payload = {
        "amount": 350.00,
        "card_number": "4532-1234-5678-9010",
        "status": "SUCCESS"
    }
    
    print(f"\nRequest Headers: {headers}")
    print(f"Request Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/payments", headers=headers, json=payload)
    print_response(response, "Create Payment Response")
    
    assert response.status_code == 201
    data = response.json()
    assert 'status_code' in data, "V1 should have status_code"
    assert data['status_code'] == 201
    
    payment = data['data']
    assert 'transaction_id' in payment, "V1 should have transaction_id"
    assert 'card_number' in payment, "V1 should have card_number"
    print(f"\nV1 format confirmed: has transaction_id = {payment['transaction_id']}")
    
    return payment['id']


def test_v1_get_payment_by_id(payment_id: int):
    """Test V1: GET payment by ID."""
    print_test_header(f"V1 - GET Payment by ID: {payment_id} (Header: API-Version: 1)")
    
    headers = {'API-Version': '1'}
    response = requests.get(f"{BASE_URL}/api/payments/{payment_id}", headers=headers)
    print_response(response)
    
    assert response.status_code == 200
    data = response.json()
    assert 'status_code' in data
    assert data['data']['id'] == payment_id


def test_v1_delete_payment(payment_id: int):
    """Test V1: DELETE payment."""
    print_test_header(f"V1 - DELETE Payment ID: {payment_id} (Header: API-Version: 1)")
    
    headers = {'API-Version': '1'}
    response = requests.delete(f"{BASE_URL}/api/payments/{payment_id}", headers=headers)
    print_response(response)
    
    assert response.status_code == 200
    data = response.json()
    assert 'status_code' in data


# ============================================================================
# V2 Tests (API-Version: 2)
# ============================================================================

def test_v2_get_all_transactions():
    """Test V2: GET all transactions with header."""
    print_test_header("V2 - GET All Transactions (Header: API-Version: 2)")
    
    headers = {'API-Version': '2'}
    response = requests.get(f"{BASE_URL}/api/payments", headers=headers)
    print_response(response)
    
    assert response.status_code == 200
    data = response.json()
    assert 'code' in data, "V2 should have 'code' not 'status_code'"
    assert 'data' in data
    print("\nV2 format confirmed: has 'code' instead of 'status_code'")


def test_v2_create_transaction_with_token():
    """Test V2: POST create transaction with payment_token."""
    print_test_header("V2 - Create Transaction with Token (Header: API-Version: 2)")
    
    headers = {'API-Version': '2', 'Content-Type': 'application/json'}
    payload = {
        "amount": 550.99,
        "payment_token": "TOK-XYZ789ABC456",
        "status": "SUCCESS"
    }
    
    print(f"\nRequest Headers: {headers}")
    print(f"Request Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/payments", headers=headers, json=payload)
    print_response(response, "Create Transaction Response")
    
    assert response.status_code == 201
    data = response.json()
    assert 'code' in data, "V2 should have code"
    assert data['code'] == 201
    
    transaction = data['data']
    assert 'transaction_id' not in transaction, "V2 should NOT have transaction_id"
    assert 'payment_token' in transaction, "V2 should have payment_token"
    assert 'code' in transaction, "V2 data should have code field"
    print("\nV2 format confirmed: NO transaction_id, has payment_token")
    
    return transaction['id']


def test_v2_create_transaction_with_card_number():
    """Test V2: POST with card_number (backward compatibility)."""
    print_test_header("V2 - Create with card_number (Deprecated - Header: API-Version: 2)")
    
    headers = {'API-Version': '2', 'Content-Type': 'application/json'}
    payload = {
        "amount": 225.50,
        "card_number": "5500-0000-0000-0004",
        "status": "PENDING"
    }
    
    print(f"\nRequest Headers: {headers}")
    print(f"Request Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/payments", headers=headers, json=payload)
    print_response(response, "Create Transaction Response")
    
    assert response.status_code == 201
    data = response.json()
    
    if 'deprecation_warning' in data:
        print(f"\nDeprecation Warning: {data['deprecation_warning']}")
    
    transaction = data['data']
    assert 'payment_token' in transaction, "Should auto-generate payment_token"
    print(f"\nAuto-generated token: {transaction['payment_token']}")
    
    return transaction['id']


def test_v2_get_transaction_by_id(transaction_id: int):
    """Test V2: GET transaction by ID."""
    print_test_header(f"V2 - GET Transaction by ID: {transaction_id} (Header: API-Version: 2)")
    
    headers = {'API-Version': '2'}
    response = requests.get(f"{BASE_URL}/api/payments/{transaction_id}", headers=headers)
    print_response(response)
    
    assert response.status_code == 200
    data = response.json()
    assert 'code' in data
    assert data['data']['id'] == transaction_id


def test_v2_delete_transaction(transaction_id: int):
    """Test V2: DELETE transaction."""
    print_test_header(f"V2 - DELETE Transaction ID: {transaction_id} (Header: API-Version: 2)")
    
    headers = {'API-Version': '2'}
    response = requests.delete(f"{BASE_URL}/api/payments/{transaction_id}", headers=headers)
    print_response(response)
    
    assert response.status_code == 200
    data = response.json()
    assert 'code' in data


# ============================================================================
# Special Tests
# ============================================================================

def test_no_header_defaults_to_v1():
    """Test that no header defaults to V1."""
    print_test_header("No Header - Should Default to V1")
    
    # No API-Version header
    response = requests.get(f"{BASE_URL}/api/payments")
    print_response(response)
    
    assert response.status_code == 200
    data = response.json()
    assert 'status_code' in data, "Should default to V1 format"
    print("\nConfirmed: No header defaults to V1")


def test_invalid_version_header():
    """Test invalid version header."""
    print_test_header("Invalid Version Header - Should Return Error")
    
    headers = {'API-Version': '99'}
    response = requests.get(f"{BASE_URL}/api/payments", headers=headers)
    print_response(response)
    
    assert response.status_code == 400
    data = response.json()
    assert 'error' in data or 'message' in data
    print("\nConfirmed: Invalid version rejected")


def test_same_endpoint_different_versions():
    """Test same endpoint with different headers returns different formats."""
    print_test_header("Same Endpoint - Different Versions")
    
    endpoint = f"{BASE_URL}/api/payments"
    
    # V1 request
    print("\nRequest 1: API-Version: 1")
    v1_response = requests.get(endpoint, headers={'API-Version': '1'})
    v1_data = v1_response.json()
    print(f"V1 Response: {json.dumps(v1_data, indent=2)}")
    
    # V2 request
    print("\nRequest 2: API-Version: 2")
    v2_response = requests.get(endpoint, headers={'API-Version': '2'})
    v2_data = v2_response.json()
    print(f"V2 Response: {json.dumps(v2_data, indent=2)}")
    
    # Verify different formats
    assert 'status_code' in v1_data, "V1 should have status_code"
    assert 'code' in v2_data, "V2 should have code"
    assert 'status_code' not in v2_data, "V2 should NOT have status_code"
    
    print("\nConfirmed: Same URL, different formats based on header!")


# ============================================================================
# Main Test Runner
# ============================================================================

def run_all_tests():
    """Run all tests in sequence."""
    print("STARTING HEADER-BASED VERSIONING API TESTS")
    
    try:
        # Basic tests
        test_root_endpoint()
        test_health_check_v1()
        test_health_check_v2()
        
        # V1 tests
        test_v1_get_all_payments()
        v1_payment_id = test_v1_create_payment()
        test_v1_get_payment_by_id(v1_payment_id)
        test_v1_delete_payment(v1_payment_id)
        
        # V2 tests
        test_v2_get_all_transactions()
        v2_transaction_id_1 = test_v2_create_transaction_with_token()
        v2_transaction_id_2 = test_v2_create_transaction_with_card_number()
        test_v2_get_transaction_by_id(v2_transaction_id_1)
        test_v2_delete_transaction(v2_transaction_id_1)
        test_v2_delete_transaction(v2_transaction_id_2)
        
        # Special tests
        test_no_header_defaults_to_v1()
        test_invalid_version_header()
        test_same_endpoint_different_versions()
        
        # Summary
        print("ALL TESTS PASSED!")
        print("\nTest Summary:")
        print("Root & Health endpoints")
        print("V1 API (Header: API-Version: 1)")
        print("V2 API (Header: API-Version: 2)")
        print("Default to V1 when no header")
        print("Invalid version rejection")
        print("Same endpoint, different formats")
        print("\nHeader-based versioning working perfectly!")
        print("\nKey Insight:")
        print("Same URL (/api/payments) returns different formats")
        print("based on the API-Version header!")
        
    except AssertionError as e:
        print("\n" + "❌" * 40)
        print(f"TEST FAILED: {e}")
        print("❌" * 40)
        raise
    except requests.exceptions.ConnectionError:
        print("\n" + "⚠️" * 40)
        print("ERROR: Cannot connect to server!")
        print("Please start the server first:")
        print("  cd HeaderVersioning")
        print("  python app.py")
        print("⚠️" * 40)


if __name__ == '__main__':
    run_all_tests()
