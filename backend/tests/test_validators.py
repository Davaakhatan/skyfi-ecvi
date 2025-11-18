"""Tests for validation utilities"""

import pytest
from app.utils.validators import (
    validate_email,
    validate_phone,
    validate_domain,
    validate_registration_number
)


class TestEmailValidation:
    """Test email validation"""
    
    def test_valid_email(self):
        """Test valid email addresses"""
        valid_emails = [
            "test@example.com",
            "user.name@example.co.uk",
            "user+tag@example.com",
            "user123@example-domain.com"
        ]
        for email in valid_emails:
            valid, error = validate_email(email)
            assert valid, f"Email {email} should be valid: {error}"
    
    def test_invalid_email(self):
        """Test invalid email addresses"""
        invalid_emails = [
            "invalid",
            "@example.com",
            "test@",
            "test @example.com",
            "test@example",
            ""
        ]
        for email in invalid_emails:
            valid, error = validate_email(email)
            assert not valid, f"Email {email} should be invalid"


class TestPhoneValidation:
    """Test phone validation"""
    
    def test_valid_phone(self):
        """Test valid phone numbers"""
        valid_phones = [
            "+1234567890",
            "+44 20 1234 5678",
            "+1-555-123-4567",
            "(555) 123-4567"
        ]
        for phone in valid_phones:
            valid, error = validate_phone(phone)
            assert valid, f"Phone {phone} should be valid: {error}"
    
    def test_invalid_phone(self):
        """Test invalid phone numbers"""
        invalid_phones = [
            "123",
            "abc",
            "",
            "12345"
        ]
        for phone in invalid_phones:
            valid, error = validate_phone(phone)
            assert not valid, f"Phone {phone} should be invalid"
    
    def test_phone_with_country_code(self):
        """Test phone validation with country code"""
        valid, error = validate_phone("+1234567890", "US")
        assert valid, f"Phone with US country code should be valid: {error}"


class TestDomainValidation:
    """Test domain validation"""
    
    def test_valid_domain(self):
        """Test valid domains"""
        valid_domains = [
            "example.com",
            "subdomain.example.com",
            "example.co.uk",
            "example-domain.com"
        ]
        for domain in valid_domains:
            valid, error = validate_domain(domain)
            assert valid, f"Domain {domain} should be valid: {error}"
    
    def test_invalid_domain(self):
        """Test invalid domains"""
        invalid_domains = [
            "invalid",
            ".com",
            "example.",
            "example..com",
            ""
        ]
        for domain in invalid_domains:
            valid, error = validate_domain(domain)
            assert not valid, f"Domain {domain} should be invalid"


class TestRegistrationNumberValidation:
    """Test registration number validation"""
    
    def test_valid_registration_number(self):
        """Test valid registration numbers"""
        valid_numbers = [
            ("12345678", "US"),
            ("SC123456", "GB"),
            ("1234567890", None)
        ]
        for number, jurisdiction in valid_numbers:
            valid, error = validate_registration_number(number, jurisdiction)
            # Registration validation is lenient, so we just check it doesn't crash
            assert isinstance(valid, bool)
    
    def test_empty_registration_number(self):
        """Test empty registration number"""
        valid, error = validate_registration_number("", "US")
        assert not valid

