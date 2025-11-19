"""Data validation utilities"""

import re
from typing import Optional, Tuple
import dns.resolver
import dns.exception


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    # Basic email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, None


def validate_phone(phone: str, country_code: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number format
    
    Args:
        phone: Phone number to validate
        country_code: Optional country code (e.g., 'US', 'GB')
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, "Phone number is required"
    
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it's all digits (with optional + prefix)
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    if not cleaned.isdigit():
        return False, "Phone number must contain only digits"
    
    # Basic length check (7-15 digits is typical)
    if len(cleaned) < 7 or len(cleaned) > 15:
        return False, "Phone number length invalid"
    
    return True, None


def validate_domain(domain: str) -> Tuple[bool, Optional[str]]:
    """
    Validate domain name format
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not domain:
        return False, "Domain is required"
    
    # Basic domain regex
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    if not re.match(pattern, domain):
        return False, "Invalid domain format"
    
    return True, None


def check_dns_record(domain: str, record_type: str = "A") -> Tuple[bool, Optional[str]]:
    """
    Check if DNS record exists for domain
    
    Args:
        domain: Domain name to check
        record_type: DNS record type (A, MX, etc.)
    
    Returns:
        Tuple of (exists, error_message)
    """
    try:
        dns.resolver.resolve(domain, record_type)
        return True, None
    except dns.resolver.NXDOMAIN:
        return False, "Domain does not exist"
    except dns.resolver.NoAnswer:
        return False, f"No {record_type} record found"
    except dns.exception.DNSException as e:
        return False, f"DNS error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def validate_registration_number(registration_number: str, jurisdiction: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate company registration number format
    
    Args:
        registration_number: Registration number to validate
        jurisdiction: Optional jurisdiction code for format-specific validation
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not registration_number:
        return False, "Registration number is required"
    
    # Basic validation - alphanumeric, some special chars allowed
    if not re.match(r'^[A-Z0-9\-/]+$', registration_number.upper()):
        return False, "Invalid registration number format"
    
    # Jurisdiction-specific validation could be added here
    # For now, just basic format check
    
    return True, None


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format and check for dangerous protocols
    
    Args:
        url: URL to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL is required"
    
    # Check for dangerous protocols
    dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:', 'about:']
    url_lower = url.lower().strip()
    
    for protocol in dangerous_protocols:
        if url_lower.startswith(protocol):
            return False, f"Dangerous protocol detected: {protocol}"
    
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
    
    return True, None

