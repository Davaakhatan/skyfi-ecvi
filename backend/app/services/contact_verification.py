"""Contact information verification service"""

from typing import Dict, Optional, Tuple
import re
import dns.resolver
import dns.exception
from app.utils.validators import validate_email, validate_phone


class ContactVerificationService:
    """Service for verifying contact information (email, phone)"""
    
    @staticmethod
    def verify_email(email: str) -> Dict:
        """
        Verify email address format and existence
        
        Args:
            email: Email address to verify
        
        Returns:
            Dictionary with verification results
        """
        result = {
            "email": email,
            "format_valid": False,
            "domain_exists": False,
            "mx_record_exists": False,
            "email_exists": None,  # None = not checked, True/False = checked
            "verified": False,
            "errors": []
        }
        
        if not email:
            result["errors"].append("Email is required")
            return result
        
        # Step 1: Format validation
        format_valid, format_error = validate_email(email)
        result["format_valid"] = format_valid
        if not format_valid:
            result["errors"].append(f"Format validation failed: {format_error}")
            return result
        
        # Extract domain
        try:
            domain = email.split("@")[1]
        except IndexError:
            result["errors"].append("Invalid email format - no domain found")
            return result
        
        # Step 2: Check if domain exists (DNS A record)
        try:
            dns.resolver.resolve(domain, "A")
            result["domain_exists"] = True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            result["errors"].append("Domain does not exist or has no A record")
        except Exception as e:
            result["errors"].append(f"DNS A record check failed: {str(e)}")
        
        # Step 3: Check MX record (indicates email capability)
        try:
            mx_records = dns.resolver.resolve(domain, "MX")
            result["mx_record_exists"] = True
            result["mx_records"] = [str(r) for r in mx_records]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            result["errors"].append("No MX record found - domain may not handle email")
        except Exception as e:
            result["errors"].append(f"MX record check failed: {str(e)}")
        
        # Step 4: Email existence check (SMTP verification)
        # Note: This is a basic check - full SMTP verification requires connecting to mail server
        # For now, we'll mark it as None (not checked) since it requires external service
        # TODO: Integrate with email verification API (e.g., ZeroBounce, NeverBounce)
        result["email_exists"] = None
        
        # Overall verification status
        result["verified"] = (
            result["format_valid"] and
            result["domain_exists"] and
            result["mx_record_exists"]
        )
        
        return result
    
    @staticmethod
    def verify_phone(phone: str, country_code: Optional[str] = None) -> Dict:
        """
        Verify phone number format and carrier
        
        Args:
            phone: Phone number to verify
            country_code: Optional country code (e.g., 'US', 'GB')
        
        Returns:
            Dictionary with verification results
        """
        result = {
            "phone": phone,
            "format_valid": False,
            "carrier_valid": None,  # None = not checked, True/False = checked
            "carrier_name": None,
            "line_type": None,  # mobile, landline, voip, etc.
            "verified": False,
            "errors": []
        }
        
        if not phone:
            result["errors"].append("Phone number is required")
            return result
        
        # Step 1: Format validation
        format_valid, format_error = validate_phone(phone, country_code)
        result["format_valid"] = format_valid
        if not format_valid:
            result["errors"].append(f"Format validation failed: {format_error}")
            return result
        
        # Step 2: Carrier validation
        # Note: Full carrier validation requires external API (e.g., Twilio Lookup, NumLookup)
        # For now, we'll do basic validation and mark carrier check as None
        # TODO: Integrate with phone carrier lookup API
        
        # Basic checks we can do without external API:
        # - Check for common invalid patterns
        # - Check length and format consistency
        
        cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
        
        # Check for suspicious patterns (all same digit, sequential, etc.)
        if len(set(cleaned)) == 1:
            result["errors"].append("Phone number appears invalid (all same digits)")
            result["carrier_valid"] = False
        elif cleaned == cleaned[::-1]:  # Palindrome check
            result["errors"].append("Phone number appears invalid (palindrome)")
            result["carrier_valid"] = False
        else:
            # Format looks valid, but carrier not verified
            result["carrier_valid"] = None
        
        # Overall verification status
        result["verified"] = result["format_valid"] and (
            result["carrier_valid"] is not False
        )
        
        return result
    
    @staticmethod
    def verify_contact_info(
        email: Optional[str] = None,
        phone: Optional[str] = None,
        country_code: Optional[str] = None
    ) -> Dict:
        """
        Verify both email and phone contact information
        
        Args:
            email: Email address to verify
            phone: Phone number to verify
            country_code: Optional country code for phone validation
        
        Returns:
            Dictionary with combined verification results
        """
        result = {
            "email_result": None,
            "phone_result": None,
            "overall_verified": False,
            "has_email": False,
            "has_phone": False
        }
        
        if email:
            result["has_email"] = True
            result["email_result"] = ContactVerificationService.verify_email(email)
        
        if phone:
            result["has_phone"] = True
            result["phone_result"] = ContactVerificationService.verify_phone(phone, country_code)
        
        # Overall verification: at least one contact method must be verified
        email_verified = result["email_result"]["verified"] if result["email_result"] else False
        phone_verified = result["phone_result"]["verified"] if result["phone_result"] else False
        
        result["overall_verified"] = email_verified or phone_verified
        
        return result

