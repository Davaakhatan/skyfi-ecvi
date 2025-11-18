"""Tests for data collection service"""

import pytest
from app.services.data_collection import DataCollectionService


class TestDataCollectionService:
    """Test DataCollectionService"""
    
    def test_get_from_cache(self):
        """Test getting data from cache"""
        service = DataCollectionService()
        
        # Without Redis, should return None
        result = service._get_from_cache("test_key")
        assert result is None
    
    def test_set_cache(self):
        """Test setting cache"""
        service = DataCollectionService()
        
        # Without Redis, should not crash
        service._set_cache("test_key", {"data": "test"})
        # Should complete without error
    
    def test_get_cache_key(self):
        """Test generating cache key"""
        service = DataCollectionService()
        
        key = service._get_cache_key("source", "query")
        assert isinstance(key, str)
        assert "data_collection:" in key
    
    def test_retry_request(self):
        """Test retry mechanism"""
        service = DataCollectionService()
        
        # Test successful function
        def success_func():
            return "success"
        
        result = service._retry_request(success_func)
        assert result == "success"
        
        # Test failing function (will fail after retries)
        call_count = [0]
        def fail_func():
            call_count[0] += 1
            raise Exception("Test error")
        
        result = service._retry_request(fail_func, max_retries=2)
        assert result is None
        assert call_count[0] == 2

