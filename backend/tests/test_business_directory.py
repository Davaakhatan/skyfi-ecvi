"""Tests for business directory service"""

import pytest
from app.services.business_directory import BusinessDirectoryService


class TestBusinessDirectoryService:
    """Test BusinessDirectoryService"""
    
    def test_search_opencorporates(self):
        """Test OpenCorporates search"""
        service = BusinessDirectoryService()
        result = service.search_opencorporates("Example Company", "US")
        
        assert isinstance(result, dict)
        assert "success" in result
        # May return empty results if API not configured, but should not crash
    
    def test_search_crunchbase(self):
        """Test Crunchbase search"""
        service = BusinessDirectoryService()
        result = service.search_crunchbase("Example Company")
        
        assert isinstance(result, dict)
        assert "success" in result
    
    def test_search_google_business(self):
        """Test Google Business Profile search"""
        service = BusinessDirectoryService()
        result = service.search_google_business("Example Company", "New York")
        
        assert isinstance(result, dict)
        assert "success" in result
    
    def test_search_yelp_business(self):
        """Test Yelp Business search"""
        service = BusinessDirectoryService()
        result = service.search_yelp("Example Company", "New York")
        
        assert isinstance(result, dict)
        assert "success" in result
    
    def test_search_all_directories(self):
        """Test searching all business directory sources"""
        service = BusinessDirectoryService()
        result = service.search_all_directories("Example Company", "US", "New York")
        
        assert isinstance(result, dict)
        assert "sources" in result or "results" in result

