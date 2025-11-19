# Test script cho API v2 - Breaking Changes Demo
# Chạy file này sau khi start server: python app.py

import requests
import json
import hashlib

BASE_URL = "http://localhost:5000/api/v2"

def print_colored_separator(char="=", length=80):
    """Print separator line"""
    print("\n" + char * length)

def print_section_header(title, emoji="🔹"):
    """Print test section header"""
    print_colored_separator("=")
    print(f"\n{emoji} {title}")
    print()

def print_response(response, title=None):
    """Print formatted response with colors"""
    if title:
        print(f"\n📋 {title}")
    print(f"Status Code: {response.status_code}")
    print("Response:")
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # Highlight warnings if present
    if isinstance(data.get('data'), dict) and '_warnings' in data['data']:
        print("\n⚠️  DEPRECATION WARNINGS:")
        for warning in data['data']['_warnings']:
            print(f"   - {warning}")
    
    if isinstance(data.get('data'), dict) and '_deprecated' in data['data']:
        print(f"\n📢 DEPRECATION NOTICE: {data['data']['_deprecated']['message']}")
        print(f"   Migration Guide: {data['data']['_deprecated']['migration_guide']}")

def generate_payment_token(card_number):
    """Generate payment token from card number (same as v2 API)"""
    token = hashlib.sha256(card_number.encode()).hexdigest()[:32].upper()
    return f"TOK-{token}"

def test_migration_guide():
    """Test 1: Get migration guide"""
    print_section_header("TEST 1: Get Migration Guide", "📖")
    
    response = requests.get(f"{BASE_URL}/migration-guide")
    print_response(response, "Migration Guide")
    
    if response.status_code == 200:
        data = response.json()['data']
        print("\n🚨 Breaking Changes Summary:")
        for change in data['breaking_changes']:
            print(f"\n  • {change['change']}")
            print(f"    v1: {change['v1']}")
            print(f"    v2: {change['v2']}")
            print(f"    Reason: {change['reason']}")
        
        print(f"\n⏰ Deprecation Timeline:")
        timeline = data['deprecation_timeline']
        print(f"  • v1 Deprecation: {timeline['v1_deprecation_date']}")
        print(f"  • v1 Sunset: {timeline['v1_sunset_date']}")
        print(f"  • Message: {timeline['message']}")
    
    return response

def test_create_transaction_v2_style():
    """Test 2: Create transaction with payment_token (v2 way)"""
    print_section_header("TEST 2: Create Transaction with payment_token (v2 style)", "✅")
    
    transaction_data = {
        "amount": 150.00,
        "payment_token": "TOK-ABC123DEF456GHI789JKL012MNO",
        "status": "SUCCESS"
    }
    
    print("Request Body (v2 recommended):")
    print(json.dumps(transaction_data, indent=2))
    
    response = requests.post(f"{BASE_URL}/transactions", json=transaction_data)
    print_response(response, "Create Transaction Response")
    
    if response.status_code == 201:
        data = response.json()['data']
        print("\n✅ Created successfully!")
        print(f"   ID: {data['id']}")
        print(f"   Payment Token: {data['payment_token']}")
        print(f"   Code: {data['code']}")
        print(f"   Status: {data['status']}")
        return data['id']
    
    return None

def test_create_transaction_backward_compat():
    """Test 3: Create transaction with card_number (backward compatibility)"""
    print_section_header("TEST 3: Create Transaction with card_number (backward compatibility)", "⚠️")
    
    transaction_data = {
        "amount": 250.00,
        "card_number": "4532-1234-5678-9010",  # Deprecated field
        "status": "PENDING"
    }
    
    print("Request Body (v1 style - deprecated):")
    print(json.dumps(transaction_data, indent=2))
    print("\n⚠️  Using deprecated 'card_number' field for backward compatibility demo")
    
    response = requests.post(f"{BASE_URL}/transactions", json=transaction_data)
    print_response(response, "Create Transaction Response")
    
    if response.status_code == 201:
        data = response.json()['data']
        print("\n✅ Created successfully (with deprecation warning)!")
        print(f"   ID: {data['id']}")
        print(f"   Payment Token (auto-generated): {data['payment_token']}")
        print(f"   Code: {data['code']}")
        return data['id']
    
    return None

