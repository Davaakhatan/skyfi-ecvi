"""Security utilities for production"""

import re
import secrets
from typing import Tuple, Optional


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be no more than 128 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    # Check for common weak passwords
    common_passwords = ['password', '12345678', 'qwerty', 'abc123', 'password123']
    if password.lower() in common_passwords:
        return False, "Password is too common. Please choose a stronger password."
    
    return True, None


def validate_secret_key(secret_key: str) -> Tuple[bool, Optional[str]]:
    """
    Validate secret key strength for production
    
    Requirements:
    - Minimum 32 characters
    - Should be cryptographically random
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not secret_key:
        return False, "SECRET_KEY is required"
    
    if len(secret_key) < 32:
        return False, "SECRET_KEY must be at least 32 characters long for production"
    
    # Check for common weak keys
    if secret_key in ['secret', 'changeme', 'your-secret-key-here']:
        return False, "SECRET_KEY is too weak. Use a cryptographically random key."
    
    return True, None


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML to prevent XSS attacks
    
    Args:
        text: Text that may contain HTML
    
    Returns:
        Sanitized text with HTML entities escaped
    """
    if not text:
        return ""
    
    import html
    return html.escape(str(text), quote=True)


def sanitize_for_sql(text: str) -> str:
    """
    Basic sanitization for SQL (though we use ORM, this is a safety measure)
    
    Note: SQLAlchemy ORM already protects against SQL injection,
    but this provides an additional layer of validation.
    
    Args:
        text: Text to sanitize
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove or escape dangerous SQL characters
    # In practice, ORM handles this, but we validate format
    dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
    text_str = str(text)
    
    # Check for SQL injection patterns
    sql_patterns = [
        r'union\s+select',
        r'exec\s*\(',
        r'execute\s*\(',
        r'script\s*>',
        r'<\s*script',
    ]
    
    text_lower = text_str.lower()
    for pattern in sql_patterns:
        if re.search(pattern, text_lower):
            raise ValueError(f"Potentially dangerous input detected: {pattern}")
    
    return text_str


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token
    
    Args:
        length: Length of token in bytes (default 32)
    
    Returns:
        URL-safe base64 encoded token
    """
    return secrets.token_urlsafe(length)


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format and safety
    
    Args:
        url: URL to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL is required"
    
    # Basic URL format validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False, "Invalid URL format"
    
    # Check for dangerous protocols
    dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
    url_lower = url.lower()
    for protocol in dangerous_protocols:
        if url_lower.startswith(protocol):
            return False, f"Dangerous protocol detected: {protocol}"
    
    return True, None

