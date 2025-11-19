"""Prometheus metrics middleware"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import time

# HTTP request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# Active requests gauge
http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently in progress',
    ['method', 'endpoint']
)

# Database connection pool metrics
db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections'
)

db_connections_idle = Gauge(
    'db_connections_idle',
    'Idle database connections'
)

# Celery task metrics
celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total Celery tasks',
    ['task_name', 'status']
)

celery_task_duration_seconds = Histogram(
    'celery_task_duration_seconds',
    'Celery task duration in seconds',
    ['task_name'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0, 1200.0]
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip metrics endpoint
        if request.url.path == "/metrics":
            return await call_next(request)
        
        # Get endpoint path (normalize to avoid high cardinality)
        endpoint = self._normalize_path(request.url.path)
        method = request.method
        
        # Increment in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
        
        start_time = time.time()
        status_code = 500
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as e:
            status_code = 500
            raise
        finally:
            # Calculate duration
            duration = time.time() - start_time
            
            # Decrement in-progress requests
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
            
            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path to avoid high cardinality in metrics"""
        # Replace UUIDs and IDs with placeholders
        import re
        # Replace UUIDs
        path = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '{id}', path)
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        return path


def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest()

