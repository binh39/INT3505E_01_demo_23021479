import requests
import json
from datetime import datetime

WEBHOOK_URL = "http://localhost:5001"

def send_book_event(event_type, book_data):
    """Gửi event về sách đến webhook receiver."""
    url = f"{WEBHOOK_URL}/webhook/books"
    
    payload = {
        'event_type': event_type,
        'timestamp': datetime.now().isoformat(),
        'data': book_data
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-Webhook-Source': 'library-api'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"[SENT] {event_type}")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        return response
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to webhook receiver at {url}")
        print("  Make sure webhook_receiver.py is running on port 5001")
        return None


def send_notification(message, level="info"):
    """Gửi thông báo chung."""
    url = f"{WEBHOOK_URL}/webhook/notifications"
    
    payload = {
        'message': message,
        'level': level,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"[SENT] Notification: {message}")
        print(f"  Status: {response.status_code}")
        return response
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to webhook receiver at {url}")
        return None


def get_received_events():
    """Lấy danh sách events đã nhận."""
    url = f"{WEBHOOK_URL}/webhook/events"
    
    try:
        response = requests.get(url)
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to webhook receiver")
        return None


def demo():
    """Chạy demo webhook."""
    print("\n" + "=" * 60)
    print("  WEBHOOK DEMO")
    print("=" * 60)
    
    # Check webhook receiver health
    print("\n[1] Checking webhook receiver health...")
    try:
        health = requests.get(f"{WEBHOOK_URL}/health")
        print(f"  Webhook receiver status: {health.json()['status']}")
    except:
        print("  [ERROR] Webhook receiver is not running!")
        print("  Please start it first: python webhook_receiver.py")
        return
    
    print("\n" + "-" * 40)
    
    # Send book borrowed event
    print("\n[2] Sending 'book_borrowed' event...")
    send_book_event('book_borrowed', {
        'book_key': 'B001',
        'user_id': 'user_123',
        'borrowed_at': datetime.now().isoformat()
    })
    
    print("\n" + "-" * 40)
    
    # Send book returned event
    print("\n[3] Sending 'book_returned' event...")
    send_book_event('book_returned', {
        'book_key': 'B002',
        'user_id': 'user_456',
        'returned_at': datetime.now().isoformat()
    })
    
    print("\n" + "-" * 40)
    
    # Send notification
    print("\n[4] Sending notification...")
    send_notification("Library system started successfully", "info")
    
    print("\n" + "-" * 40)
    
    # Get all received events
    print("\n[5] Fetching all received events...")
    events = get_received_events()
    if events:
        print(f"  Total events: {events['total_events']}")
        for i, event in enumerate(events['events'], 1):
            print(f"  {i}. [{event.get('event_type', event.get('type', 'unknown'))}] at {event['received_at']}")
    
    print("\n" + "=" * 60)
    print("  DEMO COMPLETED")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    demo()
