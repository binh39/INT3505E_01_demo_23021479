# Test script cho API v1
# Chạy file này sau khi start server: python app.py

import requests
import json

BASE_URL = "http://localhost:5000/api/v1"

def print_response(title, response):
    """Print formatted response"""
    print("\n" + "="*60)
    print(f"{title}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print("="*60)

def test_api_v1():
    """Test all v1 endpoints"""
    # Test 1: Create a payment
    print("\n🔹 TEST 1: Create Payment (POST)")
    payment_data = {
        "amount": 150.75,
        "card_number": "4111111111111111",
        "status": "SUCCESS"
    }
    response = requests.post(f"{BASE_URL}/payments", json=payment_data)
    print_response("Create Payment Response", response)
    
    # Get payment_id from response
    payment_id = response.json()['data']['id']
    
    # Test 2: Create another payment
    print("\n🔹 TEST 2: Create Another Payment (PENDING)")
    payment_data_2 = {
        "amount": 200.00,
        "card_number": "5500000000000004",
        "status": "PENDING"
    }
    response = requests.post(f"{BASE_URL}/payments", json=payment_data_2)
    print_response("Create Another Payment Response", response)
    
    # Test 3: Get all payments
    print("\n🔹 TEST 3: Get All Payments (GET)")
    response = requests.get(f"{BASE_URL}/payments")
    print_response("Get All Payments Response", response)
    
    # Test 4: Get specific payment
    print("\n🔹 TEST 4: Get Payment by ID (GET)")
    response = requests.get(f"{BASE_URL}/payments/{payment_id}")
    print_response(f"Get Payment {payment_id} Response", response)
    
    # Test 5: Try to get non-existent payment
    print("\n🔹 TEST 5: Get Non-existent Payment (GET)")
    response = requests.get(f"{BASE_URL}/payments/9999")
    print_response("Get Non-existent Payment Response", response)
    
    # Test 6: Create payment with missing fields
    print("\n🔹 TEST 6: Create Payment with Missing Fields (POST)")
    bad_data = {
        "amount": 100.00
        # Missing card_number and status
    }
    response = requests.post(f"{BASE_URL}/payments", json=bad_data)
    print_response("Create Payment with Missing Fields Response", response)
    
    # Test 7: Create payment with invalid status
    print("\n🔹 TEST 7: Create Payment with Invalid Status (POST)")
    invalid_data = {
        "amount": 100.00,
        "card_number": "4111111111111111",
        "status": "INVALID_STATUS"
    }
    response = requests.post(f"{BASE_URL}/payments", json=invalid_data)
    print_response("Create Payment with Invalid Status Response", response)
    
    # Test 8: Delete a payment
    print("\n🔹 TEST 8: Delete Payment (DELETE)")
    response = requests.delete(f"{BASE_URL}/payments/{payment_id}")
    print_response(f"Delete Payment {payment_id} Response", response)
    
    # Test 9: Try to delete the same payment again
    print("\n🔹 TEST 9: Delete Non-existent Payment (DELETE)")
    response = requests.delete(f"{BASE_URL}/payments/{payment_id}")
    print_response("Delete Non-existent Payment Response", response)
    
    # Test 10: Verify deletion
    print("\n🔹 TEST 10: Get All Payments After Deletion (GET)")
    response = requests.get(f"{BASE_URL}/payments")
    print_response("Get All Payments After Deletion Response", response)
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)

if __name__ == "__main__":
    try:
        # Check if server is running
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            print("✅ Server is running!")
            test_api_v1()
        else:
            print("❌ Server returned unexpected status")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server.")
        print("Please start the server first: python app.py")
