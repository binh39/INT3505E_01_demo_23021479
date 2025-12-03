"""
Test suite for Query Parameter API Versioning
Tests both V1 and V2 endpoints using query parameters
"""
import requests

BASE_URL = "http://localhost:5003/api/payments"


def test_v1_get_all_payments():
    """Test GET /api/payments?version=1"""
    print("\n=== TEST: V1 GET All Payments ===")
    response = requests.get(f"{BASE_URL}?version=1")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert 'status_code' in response.json()
    assert '_links' in response.json()
    print("✅ V1 GET All Payments: PASSED")


def test_v1_get_single_payment():
    """Test GET /api/payments/{id}?version=1"""
    print("\n=== TEST: V1 GET Single Payment ===")
    response = requests.get(f"{BASE_URL}/1?version=1")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code in [200, 404]
    assert '_links' in response.json()
    print("✅ V1 GET Single Payment: PASSED")


def test_v1_create_payment():
    """Test POST /api/payments?version=1"""
    print("\n=== TEST: V1 CREATE Payment ===")
    payload = {
        "amount": 150.75,
        "card_number": "4111-1111-1111-1111",
        "status": "SUCCESS"
    }
    response = requests.post(f"{BASE_URL}?version=1", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201
    assert 'status_code' in response.json()
    assert 'transaction_id' in response.json()['data']
    assert '_links' in response.json()
    print("✅ V1 CREATE Payment: PASSED")
    return response.json()['data']['id']


def test_v1_delete_payment(payment_id):
    """Test DELETE /api/payments/{id}?version=1"""
    print(f"\n=== TEST: V1 DELETE Payment (ID: {payment_id}) ===")
    response = requests.delete(f"{BASE_URL}/{payment_id}?version=1")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code in [200, 404]
    assert '_links' in response.json()
    print("✅ V1 DELETE Payment: PASSED")


def test_v2_get_all_transactions():
    """Test GET /api/payments?version=2"""
    print("\n=== TEST: V2 GET All Transactions ===")
    response = requests.get(f"{BASE_URL}?version=2")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert 'code' in response.json()
    assert '_links' in response.json()
    print("✅ V2 GET All Transactions: PASSED")


def test_v2_get_single_transaction():
    """Test GET /api/payments/{id}?version=2"""
    print("\n=== TEST: V2 GET Single Transaction ===")
    response = requests.get(f"{BASE_URL}/1?version=2")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code in [200, 404]
    assert '_links' in response.json()
    print("✅ V2 GET Single Transaction: PASSED")


def test_v2_create_transaction():
    """Test POST /api/payments?version=2"""
    print("\n=== TEST: V2 CREATE Transaction ===")
    payload = {
        "amount": 250.00,
        "card_number": "5555-5555-5555-4444",
        "status": "SUCCESS"
    }
    response = requests.post(f"{BASE_URL}?version=2", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201
    assert 'code' in response.json()
    assert 'payment_token' in response.json()['data']
    assert '_links' in response.json()
    print("✅ V2 CREATE Transaction: PASSED")
    return response.json()['data']['id']


def test_v2_delete_transaction(transaction_id):
    """Test DELETE /api/payments/{id}?version=2"""
    print(f"\n=== TEST: V2 DELETE Transaction (ID: {transaction_id}) ===")
    response = requests.delete(f"{BASE_URL}/{transaction_id}?version=2")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code in [200, 404]
    assert '_links' in response.json()
    print("✅ V2 DELETE Transaction: PASSED")


def test_default_version():
    """Test no version parameter defaults to V1"""
    print("\n=== TEST: Default Version (No Parameter) ===")
    response = requests.get(BASE_URL)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert 'status_code' in response.json()  # V1 format
    print("✅ Default Version (V1): PASSED")


def test_invalid_version():
    """Test invalid version parameter defaults to V1"""
    print("\n=== TEST: Invalid Version Parameter ===")
    response = requests.get(f"{BASE_URL}?version=99")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert 'status_code' in response.json()  # Should default to V1
    print("✅ Invalid Version (Defaults to V1): PASSED")


def test_version_aliases():
    """Test version aliases (v1 and v2)"""
    print("\n=== TEST: Version Aliases ===")
    
    # Test v1 alias
    response = requests.get(f"{BASE_URL}?version=v1")
    print(f"V1 Alias Status: {response.status_code}")
    assert response.status_code == 200
    assert 'status_code' in response.json()
    
    # Test v2 alias
    response = requests.get(f"{BASE_URL}?version=v2")
    print(f"V2 Alias Status: {response.status_code}")
    assert response.status_code == 200
    assert 'code' in response.json()
    
    print("✅ Version Aliases: PASSED")


def test_hateoas_links():
    """Test HATEOAS links in responses"""
    print("\n=== TEST: HATEOAS Links ===")
    
    # V1 HATEOAS
    response = requests.get(f"{BASE_URL}/1?version=1")
    data = response.json()
    assert '_links' in data
    assert 'self' in data['_links']
    assert 'collection' in data['_links']
    print("V1 HATEOAS links present")
    
    # V2 HATEOAS
    response = requests.get(f"{BASE_URL}/1?version=2")
    data = response.json()
    assert '_links' in data
    assert 'self' in data['_links']
    assert 'collection' in data['_links']
    print("V2 HATEOAS links present")
    
    print("✅ HATEOAS Links: PASSED")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 Query Parameter API Versioning - Test Suite")
    print("="*60)
    
    try:
        # V1 Tests
        test_v1_get_all_payments()
        test_v1_get_single_payment()
        v1_payment_id = test_v1_create_payment()
        test_v1_delete_payment(v1_payment_id)
        
        # V2 Tests
        test_v2_get_all_transactions()
        test_v2_get_single_transaction()
        v2_transaction_id = test_v2_create_transaction()
        test_v2_delete_transaction(v2_transaction_id)
        
        # Edge Cases
        test_default_version()
        test_invalid_version()
        test_version_aliases()
        test_hateoas_links()
        
        print("\n" + "="*60)
        print("✅ All tests passed!")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: Is the server running on port 5003?")
        print("Start server with: python app.py")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == '__main__':
    run_all_tests()
