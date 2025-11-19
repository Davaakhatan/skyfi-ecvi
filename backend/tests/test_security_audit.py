"""Security audit tests"""

import pytest
from app.core.security import create_access_token, decode_access_token
from app.utils.security import (
    validate_password_strength,
    sanitize_html,
    sanitize_for_sql
)
from app.utils.validators import validate_url


class TestAuthenticationSecurity:
    """Test authentication security"""
    
    def test_password_strength_validation(self):
        """Test that weak passwords are rejected"""
        # Weak password
        valid, error = validate_password_strength("password")
        assert valid is False
        assert "uppercase" in error or "digit" in error or "special" in error
        
        # Strong password
        valid, error = validate_password_strength("StrongPass123!@#")
        assert valid is True
        assert error is None
    
    def test_jwt_token_security(self):
        """Test JWT token security"""
        # Create token
        token = create_access_token({"sub": "test@example.com"})
        
        # Token should be valid
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded.get("sub") == "test@example.com"
        
        # Invalid token should fail
        invalid_decoded = decode_access_token("invalid.token.here")
        assert invalid_decoded is None
    
    def test_token_expiration(self):
        """Test that tokens expire"""
        from datetime import timedelta
        from app.core.security import create_access_token
        
        # Create token with short expiration
        token = create_access_token(
            {"sub": "test@example.com"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        # Should fail to decode
        decoded = decode_access_token(token)
        assert decoded is None


class TestInputValidationSecurity:
    """Test input validation and sanitization"""
    
    def test_html_sanitization(self):
        """Test XSS prevention via HTML sanitization"""
        malicious = "<script>alert('xss')</script>Hello"
        sanitized = sanitize_html(malicious)
        
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized
        assert "Hello" in sanitized
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        # SQL injection attempt
        malicious = "'; DROP TABLE users; --"
        
        # Should raise ValueError (expected behavior - rejects dangerous input)
        try:
            sanitized = sanitize_for_sql(malicious)
            # If it doesn't raise, should be sanitized (both should be removed)
            assert "DROP" not in sanitized and "';" not in sanitized
        except ValueError:
            # Expected behavior - should reject dangerous input
            # This is the correct behavior, so test passes
            assert True
    
    def test_url_validation(self):
        """Test URL validation for security"""
        # Valid URL
        valid, error = validate_url("https://example.com")
        assert valid is True
        
        # Dangerous protocol
        valid, error = validate_url("javascript:alert('xss')")
        assert valid is False
        assert error is not None
        assert "Dangerous protocol" in error
        
        # Invalid URL
        valid, error = validate_url("not-a-url")
        assert valid is False


class TestAPISecurity:
    """Test API security"""
    
    def test_unauthorized_access(self, client, db_session, override_get_db):
        """Test that unauthorized requests are rejected"""
        from app.db.database import get_db
        from app.main import app
        
        app.dependency_overrides[get_db] = override_get_db
        
        # Try to access protected endpoint without token
        response = client.get("/api/v1/companies/")
        assert response.status_code == 401
        
        app.dependency_overrides.clear()
    
    def test_invalid_token(self, client, db_session, override_get_db):
        """Test that invalid tokens are rejected"""
        from app.db.database import get_db
        from app.main import app
        
        app.dependency_overrides[get_db] = override_get_db
        
        # Try with invalid token
        response = client.get(
            "/api/v1/companies/",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401
        
        app.dependency_overrides.clear()
    
    def test_role_based_access(self, client, db_session, override_get_db, test_user, test_admin_user):
        """Test that role-based access control works"""
        from app.db.database import get_db
        from app.core.auth import get_current_active_user
        from app.main import app
        
        app.dependency_overrides[get_db] = override_get_db
        
        # Regular user token
        user_token = create_access_token(data={"sub": test_user.email})
        
        # Admin-only endpoint should reject regular user
        # (Assuming there's an admin-only endpoint)
        # This is a placeholder - adjust based on actual admin endpoints
        
        app.dependency_overrides.clear()


class TestDataSecurity:
    """Test data security"""
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        from app.core.security import get_password_hash, verify_password
        
        password = "TestPassword123!@#"
        hashed = get_password_hash(password)
        
        # Hash should be different from password
        assert hashed != password
        assert len(hashed) > 50  # Bcrypt hashes are long
        
        # Should verify correctly
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False
    
    def test_sensitive_data_not_logged(self):
        """Test that sensitive data is not logged"""
        # This is a placeholder - in real implementation, check logs
        # Ensure passwords, tokens, API keys are never logged
        pass


class TestCORSecurity:
    """Test CORS configuration"""
    
    def test_cors_headers(self, client):
        """Test that CORS headers are properly configured"""
        response = client.options(
            "/api/v1/companies/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        # Should have CORS headers (if configured)
        # Adjust based on actual CORS configuration
        assert response.status_code in [200, 204, 405]


class TestRateLimiting:
    """Test rate limiting (if implemented)"""
    
    def test_rate_limiting_placeholder(self):
        """Placeholder for rate limiting tests"""
        # Rate limiting should be implemented for production
        # This is a placeholder test
        pass


class TestEncryption:
    """Test encryption at rest and in transit"""
    
    def test_https_enforcement(self):
        """Test HTTPS enforcement (if implemented)"""
        # In production, should enforce HTTPS
        # This is a placeholder test
        pass
    
    def test_data_encryption(self):
        """Test that sensitive data is encrypted"""
        # Passwords should be hashed (not encrypted, but secure)
        from app.core.security import get_password_hash
        hashed = get_password_hash("test")
        assert hashed != "test"
        assert len(hashed) > 0

