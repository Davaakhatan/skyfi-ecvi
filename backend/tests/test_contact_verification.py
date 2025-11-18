"""Tests for contact verification service"""

import pytest
from uuid import uuid4
from app.services.contact_verification import ContactVerificationService
from app.services.contact_verification_enhanced import EnhancedContactVerificationService


class TestContactVerificationService:
    """Test ContactVerificationService"""
    
    def test_verify_email_valid(self):
        """Test email verification with valid email"""
        result = ContactVerificationService.verify_email("test@example.com")
        assert result["email"] == "test@example.com"
        assert result["format_valid"] is True
    
    def test_verify_email_invalid_format(self):
        """Test email verification with invalid format"""
        result = ContactVerificationService.verify_email("invalid-email")
        assert result["format_valid"] is False
        assert len(result["errors"]) > 0
    
    def test_verify_email_empty(self):
        """Test email verification with empty string"""
        result = ContactVerificationService.verify_email("")
        assert result["format_valid"] is False
        assert "Email is required" in result["errors"]
    
    def test_verify_phone_valid(self):
        """Test phone verification with valid phone"""
        result = ContactVerificationService.verify_phone("+1234567890")
        assert result["phone"] == "+1234567890"
        assert result["format_valid"] is True
    
    def test_verify_phone_invalid_format(self):
        """Test phone verification with invalid format"""
        result = ContactVerificationService.verify_phone("123")
        assert result["format_valid"] is False
        assert len(result["errors"]) > 0
    
    def test_verify_phone_empty(self):
        """Test phone verification with empty string"""
        result = ContactVerificationService.verify_phone("")
        assert result["format_valid"] is False
        assert "Phone number is required" in result["errors"]
    
    def test_verify_phone_suspicious_pattern(self):
        """Test phone verification with suspicious pattern"""
        result = ContactVerificationService.verify_phone("1111111111")
        assert result["format_valid"] is True  # Format might be valid
        assert result["carrier_valid"] is False  # But carrier invalid
    
    def test_verify_contact_info_email_only(self):
        """Test contact info verification with email only"""
        result = ContactVerificationService.verify_contact_info(email="test@example.com")
        assert result["has_email"] is True
        assert result["has_phone"] is False
        assert result["email_result"] is not None
    
    def test_verify_contact_info_phone_only(self):
        """Test contact info verification with phone only"""
        result = ContactVerificationService.verify_contact_info(phone="+1234567890")
        assert result["has_email"] is False
        assert result["has_phone"] is True
        assert result["phone_result"] is not None
    
    def test_verify_contact_info_both(self):
        """Test contact info verification with both email and phone"""
        result = ContactVerificationService.verify_contact_info(
            email="test@example.com",
            phone="+1234567890"
        )
        assert result["has_email"] is True
        assert result["has_phone"] is True
        assert result["email_result"] is not None
        assert result["phone_result"] is not None


class TestEnhancedContactVerificationService:
    """Test EnhancedContactVerificationService"""
    
    def test_verify_and_store_email(self, db_session, test_company):
        """Test email verification and storage"""
        service = EnhancedContactVerificationService(db_session)
        result = service.verify_and_store_email(
            company_id=test_company.id,
            verification_result_id=None,
            email="test@example.com"
        )
        assert result.company_id == test_company.id
        assert result.contact_type.value == "EMAIL"
        assert result.contact_value == "test@example.com"
        assert result.format_valid is True
    
    def test_verify_and_store_phone(self, db_session, test_company):
        """Test phone verification and storage"""
        service = EnhancedContactVerificationService(db_session)
        result = service.verify_and_store_phone(
            company_id=test_company.id,
            verification_result_id=None,
            phone="+1234567890",
            country_code="US"
        )
        assert result.company_id == test_company.id
        assert result.contact_type.value == "PHONE"
        assert result.contact_value == "+1234567890"
        assert result.format_valid is True
    
    def test_verify_and_store_name(self, db_session, test_company):
        """Test name verification and storage"""
        service = EnhancedContactVerificationService(db_session)
        result = service.verify_and_store_name(
            company_id=test_company.id,
            verification_result_id=None,
            name="John Doe"
        )
        assert result.company_id == test_company.id
        assert result.contact_type.value == "NAME"
        assert result.contact_value == "John Doe"
        assert result.format_valid is True
    
    def test_get_contact_verifications(self, db_session, test_company):
        """Test retrieving contact verifications"""
        service = EnhancedContactVerificationService(db_session)
        
        # Create some verifications
        service.verify_and_store_email(
            company_id=test_company.id,
            verification_result_id=None,
            email="test@example.com"
        )
        service.verify_and_store_phone(
            company_id=test_company.id,
            verification_result_id=None,
            phone="+1234567890"
        )
        
        # Retrieve verifications
        verifications = service.get_contact_verifications(company_id=test_company.id)
        assert len(verifications) == 2
        assert any(v.contact_type.value == "EMAIL" for v in verifications)
        assert any(v.contact_type.value == "PHONE" for v in verifications)
    
    def test_calculate_email_confidence(self, db_session):
        """Test email confidence calculation"""
        service = EnhancedContactVerificationService(db_session)
        
        # High confidence case
        result = {
            "format_valid": True,
            "domain_exists": True,
            "mx_record_exists": True,
            "email_exists": True
        }
        confidence = service._calculate_email_confidence(result)
        assert confidence >= 0.8
        
        # Low confidence case
        result = {
            "format_valid": True,
            "domain_exists": False,
            "mx_record_exists": False,
            "email_exists": None
        }
        confidence = service._calculate_email_confidence(result)
        assert confidence < 0.5
    
    def test_calculate_phone_confidence(self, db_session):
        """Test phone confidence calculation"""
        service = EnhancedContactVerificationService(db_session)
        
        # High confidence case
        result = {
            "format_valid": True,
            "carrier_valid": True,
            "line_type": "mobile"
        }
        confidence = service._calculate_phone_confidence(result)
        assert confidence >= 0.8
        
        # Low confidence case
        result = {
            "format_valid": True,
            "carrier_valid": None,
            "line_type": None
        }
        confidence = service._calculate_phone_confidence(result)
        assert confidence < 0.5
    
    def test_determine_email_status(self, db_session):
        """Test email status determination"""
        service = EnhancedContactVerificationService(db_session)
        
        # Verified status
        result = {
            "format_valid": True,
            "domain_exists": True,
            "mx_record_exists": True,
            "email_exists": True
        }
        status = service._determine_email_status(result)
        assert status.value == "VERIFIED"
        
        # Partial status
        result = {
            "format_valid": True,
            "domain_exists": True,
            "mx_record_exists": True,
            "email_exists": None
        }
        status = service._determine_email_status(result)
        assert status.value == "PARTIAL"
        
        # Failed status
        result = {
            "format_valid": False,
            "domain_exists": False,
            "mx_record_exists": False,
            "email_exists": None
        }
        status = service._determine_email_status(result)
        assert status.value == "FAILED"
    
    def test_determine_phone_status(self, db_session):
        """Test phone status determination"""
        service = EnhancedContactVerificationService(db_session)
        
        # Verified status
        result = {
            "format_valid": True,
            "carrier_valid": True
        }
        status = service._determine_phone_status(result)
        assert status.value == "VERIFIED"
        
        # Partial status
        result = {
            "format_valid": True,
            "carrier_valid": None
        }
        status = service._determine_phone_status(result)
        assert status.value == "PARTIAL"
        
        # Failed status
        result = {
            "format_valid": False,
            "carrier_valid": None
        }
        status = service._determine_phone_status(result)
        assert status.value == "FAILED"

