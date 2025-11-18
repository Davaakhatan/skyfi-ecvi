"""Tests for registration verification service"""

import pytest
from app.services.registration_verification import RegistrationVerificationService


class TestRegistrationVerificationService:
    """Test RegistrationVerificationService"""
    
    def test_verify_registration_number_valid(self):
        """Test registration number verification with valid number"""
        service = RegistrationVerificationService()
        result = service.verify_registration_number("12345678", "US")
        
        assert "verified" in result
        assert isinstance(result["verified"], bool)
    
    def test_verify_registration_number_invalid_format(self):
        """Test registration number verification with invalid format"""
        service = RegistrationVerificationService()
        result = service.verify_registration_number("", "US")
        
        assert result["verified"] is False
        assert len(result.get("errors", [])) > 0
    
    def test_verify_address_valid(self):
        """Test address verification with valid address"""
        service = RegistrationVerificationService()
        result = service.verify_address(
            address="123 Main St",
            city="New York",
            state="NY",
            country="US",
            postal_code="10001"
        )
        
        assert "verified" in result
        assert "completeness_score" in result
    
    def test_verify_address_incomplete(self):
        """Test address verification with incomplete address"""
        service = RegistrationVerificationService()
        result = service.verify_address(
            address="123 Main St",
            city=None,
            state=None,
            country=None,
            postal_code=None
        )
        
        assert result["verified"] is False or result["completeness_score"] < 0.6
    
    def test_cross_reference_registration_data(self):
        """Test cross-referencing registration data"""
        service = RegistrationVerificationService()
        result = service.cross_reference_registration_data(
            legal_name="Test Company",
            registration_number="12345678",
            jurisdiction="US",
            domain="test.com"
        )
        
        assert "matches" in result
        assert "total_sources" in result
        assert isinstance(result["matches"], int)
        assert isinstance(result["total_sources"], int)

