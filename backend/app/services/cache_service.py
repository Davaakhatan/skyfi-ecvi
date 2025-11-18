"""Centralized caching service for performance optimization"""

import json
import logging
from typing import Optional, Any, Dict
from functools import wraps
from datetime import timedelta
import hashlib

from redis import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Centralized caching service using Redis"""
    
    def __init__(self, redis_client: Optional[Redis] = None):
        """
        Initialize cache service
        
        Args:
            redis_client: Optional Redis client. If None, will try to connect using settings.
        """
        self.redis_client = redis_client
        self.default_ttl = 3600  # 1 hour default
        self._connect()
    
    def _connect(self):
        """Connect to Redis if not already connected"""
        if self.redis_client is None:
            try:
                if settings.REDIS_URL:
                    import redis
                    self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
                    # Test connection
                    self.redis_client.ping()
                    logger.info("Connected to Redis cache")
                else:
                    logger.warning("REDIS_URL not configured - caching disabled")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e} - caching disabled")
                self.redis_client = None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments"""
        key_parts = [prefix]
        if args:
            key_parts.extend(str(arg) for arg in args)
        if kwargs:
            # Sort kwargs for consistent key generation
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend(f"{k}:{v}" for k, v in sorted_kwargs)
        
        key_string = ":".join(key_parts)
        # Hash long keys to avoid Redis key length issues
        if len(key_string) > 250:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:hash:{key_hash}"
        return key_string
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.redis_client:
            return None
        
        try:
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Cache read error for key {key}: {e}")
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (default: self.default_ttl)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except (TypeError, ValueError) as e:
            logger.warning(f"Cache set error (serialization): {e}")
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
        
        return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern
        
        Args:
            pattern: Redis key pattern (e.g., "company:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern error: {e}")
            return 0
    
    def invalidate_company_cache(self, company_id: str):
        """Invalidate all cache entries for a company"""
        patterns = [
            f"company:{company_id}:*",
            f"verification:{company_id}:*",
            f"report:{company_id}:*",
            f"risk:{company_id}:*"
        ]
        total_deleted = 0
        for pattern in patterns:
            total_deleted += self.delete_pattern(pattern)
        logger.info(f"Invalidated {total_deleted} cache entries for company {company_id}")
    
    def get_or_set(self, key: str, func, ttl: Optional[int] = None, *args, **kwargs) -> Any:
        """
        Get value from cache, or compute and cache it if not found
        
        Args:
            key: Cache key
            func: Function to call if cache miss
            ttl: Time to live in seconds
            *args, **kwargs: Arguments to pass to func
            
        Returns:
            Cached or computed value
        """
        # Try to get from cache
        cached = self.get(key)
        if cached is not None:
            return cached
        
        # Compute value
        value = func(*args, **kwargs)
        
        # Cache it
        self.set(key, value, ttl)
        
        return value


# Global cache service instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get global cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def cache_result(prefix: str, ttl: int = 3600):
    """
    Decorator to cache function results
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
        
    Example:
        @cache_result("company", ttl=1800)
        def get_company(company_id: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_service()
            cache_key = cache._generate_key(prefix, *args, **kwargs)
            
            # Try cache first
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

