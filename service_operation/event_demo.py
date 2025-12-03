"""
Demo: Event-Driven Architecture Pattern
This script demonstrates Publisher-Subscriber pattern with async event handling

Run this script: python event_demo.py
"""

import time
import threading
from datetime import datetime
from events import EventBus


def create_demo():
    """Create a fresh EventBus for demonstration"""
    print("\n" + "="*60)
    print("  EVENT-DRIVEN ARCHITECTURE DEMO")
    print("  Publisher-Subscriber Pattern")
    print("="*60 + "\n")

    # Create new EventBus instance for demo
    demo_bus = EventBus()

    # ============================================
    # Define Event Handlers (Consumers/Subscribers)
    # ============================================
    
    def email_notification_handler(event):
        """Simulates sending email notification"""
        data = event['data']
        print(f"  [EMAIL SERVICE] Sending email about: {data.get('action', 'event')}")
        time.sleep(0.2)  # Simulate async operation
        print(f"  [EMAIL SERVICE] Email sent successfully!")

    def sms_notification_handler(event):
        """Simulates sending SMS notification"""
        data = event['data']
        print(f"  [SMS SERVICE] Sending SMS: {data.get('message', 'notification')}")
        time.sleep(0.1)  # Simulate async operation
        print(f"  [SMS SERVICE] SMS delivered!")

    def analytics_handler(event):
        """Logs event for analytics"""
        print(f"  [ANALYTICS] Recorded event: {event['type']} at {event['timestamp']}")

    def inventory_handler(event):
        """Updates inventory based on events"""
        data = event['data']
        action = data.get('action', '')
        if action == 'borrowed':
            print(f"  [INVENTORY] Book checked out: {data.get('book_key')}")
        elif action == 'returned':
            print(f"  [INVENTORY] Book checked in: {data.get('book_key')}")

    def audit_log_handler(event):
        """Records all events for audit purposes"""
        print(f"  [AUDIT LOG] {event['type']}: {event['data']}")

    # ============================================
    # Subscribe Handlers to Events
    # ============================================
    print("[SETUP] Subscribing handlers to events...\n")
    
    # One event can have multiple subscribers
    demo_bus.subscribe('order.created', email_notification_handler)
    demo_bus.subscribe('order.created', sms_notification_handler)
    demo_bus.subscribe('order.created', analytics_handler)
    demo_bus.subscribe('order.created', audit_log_handler)
    
    # Different events can share handlers
    demo_bus.subscribe('book.borrowed', inventory_handler)
    demo_bus.subscribe('book.borrowed', analytics_handler)
    demo_bus.subscribe('book.borrowed', audit_log_handler)
    
    demo_bus.subscribe('book.returned', inventory_handler)
    demo_bus.subscribe('book.returned', analytics_handler)
    demo_bus.subscribe('book.returned', audit_log_handler)

    demo_bus.subscribe('user.registered', email_notification_handler)
    demo_bus.subscribe('user.registered', analytics_handler)

    # Start the event processing worker
    demo_bus.start()
    
    print("Subscriptions configured:")
    print("  - order.created -> email, sms, analytics, audit")
    print("  - book.borrowed -> inventory, analytics, audit")
    print("  - book.returned -> inventory, analytics, audit")
    print("  - user.registered -> email, analytics")
    print()

    # ============================================
    # Publish Events (Non-blocking)
    # ============================================
    
    print("-" * 60)
    print("SCENARIO 1: User borrows a book")
    print("-" * 60)
    
    # This is NON-BLOCKING - returns immediately
    start = time.time()
    demo_bus.publish('book.borrowed', {
        'book_key': 'B001',
        'title': 'Clean Code',
        'action': 'borrowed'
    })
    elapsed = (time.time() - start) * 1000
    print(f"[PUBLISHER] Event published in {elapsed:.2f}ms (non-blocking!)")
    print("[PUBLISHER] Main thread continues while events are processed...\n")
    
    # Wait for events to be processed
    time.sleep(0.5)
    
    print("\n" + "-" * 60)
    print("SCENARIO 2: New order is created (triggers 4 handlers)")
    print("-" * 60)
    
    demo_bus.publish('order.created', {
        'order_id': 'ORD-12345',
        'amount': 99.99,
        'action': 'New Order',
        'message': 'Your order #12345 is confirmed'
    })
    print("[PUBLISHER] Order event published\n")
    
    time.sleep(0.8)
    
    print("\n" + "-" * 60)
    print("SCENARIO 3: Book is returned")
    print("-" * 60)
    
    demo_bus.publish('book.returned', {
        'book_key': 'B001',
        'action': 'returned'
    })
    print("[PUBLISHER] Return event published\n")
    
    time.sleep(0.5)
    
    print("\n" + "-" * 60)
    print("SCENARIO 4: Multiple events in quick succession")
    print("-" * 60)
    
    # Publish multiple events rapidly
    for i in range(3):
        demo_bus.publish('user.registered', {
            'user_id': f'USER-{i+1}',
            'action': f'User {i+1} registered',
            'message': f'Welcome User {i+1}!'
        })
    print(f"[PUBLISHER] Published 3 user registration events")
    print(f"[PUBLISHER] Queue has {demo_bus.get_pending_count()} pending events\n")
    
    # Wait for all events to be processed
    time.sleep(1.5)
    
    # ============================================
    # Cleanup
    # ============================================
    print("\n" + "="*60)
    print("DEMO COMPLETE!")
    print("="*60)
    print("""
Key Takeaways:
1. Publishers don't wait for handlers - events are async
2. One event can trigger multiple handlers
3. Handlers run in background thread (non-blocking)
4. Events are queued and processed in order
5. Decouples producer from consumers (loose coupling)

Benefits:
- Scalability: Add new handlers without changing publisher
- Flexibility: Services can subscribe/unsubscribe dynamically
- Resilience: Failure in one handler doesn't affect others
- Loose Coupling: Publisher doesn't know about subscribers
""")
    
    demo_bus.stop()


if __name__ == "__main__":
    create_demo()
