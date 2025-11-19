# Test script cho API v2
# Chạy file này sau khi start server: python app.py

import requests
import json
import hashlib

BASE_URL = "http://localhost:5000/api/v2"

def print_response(title, response):
    """Print formatted response"""
    print("\n" + "="*60)
    print(f"{title}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print("="*60)

def generate_payment_token(card_number):
    """Generate payment token from card number"""
    token = hashlib.sha256(card_number.encode()).hexdigest()[:32].upper()
    return f"TOK-{token}"

def test_api_v2():
    """Test all v2 endpoints"""
    
    # Test 1: Create a transaction (v2 style with payment_token)
    print("\n🔹 TEST 1: Create Transaction with payment_token (v2 style)")
    transaction_data = {
        "amount": 150.75,
        "payment_token": "TOK-ABC123DEF456GHI789JKL012MNO",
        "status": "SUCCESS"
    }
    response = requests.post(f"{BASE_URL}/transactions", json=transaction_data)
    print_response("Create Transaction Response", response)
    
    # Get transaction_id from response
    transaction_id = response.json()['data']['id']
    
    # Test 2: Create transaction with card_number (backward compatibility)
    print("\n🔹 TEST 2: Create Transaction with card_number (backward compatibility)")
    transaction_data_2 = {
        "amount": 200.00,
        "card_number": "5500000000000004",
        "status": "PENDING"
    }
    response = requests.post(f"{BASE_URL}/transactions", json=transaction_data_2)
    print_response("Create Transaction with card_number Response", response)
    
    # Test 3: Create transaction by generating token
    print("\n🔹 TEST 3: Create Transaction with generated token")
    card_number = "4111111111111111"
    payment_token = generate_payment_token(card_number)
    print(f"Card: {card_number} -> Token: {payment_token}")
    
    transaction_data_3 = {
        "amount": 99.99,
        "payment_token": payment_token,
        "status": "REFUND"
    }
    response = requests.post(f"{BASE_URL}/transactions", json=transaction_data_3)
    print_response("Create Transaction with generated token Response", response)
    
    # Test 4: Get all transactions
    print("\n🔹 TEST 4: Get All Transactions (GET)")
    response = requests.get(f"{BASE_URL}/transactions")
    print_response("Get All Transactions Response", response)
    
    # Test 5: Get specific transaction
    print("\n🔹 TEST 5: Get Transaction by ID (GET)")
    response = requests.get(f"{BASE_URL}/transactions/{transaction_id}")
    print_response(f"Get Transaction {transaction_id} Response", response)
    
    # Test 6: Try to get non-existent transaction
    print("\n🔹 TEST 6: Get Non-existent Transaction (GET)")
    response = requests.get(f"{BASE_URL}/transactions/9999")
    print_response("Get Non-existent Transaction Response", response)
    
    # Test 7: Create transaction with missing fields
    print("\n🔹 TEST 7: Create Transaction with Missing Fields (POST)")
    bad_data = {
        "amount": 100.00
        # Missing payment_token/card_number and status
    }
    response = requests.post(f"{BASE_URL}/transactions", json=bad_data)
    print_response("Create Transaction with Missing Fields Response", response)
    
    # Test 8: Create transaction with invalid status
    print("\n🔹 TEST 8: Create Transaction with Invalid Status (POST)")
    invalid_data = {
        "amount": 100.00,
        "payment_token": "TOK-TEST123",
        "status": "INVALID_STATUS"
    }
    response = requests.post(f"{BASE_URL}/transactions", json=invalid_data)
    print_response("Create Transaction with Invalid Status Response", response)
    
    # Test 9: Create transaction without payment_token or card_number
    print("\n🔹 TEST 9: Create Transaction without payment info (POST)")
    no_payment_data = {
        "amount": 100.00,
        "status": "SUCCESS"
    }
    response = requests.post(f"{BASE_URL}/transactions", json=no_payment_data)
    print_response("Create Transaction without payment info Response", response)
    
    # Test 10: Delete a transaction
    print("\n🔹 TEST 10: Delete Transaction (DELETE)")
    response = requests.delete(f"{BASE_URL}/transactions/{transaction_id}")
    print_response(f"Delete Transaction {transaction_id} Response", response)
    
    # Test 11: Try to delete the same transaction again
    print("\n🔹 TEST 11: Delete Non-existent Transaction (DELETE)")
    response = requests.delete(f"{BASE_URL}/transactions/{transaction_id}")
    print_response("Delete Non-existent Transaction Response", response)
    
    # Test 12: Verify deletion
    print("\n🔹 TEST 12: Get All Transactions After Deletion (GET)")
    response = requests.get(f"{BASE_URL}/transactions")
    print_response("Get All Transactions After Deletion Response", response)
    
    # Test 13: Compare v1 and v2
    print("\n🔹 TEST 13: Compare v1 vs v2 Response Format")
    print("\n" + "="*60)
    print("v1 Response includes:")
    print("  - id, transaction_id, amount, card_number, created_at")
    print("\nv2 Response includes:")
    print("  - id, amount, payment_token, status, code, created_at")
    print("\nBreaking Changes:")
    print("  ✗ transaction_id removed (use id)")
    print("  ✗ card_number → payment_token (security)")
    print("  ✗ status_code → code (at response level)")
    print("  ✗ Resource: payments → transactions")
    print("="*60)
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)

if __name__ == "__main__":
    try:
        # Check if server is running
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            print("✅ Server is running!")
            
            # Check if v2 API is available
            root = requests.get("http://localhost:5000")
            if root.status_code == 200:
                versions = root.json().get('versions', {})
                if 'v2' in versions:
                    print("✅ v2 API is available!")
                    test_api_v2()
                else:
                    print("❌ v2 API not found")
        else:
            print("❌ Server returned unexpected status")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server.")
        print("Please start the server first: python app.py")