def test_create_transaction_with_generated_token():
    """Test 4: Create transaction by generating token from card number"""
    print_section_header("TEST 4: Generate Token from Card Number", "🔐")
    
    card_number = "5555-4444-3333-2222"
    payment_token = generate_payment_token(card_number)
    
    print(f"Card Number: {card_number}")
    print(f"Generated Token: {payment_token}")
    
    transaction_data = {
        "amount": 300.00,
        "payment_token": payment_token,
        "status": "SUCCESS"
    }
    
    print("\nRequest Body:")
    print(json.dumps(transaction_data, indent=2))
    
    response = requests.post(f"{BASE_URL}/transactions", json=transaction_data)
    print_response(response, "Create Transaction Response")
    
    if response.status_code == 201:
        print("\n✅ Token generation and transaction creation successful!")
        return response.json()['data']['id']
    
    return None

def test_get_all_transactions():
    """Test 5: Get all transactions"""
    print_section_header("TEST 5: Get All Transactions", "📊")
    
    response = requests.get(f"{BASE_URL}/transactions")
    print_response(response, "Get All Transactions")
    
    if response.status_code == 200:
        transactions = response.json()['data']
        print(f"\n✅ Retrieved {len(transactions)} transaction(s)")
        
        print("\nTransaction Summary:")
        for txn in transactions:
            print(f"  • ID: {txn['id']}, Amount: ${txn['amount']:.2f}, "
                  f"Status: {txn['status']}, Code: {txn['code']}")
    
    return response

def test_get_transaction_by_id(transaction_id):
    """Test 6: Get specific transaction by ID"""
    print_section_header(f"TEST 6: Get Transaction by ID ({transaction_id})", "🔍")
    
    response = requests.get(f"{BASE_URL}/transactions/{transaction_id}")
    print_response(response, f"Get Transaction {transaction_id}")
    
    if response.status_code == 200:
        data = response.json()['data']
        print("\n✅ Transaction Details:")
        print(f"   ID: {data['id']}")
        print(f"   Amount: ${data['amount']:.2f}")
        print(f"   Payment Token: {data['payment_token']}")
        print(f"   Status: {data['status']}")
        print(f"   Code: {data['code']}")
        print(f"   Created At: {data['created_at']}")
    
    return response

def test_get_nonexistent_transaction():
    """Test 7: Try to get non-existent transaction"""
    print_section_header("TEST 7: Get Non-existent Transaction", "❌")
    
    response = requests.get(f"{BASE_URL}/transactions/99999")
    print_response(response, "Get Non-existent Transaction")
    
    if response.status_code == 404:
        print("\n✅ Correctly returned 404 for non-existent transaction")
    
    return response

def test_create_transaction_missing_fields():
    """Test 8: Create transaction with missing fields"""
    print_section_header("TEST 8: Create Transaction with Missing Fields", "❌")
    
    invalid_data = {
        "amount": 100.00
        # Missing payment_token/card_number and status
    }
    
    print("Request Body (invalid):")
    print(json.dumps(invalid_data, indent=2))
    
    response = requests.post(f"{BASE_URL}/transactions", json=invalid_data)
    print_response(response, "Create Transaction Response")
    
    if response.status_code == 400:
        print("\n✅ Correctly returned 400 for missing required fields")
    
    return response

def test_create_transaction_invalid_status():
    """Test 9: Create transaction with invalid status"""
    print_section_header("TEST 9: Create Transaction with Invalid Status", "❌")
    
    invalid_data = {
        "amount": 100.00,
        "payment_token": "TOK-TEST123",
        "status": "INVALID_STATUS"
    }
    
    print("Request Body (invalid status):")
    print(json.dumps(invalid_data, indent=2))
    
    response = requests.post(f"{BASE_URL}/transactions", json=invalid_data)
    print_response(response, "Create Transaction Response")
    
    if response.status_code == 400:
        print("\n✅ Correctly returned 400 for invalid status")
    
    return response

def test_delete_transaction(transaction_id):
    """Test 10: Delete transaction"""
    print_section_header(f"TEST 10: Delete Transaction ({transaction_id})", "🗑️")
    
    response = requests.delete(f"{BASE_URL}/transactions/{transaction_id}")
    print_response(response, f"Delete Transaction {transaction_id}")
    
    if response.status_code == 200:
        print(f"\n✅ Transaction {transaction_id} deleted successfully!")
    
    return response

def test_delete_nonexistent_transaction():
    """Test 11: Try to delete non-existent transaction"""
    print_section_header("TEST 11: Delete Non-existent Transaction", "❌")
    
    response = requests.delete(f"{BASE_URL}/transactions/99999")
    print_response(response, "Delete Non-existent Transaction")
    
    if response.status_code == 404:
        print("\n✅ Correctly returned 404 for non-existent transaction")
    
    return response

