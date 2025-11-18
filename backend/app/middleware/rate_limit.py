"""Rate limiting middleware (placeholder for production implementation)"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Dict, Tuple
from datetime import datetime, timedelta
import time


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware
    
    Note: For production, use Redis-based rate limiting (e.g., slowapi, fastapi-limiter)
    This is a basic implementation for development/testing.
    """
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.rate_limit_store: Dict[str, list] = {}  # {ip: [timestamps]}
        self.cleanup_interval = 300  # Clean up old entries every 5 minutes
        self.last_cleanup = time.time()
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded IP (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _cleanup_old_entries(self):
        """Remove old rate limit entries"""
        current_time = time.time()
        cutoff = current_time - 60  # Keep last minute
        
        for ip in list(self.rate_limit_store.keys()):
            self.rate_limit_store[ip] = [
                ts for ts in self.rate_limit_store[ip] if ts > cutoff
            ]
            if not self.rate_limit_store[ip]:
                del self.rate_limit_store[ip]
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        # Cleanup old entries periodically
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries()
            self.last_cleanup = current_time
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        current_time = time.time()
        cutoff = current_time - 60  # Last minute
        
        if client_ip in self.rate_limit_store:
            # Filter timestamps from last minute
            self.rate_limit_store[client_ip] = [
                ts for ts in self.rate_limit_store[client_ip] if ts > cutoff
            ]
            
            # Check if over limit
            if len(self.rate_limit_store[client_ip]) >= self.requests_per_minute:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
                )
        
        # Add current request timestamp
        if client_ip not in self.rate_limit_store:
            self.rate_limit_store[client_ip] = []
        self.rate_limit_store[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.requests_per_minute - len(self.rate_limit_store[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))
        
        return response

