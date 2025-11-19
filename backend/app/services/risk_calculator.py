"""Risk score calculation service"""

from typing import Dict, Optional
from app.models.verification_result import RiskCategory


class RiskCalculator:
    """Calculate risk scores for company verifications"""
    
    # Risk factor weights (sum should be ~100)
    DNS_WEIGHT = 25
    REGISTRATION_CONSISTENCY_WEIGHT = 25
    CONTACT_VALIDATION_WEIGHT = 20
    DOMAIN_AUTHENTICITY_WEIGHT = 15
    CROSS_SOURCE_VALIDATION_WEIGHT = 15
    
    @staticmethod
    def calculate_dns_risk(dns_verified: bool, domain_age_days: Optional[int] = None) -> int:
        """
        Calculate DNS-related risk score (0-100, higher = more risk)
        
        Args:
            dns_verified: Whether DNS verification passed
            domain_age_days: Age of domain in days
        
        Returns:
            Risk score component (0-100)
        """
        if not dns_verified:
            return 100  # Maximum risk if DNS doesn't verify
        
        if domain_age_days is None:
            return 50  # Unknown age = medium risk
        
        # Newer domains are riskier
        if domain_age_days < 30:
            return 80  # Very new domain
        elif domain_age_days < 90:
            return 60  # New domain
        elif domain_age_days < 365:
            return 30  # Less than a year
        else:
            return 10  # Established domain
    
    @staticmethod
    def calculate_registration_consistency_risk(
        registration_matches: int,
        total_sources: int
    ) -> int:
        """
        Calculate risk based on registration data consistency
        
        Args:
            registration_matches: Number of sources with matching registration data
            total_sources: Total number of sources checked
        
        Returns:
            Risk score component (0-100)
        """
        if total_sources == 0:
            return 70  # No data = high risk
        
        match_ratio = registration_matches / total_sources
        
        if match_ratio >= 0.9:
            return 10  # Very consistent
        elif match_ratio >= 0.7:
            return 30  # Mostly consistent
        elif match_ratio >= 0.5:
            return 60  # Somewhat inconsistent
        else:
            return 90  # Very inconsistent
    
    @staticmethod
    def calculate_contact_validation_risk(
        email_valid: bool,
        phone_valid: bool,
        email_exists: Optional[bool] = None,
        phone_carrier_valid: Optional[bool] = None
    ) -> int:
        """
        Calculate risk based on contact information validation
        
        Args:
            email_valid: Whether email format is valid
            phone_valid: Whether phone format is valid
            email_exists: Whether email actually exists (if checked)
            phone_carrier_valid: Whether phone carrier lookup succeeded
        
        Returns:
            Risk score component (0-100)
        """
        risk = 0
        
        if not email_valid:
            risk += 40
        elif email_exists is False:
            risk += 30
        elif email_exists is True:
            risk -= 10
        
        if not phone_valid:
            risk += 40
        elif phone_carrier_valid is False:
            risk += 20
        elif phone_carrier_valid is True:
            risk -= 10
        
        return min(100, max(0, risk))
    
    @staticmethod
    def calculate_domain_authenticity_risk(
        domain_matches_company: bool,
        ssl_valid: Optional[bool] = None,
        suspicious_keywords: int = 0
    ) -> int:
        """
        Calculate risk based on domain authenticity
        
        Args:
            domain_matches_company: Whether domain name matches company name
            ssl_valid: Whether SSL certificate is valid
            suspicious_keywords: Number of suspicious keywords found
        
        Returns:
            Risk score component (0-100)
        """
        risk = 0
        
        if not domain_matches_company:
            risk += 50
        
        if ssl_valid is False:
            risk += 30
        elif ssl_valid is True:
            # SSL valid reduces risk, but don't go below 0
            risk = max(0, risk - 15)
        
        # Suspicious keywords increase risk
        risk += min(30, suspicious_keywords * 10)
        
        return min(100, max(0, risk))
    
    @staticmethod
    def calculate_cross_source_validation_risk(
        data_consistency_score: float,
        source_reliability_avg: float
    ) -> int:
        """
        Calculate risk based on cross-source validation
        
        Args:
            data_consistency_score: Consistency score across sources (0.0-1.0)
            source_reliability_avg: Average reliability of sources (0.0-1.0)
        
        Returns:
            Risk score component (0-100)
        """
        # Lower consistency = higher risk
        consistency_risk = (1.0 - data_consistency_score) * 60
        
        # Lower reliability = higher risk
        reliability_risk = (1.0 - source_reliability_avg) * 40
        
        total_risk = consistency_risk + reliability_risk
        return min(100, max(0, int(total_risk)))
    
    @classmethod
    def calculate_overall_risk(
        cls,
        dns_verified: bool,
        domain_age_days: Optional[int] = None,
        registration_matches: int = 0,
        total_sources: int = 0,
        email_valid: bool = False,
        phone_valid: bool = False,
        email_exists: Optional[bool] = None,
        phone_carrier_valid: Optional[bool] = None,
        domain_matches_company: bool = False,
        ssl_valid: Optional[bool] = None,
        suspicious_keywords: int = 0,
        data_consistency_score: float = 0.0,
        source_reliability_avg: float = 0.0
    ) -> Dict:
        """
        Calculate overall risk score (0-100) and category
        
        Returns:
            Dictionary with:
            - risk_score: Overall risk score (0-100)
            - risk_category: LOW, MEDIUM, or HIGH
            - breakdown: Individual component scores
        """
        # Calculate individual risk components
        dns_risk = cls.calculate_dns_risk(dns_verified, domain_age_days)
        registration_risk = cls.calculate_registration_consistency_risk(
            registration_matches, total_sources
        )
        contact_risk = cls.calculate_contact_validation_risk(
            email_valid, phone_valid, email_exists, phone_carrier_valid
        )
        domain_risk = cls.calculate_domain_authenticity_risk(
            domain_matches_company, ssl_valid, suspicious_keywords
        )
        cross_source_risk = cls.calculate_cross_source_validation_risk(
            data_consistency_score, source_reliability_avg
        )
        
        # Calculate weighted overall score
        overall_score = (
            (dns_risk * cls.DNS_WEIGHT) +
            (registration_risk * cls.REGISTRATION_CONSISTENCY_WEIGHT) +
            (contact_risk * cls.CONTACT_VALIDATION_WEIGHT) +
            (domain_risk * cls.DOMAIN_AUTHENTICITY_WEIGHT) +
            (cross_source_risk * cls.CROSS_SOURCE_VALIDATION_WEIGHT)
        ) // 100
        
        # Determine risk category
        if overall_score <= 30:
            category = RiskCategory.LOW
        elif overall_score <= 70:
            category = RiskCategory.MEDIUM
        else:
            category = RiskCategory.HIGH
        
        return {
            "risk_score": min(100, max(0, overall_score)),
            "risk_category": category,
            "breakdown": {
                "dns_risk": dns_risk,
                "registration_risk": registration_risk,
                "contact_risk": contact_risk,
                "domain_risk": domain_risk,
                "cross_source_risk": cross_source_risk,
                "weights": {
                    "dns": cls.DNS_WEIGHT,
                    "registration": cls.REGISTRATION_CONSISTENCY_WEIGHT,
                    "contact": cls.CONTACT_VALIDATION_WEIGHT,
                    "domain": cls.DOMAIN_AUTHENTICITY_WEIGHT,
                    "cross_source": cls.CROSS_SOURCE_VALIDATION_WEIGHT
                }
            }
        }

