from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# HTTP metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)
IN_PROGRESS = Gauge(
    'inprogress_requests',
    'Number of requests in progress'
)

# Application/business metrics
BOOKS_BORROWED = Counter('books_borrowed_total', 'Total number of books borrowed')
BOOKS_RETURNED = Counter('books_returned_total', 'Total number of books returned')

# Error metrics
ERRORS = Counter('errors_total', 'Total number of errors', ['type'])

# Helper to expose metrics (used by Flask route)
def metrics_response():
    data = generate_latest()
    return data, CONTENT_TYPE_LATEST
