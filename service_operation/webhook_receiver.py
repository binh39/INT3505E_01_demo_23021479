"""
Webhook Receiver Service
=========================
Dịch vụ đơn giản để nhận và xử lý webhook events.
Chạy trên port 5001 để nhận events từ ứng dụng chính (port 5000).
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

# Lưu trữ các events đã nhận (trong memory)
received_events = []


@app.route('/webhook/books', methods=['POST'])
def receive_book_event():
    """
    Endpoint nhận webhook events liên quan đến sách.
    Ví dụ: mượn sách, trả sách, thêm sách mới.
    """
    data = request.get_json()
    
    event = {
        'received_at': datetime.now().isoformat(),
        'source': request.headers.get('X-Webhook-Source', 'unknown'),
        'event_type': data.get('event_type', 'unknown'),
        'payload': data
    }
    
    received_events.append(event)
    
    # In ra console để theo dõi
    print("\n" + "=" * 50)
    print("WEBHOOK RECEIVED - /webhook/books")
    print("=" * 50)
    print(f"Time: {event['received_at']}")
    print(f"Source: {event['source']}")
    print(f"Event Type: {event['event_type']}")
    print(f"Payload: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print("=" * 50 + "\n")
    
    return jsonify({
        'status': 'received',
        'message': f"Event '{event['event_type']}' processed successfully",
        'event_id': len(received_events)
    }), 200


@app.route('/webhook/notifications', methods=['POST'])
def receive_notification():
    """
    Endpoint nhận các thông báo chung.
    """
    data = request.get_json()
    
    event = {
        'received_at': datetime.now().isoformat(),
        'type': 'notification',
        'payload': data
    }
    
    received_events.append(event)
    
    # In ra console
    print("\n" + "-" * 50)
    print("NOTIFICATION RECEIVED - /webhook/notifications")
    print("-" * 50)
    print(f"Time: {event['received_at']}")
    print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print("-" * 50 + "\n")
    
    return jsonify({
        'status': 'received',
        'message': 'Notification processed'
    }), 200


@app.route('/webhook/events', methods=['GET'])
def list_events():
    """
    Xem danh sách tất cả events đã nhận.
    """
    return jsonify({
        'total_events': len(received_events),
        'events': received_events[-20:]  # Chỉ trả về 20 events gần nhất
    })


@app.route('/webhook/events/clear', methods=['POST'])
def clear_events():
    """
    Xóa tất cả events đã lưu.
    """
    count = len(received_events)
    received_events.clear()
    
    print("[INFO] All events cleared")
    
    return jsonify({
        'status': 'cleared',
        'events_removed': count
    })


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'webhook-receiver',
        'port': 5001,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  WEBHOOK RECEIVER SERVICE")
    print("  Listening on http://localhost:5001")
    print("=" * 60)
    print("\nEndpoints:")
    print("  POST /webhook/books         - Nhận events về sách")
    print("  POST /webhook/notifications - Nhận thông báo chung")
    print("  GET  /webhook/events        - Xem danh sách events đã nhận")
    print("  POST /webhook/events/clear  - Xóa tất cả events")
    print("  GET  /health                - Health check")
    print("\n" + "=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
