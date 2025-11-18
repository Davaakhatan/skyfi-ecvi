"""Tests for security utilities"""

import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token
)
from app.utils.security import (
    validate_password_strength,
    validate_secret_key,
    sanitize_html,
    validate_url,
    generate_secure_token
)


class TestSecurityUtils:
    """Test security utility functions"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        
        # Verify password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_create_access_token(self):
        """Test creating JWT access token"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        # JWT tokens have 3 parts separated by dots
        assert len(token.split(".")) == 3
    
    def test_validate_password_strength(self):
        """Test password strength validation"""
        # Valid password
        valid, error = validate_password_strength("Test123!@#")
        assert valid is True
        assert error is None
        
        # Too short
        valid, error = validate_password_strength("Test1!")
        assert valid is False
        assert "8 characters" in error
        
        # Missing uppercase
        valid, error = validate_password_strength("test123!@#")
        assert valid is False
        assert "uppercase" in error
        
        # Missing lowercase
        valid, error = validate_password_strength("TEST123!@#")
        assert valid is False
        assert "lowercase" in error
        
        # Missing digit
        valid, error = validate_password_strength("TestPass!@#")
        assert valid is False
        assert "digit" in error
        
        # Missing special character
        valid, error = validate_password_strength("TestPass123")
        assert valid is False
        assert "special" in error
    
    def test_validate_secret_key(self):
        """Test secret key validation"""
        # Valid key
        valid, error = validate_secret_key("a" * 32)
        assert valid is True
        
        # Too short
        valid, error = validate_secret_key("short")
        assert valid is False
        assert "32 characters" in error
    
    def test_sanitize_html(self):
        """Test HTML sanitization"""
        # XSS attempt
        malicious = "<script>alert('xss')</script>"
        sanitized = sanitize_html(malicious)
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized
    
    def test_validate_url(self):
        """Test URL validation"""
        # Valid URL
        valid, error = validate_url("https://example.com")
        assert valid is True
        
        # Invalid URL
        valid, error = validate_url("not-a-url")
        assert valid is False
        
        # Dangerous protocol
        valid, error = validate_url("javascript:alert('xss')")
        assert valid is False
        assert "Dangerous protocol" in error
    
    def test_generate_secure_token(self):
        """Test secure token generation"""
        token = generate_secure_token()
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Generate multiple tokens - should be different
        token2 = generate_secure_token()
        assert token != token2

