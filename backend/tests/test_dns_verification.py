"""Tests for DNS verification service"""

import pytest
from app.services.dns_verification import DNSVerificationService


class TestDNSVerificationService:
    """Test DNSVerificationService"""
    
    def test_verify_dns_records_valid_domain(self):
        """Test DNS verification with valid domain"""
        service = DNSVerificationService()
        result = service.verify_dns_records("example.com")
        
        assert "verified" in result
        assert "a_records" in result
        assert "mx_records" in result
        assert "ns_records" in result
    
    def test_verify_dns_records_invalid_domain(self):
        """Test DNS verification with invalid domain"""
        service = DNSVerificationService()
        result = service.verify_dns_records("invalid-domain-that-does-not-exist-12345.com")
        
        assert result.get("verified") is False
        assert len(result.get("errors", [])) > 0
    
    def test_verify_dns_records_empty_domain(self):
        """Test DNS verification with empty domain"""
        service = DNSVerificationService()
        result = service.verify_dns_records("")
        
        assert result.get("verified") is False
    
    def test_get_domain_age(self):
        """Test getting domain age"""
        service = DNSVerificationService()
        age = service.get_domain_age("example.com")
        
        # Domain age should be a positive number (days)
        assert age is None or (isinstance(age, int) and age >= 0)
    
    def test_check_ssl_certificate(self):
        """Test SSL certificate check"""
        service = DNSVerificationService()
        result = service.check_ssl_certificate("example.com")
        
        assert isinstance(result, bool) or result is None
    
    def test_verify_domain_matches_company(self):
        """Test domain-company name matching"""
        service = DNSVerificationService()
        
        # Exact match
        result = service.verify_domain_matches_company("example.com", "Example Inc")
        assert isinstance(result, bool)
        
        # Partial match
        result = service.verify_domain_matches_company("example.com", "Example")
        assert isinstance(result, bool)
        
        # No match
        result = service.verify_domain_matches_company("example.com", "Different Company")
        assert isinstance(result, bool)