def test_compare_v1_v2():
    """Test 12: Compare v1 and v2 API responses"""
    print_section_header("TEST 12: Compare v1 vs v2 API Response Format", "🔄")
    
    print("📍 v1 API Response Format:")
    print("   Fields: id, transaction_id, amount, card_number, created_at")
    print("   Resource: /api/v1/payments")
    
    print("\n📍 v2 API Response Format:")
    print("   Fields: id, amount, payment_token, status, code, created_at")
    print("   Resource: /api/v2/transactions")
    print("   Additional: _deprecated (migration info)")
    
    print("\n🚨 Key Differences:")
    print("   1. Resource: 'payments' → 'transactions'")
    print("   2. Removed: 'transaction_id' (use 'id' directly)")
    print("   3. Replaced: 'card_number' → 'payment_token' (security)")
    print("   4. Renamed: 'status_code' → 'code'")
    
    # Try to get v1 data for comparison
    try:
        v1_response = requests.get("http://localhost:5000/api/v1/payments")
        if v1_response.status_code == 200:
            v1_data = v1_response.json()['data']
            if v1_data:
                print("\n📊 v1 Sample Response:")
                print(json.dumps(v1_data[0], indent=2))
    except:
        pass
    
    # Get v2 data
    v2_response = requests.get(f"{BASE_URL}/transactions")
    if v2_response.status_code == 200:
        v2_data = v2_response.json()['data']
        if v2_data:
            print("\n📊 v2 Sample Response:")
            print(json.dumps(v2_data[0], indent=2))

def run_all_tests():
    """Run all v2 API tests"""
    print_colored_separator("=", 80)
    print("\n🚀 API v2 Testing Suite - Breaking Changes Demo")
    print("   Testing: /api/v2/transactions")
    print_colored_separator("=", 80)
    
    # Store transaction IDs for later tests
    transaction_ids = []
    
    # Test 1: Migration guide
    test_migration_guide()
    
    # Test 2: Create transaction v2 style
    txn_id = test_create_transaction_v2_style()
    if txn_id:
        transaction_ids.append(txn_id)
    
    # Test 3: Create transaction with backward compatibility
    txn_id = test_create_transaction_backward_compat()
    if txn_id:
        transaction_ids.append(txn_id)
    
    # Test 4: Generate token and create transaction
    txn_id = test_create_transaction_with_generated_token()
    if txn_id:
        transaction_ids.append(txn_id)
    
    # Test 5: Get all transactions
    test_get_all_transactions()
    
    # Test 6: Get specific transaction
    if transaction_ids:
        test_get_transaction_by_id(transaction_ids[0])
    
    # Test 7: Get non-existent transaction
    test_get_nonexistent_transaction()
    
    # Test 8: Missing fields
    test_create_transaction_missing_fields()
    
    # Test 9: Invalid status
    test_create_transaction_invalid_status()
    
    # Test 10: Delete transaction
    if transaction_ids and len(transaction_ids) > 1:
        test_delete_transaction(transaction_ids[1])
    
    # Test 11: Delete non-existent
    test_delete_nonexistent_transaction()
    
    # Test 12: Compare v1 and v2
    test_compare_v1_v2()
    
    # Final summary
    print_colored_separator("=", 80)
    print("\n✅ All v2 API tests completed!")
    print("\n📚 Key Takeaways:")
    print("   1. v2 uses 'transactions' instead of 'payments' (breaking change)")
    print("   2. v2 uses 'code' instead of 'status_code' (breaking change)")
    print("   3. v2 uses 'payment_token' instead of 'card_number' (security)")
    print("   4. v2 removes 'transaction_id', only uses 'id' (simplification)")
    print("   5. v2 provides backward compatibility with deprecation warnings")
    print("   6. Migration guide available at /api/v2/migration-guide")
    print_colored_separator("=", 80)

if __name__ == "__main__":
    try:
        # Check if server is running
        print("🔍 Checking if server is running...")
        response = requests.get("http://localhost:5000/health")
        
        if response.status_code == 200:
            print("✅ Server is running!\n")
            
            # Check API version info
            root = requests.get("http://localhost:5000")
            if root.status_code == 200:
                versions = root.json().get('versions', {})
                if 'v2' in versions:
                    print("✅ v2 API is available!")
                    run_all_tests()
                else:
                    print("❌ Error: v2 API not found in server")
                    print("Please make sure v2 is properly registered in app.py")
        else:
            print("❌ Server returned unexpected status")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server.")
        print("Please start the server first: python app.py")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
