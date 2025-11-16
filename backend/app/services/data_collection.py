"""Data collection service with retry mechanisms, caching, and source attribution"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import time
import hashlib
import json

import httpx
from redis import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class DataCollectionService:
    """Service for collecting company data from multiple sources with retry and caching"""
    
    def __init__(self, redis_client: Optional[Redis] = None):
        self.redis_client = redis_client
        self.cache_ttl = 3600  # 1 hour default cache TTL
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    def _get_cache_key(self, source: str, query: str) -> str:
        """Generate cache key for query"""
        key_data = f"{source}:{query}"
        return f"data_collection:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get data from cache"""
        if not self.redis_client:
            return None
        
        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                if isinstance(cached, bytes):
                    cached = cached.decode('utf-8')
                return json.loads(cached)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Cache read failed - invalid data format: {e}")
        except Exception as e:
            logger.warning(f"Cache read failed: {e}")
        return None
    
    def _set_cache(self, cache_key: str, data: Dict, ttl: int = None):
        """Store data in cache"""
        if not self.redis_client:
            return
        
        try:
            ttl = ttl or self.cache_ttl
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(data)
            )
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")
    
    def _retry_request(
        self,
        func,
        *args,
        max_retries: int = None,
        retry_delay: int = None,
        **kwargs
    ) -> Optional[Any]:
        """Execute function with exponential backoff retry"""
        max_retries = max_retries or self.max_retries
        retry_delay = retry_delay or self.retry_delay
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Request failed after {max_retries} attempts: {e}")
                    raise
                
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
        
        return None
    
    def collect_from_api(
        self,
        source: str,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Collect data from an API endpoint with caching and retry
        
        Args:
            source: Source name for attribution
            endpoint: API endpoint URL
            params: Query parameters
            headers: Request headers
            use_cache: Whether to use cache
        
        Returns:
            Dictionary with collected data and metadata
        """
        # Generate cache key
        cache_key = self._get_cache_key(source, f"{endpoint}:{json.dumps(params or {})}")
        
        # Check cache
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                logger.info(f"Cache hit for {source}: {endpoint}")
                return {
                    **cached,
                    "cached": True
                }
        
        # Make API request with retry
        try:
            response = self._retry_request(
                self._make_api_request,
                endpoint,
                params=params,
                headers=headers
            )
            
            if response:
                result = {
                    "success": True,
                    "data": response,
                    "source": source,
                    "collected_at": datetime.utcnow().isoformat(),
                    "cached": False
                }
                
                # Cache result
                if use_cache:
                    self._set_cache(cache_key, result)
                
                return result
            else:
                return {
                    "success": False,
                    "error": "Request failed",
                    "source": source
                }
        except Exception as e:
            logger.error(f"API collection failed for {source}: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": source
            }
    
    def _make_api_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP API request with timeout and error handling"""
        try:
            # Validate URL
            from app.utils.security import validate_url
            url_valid, url_error = validate_url(endpoint)
            if not url_valid:
                raise ValueError(f"Invalid endpoint URL: {url_error}")
            
            with httpx.Client(
                timeout=httpx.Timeout(30.0, connect=10.0),  # 30s total, 10s connect
                follow_redirects=True,
                max_redirects=5
            ) as client:
                response = client.get(
                    endpoint,
                    params=params or {},
                    headers=headers or {}
                )
                response.raise_for_status()
                
                # Validate response size (prevent memory issues)
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
                    raise ValueError("Response too large (max 10MB)")
                
                return response.json()
        except httpx.TimeoutException:
            logger.error(f"Request timeout for endpoint: {endpoint}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for endpoint: {endpoint}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error for endpoint {endpoint}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error making API request to {endpoint}: {e}")
            raise
    
    def collect_from_multiple_sources(
        self,
        sources: List[Dict[str, Any]],
        query: str
    ) -> Dict[str, Any]:
        """
        Collect data from multiple sources in parallel
        
        Args:
            sources: List of source configurations
            query: Query string
        
        Returns:
            Dictionary with aggregated results from all sources
        """
        results = []
        
        for source_config in sources:
            source_name = source_config.get("name", "unknown")
            source_type = source_config.get("type", "api")
            
            if source_type == "api":
                result = self.collect_from_api(
                    source=source_name,
                    endpoint=source_config.get("endpoint"),
                    params=source_config.get("params", {}),
                    headers=source_config.get("headers", {}),
                    use_cache=source_config.get("use_cache", True)
                )
                results.append(result)
            # TODO: Add support for other source types (web scraping, database, etc.)
        
        # Aggregate results
        successful_results = [r for r in results if r.get("success")]
        failed_results = [r for r in results if not r.get("success")]
        
        return {
            "success": len(successful_results) > 0,
            "results": results,
            "successful_sources": [r["source"] for r in successful_results],
            "failed_sources": [r["source"] for r in failed_results],
            "total_sources": len(sources),
            "collected_at": datetime.utcnow().isoformat()
        }
    
    def calculate_source_reliability(self, source: str, historical_data: List[Dict]) -> float:
        """
        Calculate reliability score for a data source based on historical accuracy
        
        Args:
            source: Source name
            historical_data: List of historical verification results
        
        Returns:
            Reliability score (0.0 to 1.0)
        """
        if not historical_data:
            return 0.5  # Default reliability for unknown sources
        
        # Calculate reliability based on:
        # - Success rate
        # - Data accuracy (if available)
        # - Consistency across time
        
        successful = sum(1 for d in historical_data if d.get("success", False))
        total = len(historical_data)
        
        if total == 0:
            return 0.5
        
        success_rate = successful / total
        
        # TODO: Factor in data accuracy and consistency
        # For now, use success rate as reliability
        return success_rate
    
    def attribute_sources(self, collected_data: Dict) -> Dict[str, Any]:
        """
        Add source attribution to collected data
        
        Args:
            collected_data: Dictionary with collected data
        
        Returns:
            Dictionary with source attribution added
        """
        attributed_data = {
            **collected_data,
            "source_attribution": {}
        }
        
        # Add source information to each data point
        if "results" in collected_data:
            for result in collected_data["results"]:
                source = result.get("source", "unknown")
                data = result.get("data", {})
                
                for key, value in data.items():
                    if key not in attributed_data["source_attribution"]:
                        attributed_data["source_attribution"][key] = []
                    
                    attributed_data["source_attribution"][key].append({
                        "source": source,
                        "value": value,
                        "collected_at": result.get("collected_at")
                    })
        
        return attributed_data

