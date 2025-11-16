"""Company registration data verification service"""

from typing import Dict, List, Optional
from app.utils.validators import validate_registration_number


class RegistrationVerificationService:
    """Service for verifying company registration data"""
    
    @staticmethod
    def verify_registration_number(
        registration_number: str,
        jurisdiction: Optional[str] = None
    ) -> Dict:
        """
        Verify company registration number format
        
        Args:
            registration_number: Registration number to verify
            jurisdiction: Optional jurisdiction code
        
        Returns:
            Dictionary with verification results
        """
        result = {
            "registration_number": registration_number,
            "format_valid": False,
            "jurisdiction": jurisdiction,
            "verified": False,
            "errors": []
        }
        
        if not registration_number:
            result["errors"].append("Registration number is required")
            return result
        
        # Format validation
        format_valid, format_error = validate_registration_number(registration_number, jurisdiction)
        result["format_valid"] = format_valid
        if not format_valid:
            result["errors"].append(f"Format validation failed: {format_error}")
            return result
        
        # TODO: Integrate with external registration databases
        # - Companies House (UK)
        # - SEC EDGAR (US)
        # - Other jurisdiction-specific APIs
        
        # For now, format validation is all we can do
        result["verified"] = result["format_valid"]
        
        return result
    
    @staticmethod
    def cross_reference_registration_data(
        legal_name: str,
        registration_number: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        domain: Optional[str] = None
    ) -> Dict:
        """
        Cross-reference registration data from multiple sources
        
        Args:
            legal_name: Company legal name
            registration_number: Registration number
            jurisdiction: Jurisdiction code
            domain: Company domain
        
        Returns:
            Dictionary with cross-reference results
        """
        result = {
            "legal_name": legal_name,
            "registration_number": registration_number,
            "jurisdiction": jurisdiction,
            "sources_checked": [],
            "matches": 0,
            "total_sources": 0,
            "consistency_score": 0.0,
            "verified": False,
            "discrepancies": []
        }
        
        # TODO: Integrate with external APIs for data collection
        # Sources to check:
        # 1. Official company registry (jurisdiction-specific)
        # 2. Business directories (e.g., Yellow Pages, Yelp)
        # 3. Government databases
        # 4. Domain WHOIS data
        # 5. Social media profiles
        
        # For now, return structure with placeholder data
        result["sources_checked"] = []
        result["matches"] = 0
        result["total_sources"] = 0
        result["consistency_score"] = 0.0
        
        # If we have registration number, validate format
        if registration_number:
            reg_result = RegistrationVerificationService.verify_registration_number(
                registration_number, jurisdiction
            )
            if reg_result["verified"]:
                result["matches"] = 1
                result["total_sources"] = 1
                result["consistency_score"] = 1.0
                result["verified"] = True
        
        return result
    
    @staticmethod
    def verify_address(
        address: str,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        postal_code: Optional[str] = None
    ) -> Dict:
        """
        Verify company address
        
        Args:
            address: Street address
            city: City name
            state: State/province
            country: Country code
            postal_code: Postal/ZIP code
        
        Returns:
            Dictionary with verification results
        """
        result = {
            "address": address,
            "city": city,
            "state": state,
            "country": country,
            "postal_code": postal_code,
            "format_valid": False,
            "geocoded": False,
            "coordinates": None,
            "verified": False,
            "errors": []
        }
        
        if not address:
            result["errors"].append("Address is required")
            return result
        
        # Basic format validation
        if len(address.strip()) < 5:
            result["errors"].append("Address too short")
            return result
        
        result["format_valid"] = True
        
        # Enhanced validation
        # Check if all required components are present
        required_fields = ["address"]
        optional_fields = ["city", "state", "country", "postal_code"]
        
        # Validate postal code format if provided
        if postal_code:
            # Basic postal code validation (alphanumeric, common formats)
            if len(postal_code.strip()) < 3:
                result["errors"].append("Postal code too short")
            elif len(postal_code.strip()) > 20:
                result["errors"].append("Postal code too long")
        
        # Validate country code if provided
        if country:
            if len(country.strip()) != 2:
                result["errors"].append("Country code must be 2 characters (ISO 3166-1 alpha-2)")
        
        # Calculate completeness score
        provided_fields = sum(1 for field in [address, city, state, country, postal_code] if field)
        total_fields = len(required_fields) + len(optional_fields)
        completeness = provided_fields / total_fields
        result["completeness_score"] = completeness
        
        # TODO: Integrate with geocoding API (e.g., Google Maps, Mapbox)
        # TODO: Verify address exists and is valid
        # TODO: Check if address matches company registration records
        
        # For now, format validation and completeness determine verification
        result["verified"] = result["format_valid"] and completeness >= 0.6
        
        return result
    
    @staticmethod
    def collect_registration_data(
        legal_name: str,
        registration_number: Optional[str] = None,
        jurisdiction: Optional[str] = None
    ) -> Dict:
        """
        Collect registration data from multiple sources
        
        Args:
            legal_name: Company legal name
            registration_number: Registration number (if known)
            jurisdiction: Jurisdiction code
        
        Returns:
            Dictionary with collected data and source information
        """
        result = {
            "legal_name": legal_name,
            "registration_number": registration_number,
            "jurisdiction": jurisdiction,
            "sources": [],
            "data_points": [],
            "confidence_scores": {},
            "verified": False
        }
        
        # TODO: Integrate with AI service for data collection
        # This will use LangChain agents to:
        # 1. Search official registries
        # 2. Query business directories
        # 3. Check government databases
        # 4. Verify against multiple sources
        
        # For now, return structure
        return result

