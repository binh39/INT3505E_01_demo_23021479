"""
Simple Event-Driven Architecture Module
Publisher-Subscriber pattern with async event handling
"""

import threading
import queue
import time
from datetime import datetime
from typing import Callable, Dict, List, Any
from logger import API_LOGGER as logger


class EventBus:
    """
    Simple in-memory event bus for async event publishing and consuming.
    
    Usage:
        # Subscribe to events
        event_bus.subscribe('book.borrowed', handle_book_borrowed)
        event_bus.subscribe('book.returned', handle_book_returned)
        
        # Publish events (non-blocking)
        event_bus.publish('book.borrowed', {'book_key': 'B001', 'title': 'Clean Code'})
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_queue: queue.Queue = queue.Queue()
        self._running = False
        self._worker_thread = None
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe a handler function to an event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.info("Event handler subscribed", extra={
            'event_type': event_type,
            'handler': handler.__name__
        })
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe a handler from an event type"""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)
    
    def publish(self, event_type: str, data: Any = None):
        """
        Publish an event asynchronously (non-blocking).
        The event is added to a queue and processed by a background worker.
        """
        event = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat(),
            'id': f"{event_type}_{int(time.time() * 1000)}"
        }
        self._event_queue.put(event)
        logger.info("Event published", extra={
            'event_id': event['id'],
            'event_type': event_type,
            'data': data
        })
    
    def _process_events(self):
        """Background worker that processes events from the queue"""
        while self._running:
            try:
                # Wait for event with timeout (allows graceful shutdown)
                event = self._event_queue.get(timeout=1.0)
                self._dispatch_event(event)
                self._event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error("Error processing event", extra={'error': str(e)})
    
    def _dispatch_event(self, event: dict):
        """Dispatch event to all registered subscribers"""
        event_type = event['type']
        handlers = self._subscribers.get(event_type, [])
        
        if not handlers:
            logger.warning("No handlers for event", extra={'event_type': event_type})
            return
        
        for handler in handlers:
            try:
                logger.info("Dispatching event to handler", extra={
                    'event_id': event['id'],
                    'event_type': event_type,
                    'handler': handler.__name__
                })
                handler(event)
                logger.info("Event handled successfully", extra={
                    'event_id': event['id'],
                    'handler': handler.__name__
                })
            except Exception as e:
                logger.error("Event handler error", extra={
                    'event_id': event['id'],
                    'handler': handler.__name__,
                    'error': str(e)
                })
    
    def start(self):
        """Start the background event processing worker"""
        if self._running:
            return
        self._running = True
        self._worker_thread = threading.Thread(target=self._process_events, daemon=True)
        self._worker_thread.start()
        logger.info("EventBus started", extra={'status': 'running'})
    
    def stop(self):
        """Stop the event processing worker"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5.0)
        logger.info("EventBus stopped", extra={'status': 'stopped'})
    
    def get_pending_count(self) -> int:
        """Get number of pending events in queue"""
        return self._event_queue.qsize()


# ============================================
# Event Handlers (Consumers)
# ============================================

def handle_book_borrowed(event: dict):
    """
    Handler for book.borrowed event.
    In real app, this could: send email, update analytics, notify other services, etc.
    """
    data = event.get('data', {})
    logger.info("Processing book.borrowed event", extra={
        'event_id': event['id'],
        'book_key': data.get('book_key'),
        'title': data.get('title'),
        'action': 'send_notification'
    })
    # Simulate async processing (e.g., sending email)
    time.sleep(0.1)
    print(f"[EVENT CONSUMER] Book borrowed notification sent for: {data.get('title', 'Unknown')}")


def handle_book_returned(event: dict):
    """
    Handler for book.returned event.
    """
    data = event.get('data', {})
    logger.info("Processing book.returned event", extra={
        'event_id': event['id'],
        'book_key': data.get('book_key'),
        'action': 'update_inventory'
    })
    # Simulate async processing
    time.sleep(0.1)
    print(f"[EVENT CONSUMER] Book returned, inventory updated for: {data.get('book_key', 'Unknown')}")


def handle_analytics(event: dict):
    """
    Generic analytics handler - subscribes to multiple event types.
    """
    logger.info("Analytics event received", extra={
        'event_id': event['id'],
        'event_type': event['type'],
        'timestamp': event['timestamp']
    })
    print(f"[ANALYTICS] Event tracked: {event['type']} at {event['timestamp']}")


# ============================================
# Global Event Bus Instance
# ============================================

# Create singleton event bus
event_bus = EventBus()

# Register default handlers
event_bus.subscribe('book.borrowed', handle_book_borrowed)
event_bus.subscribe('book.borrowed', handle_analytics)  # Multiple handlers per event
event_bus.subscribe('book.returned', handle_book_returned)
event_bus.subscribe('book.returned', handle_analytics)

# Start the event bus worker
event_bus.start()
