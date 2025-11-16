"""Unit tests for risk calculator service"""

import pytest
from app.services.risk_calculator import RiskCalculator
from app.models.verification_result import RiskCategory


class TestRiskCalculator:
    """Test suite for RiskCalculator"""
    
    def test_calculate_dns_risk_no_verification(self):
        """Test DNS risk when DNS verification fails"""
        risk = RiskCalculator.calculate_dns_risk(dns_verified=False)
        assert risk == 100
    
    def test_calculate_dns_risk_unknown_age(self):
        """Test DNS risk when domain age is unknown"""
        risk = RiskCalculator.calculate_dns_risk(dns_verified=True, domain_age_days=None)
        assert risk == 50
    
    def test_calculate_dns_risk_very_new_domain(self):
        """Test DNS risk for very new domains (< 30 days)"""
        risk = RiskCalculator.calculate_dns_risk(dns_verified=True, domain_age_days=15)
        assert risk == 80
    
    def test_calculate_dns_risk_new_domain(self):
        """Test DNS risk for new domains (30-90 days)"""
        risk = RiskCalculator.calculate_dns_risk(dns_verified=True, domain_age_days=60)
        assert risk == 60
    
    def test_calculate_dns_risk_young_domain(self):
        """Test DNS risk for domains less than a year"""
        risk = RiskCalculator.calculate_dns_risk(dns_verified=True, domain_age_days=200)
        assert risk == 30
    
    def test_calculate_dns_risk_established_domain(self):
        """Test DNS risk for established domains (>= 365 days)"""
        risk = RiskCalculator.calculate_dns_risk(dns_verified=True, domain_age_days=500)
        assert risk == 10
    
    def test_calculate_registration_consistency_risk_no_sources(self):
        """Test registration risk when no sources available"""
        risk = RiskCalculator.calculate_registration_consistency_risk(
            registration_matches=0, total_sources=0
        )
        assert risk == 70
    
    def test_calculate_registration_consistency_risk_high_consistency(self):
        """Test registration risk with high consistency (>= 90%)"""
        risk = RiskCalculator.calculate_registration_consistency_risk(
            registration_matches=9, total_sources=10
        )
        assert risk == 10
    
    def test_calculate_registration_consistency_risk_good_consistency(self):
        """Test registration risk with good consistency (70-90%)"""
        risk = RiskCalculator.calculate_registration_consistency_risk(
            registration_matches=8, total_sources=10
        )
        assert risk == 30
    
    def test_calculate_registration_consistency_risk_moderate_consistency(self):
        """Test registration risk with moderate consistency (50-70%)"""
        risk = RiskCalculator.calculate_registration_consistency_risk(
            registration_matches=6, total_sources=10
        )
        assert risk == 60
    
    def test_calculate_registration_consistency_risk_low_consistency(self):
        """Test registration risk with low consistency (< 50%)"""
        risk = RiskCalculator.calculate_registration_consistency_risk(
            registration_matches=3, total_sources=10
        )
        assert risk == 90
    
    def test_calculate_contact_validation_risk_invalid_email(self):
        """Test contact risk with invalid email"""
        risk = RiskCalculator.calculate_contact_validation_risk(
            email_valid=False, phone_valid=True
        )
        assert risk == 40
    
    def test_calculate_contact_validation_risk_invalid_phone(self):
        """Test contact risk with invalid phone"""
        risk = RiskCalculator.calculate_contact_validation_risk(
            email_valid=True, phone_valid=False
        )
        assert risk == 40
    
    def test_calculate_contact_validation_risk_both_invalid(self):
        """Test contact risk with both invalid"""
        risk = RiskCalculator.calculate_contact_validation_risk(
            email_valid=False, phone_valid=False
        )
        assert risk == 80
    
    def test_calculate_contact_validation_risk_email_not_exists(self):
        """Test contact risk when email doesn't exist"""
        risk = RiskCalculator.calculate_contact_validation_risk(
            email_valid=True, phone_valid=True,
            email_exists=False, phone_carrier_valid=None
        )
        assert risk == 30
    
    def test_calculate_contact_validation_risk_email_exists(self):
        """Test contact risk when email exists (reduces risk)"""
        risk = RiskCalculator.calculate_contact_validation_risk(
            email_valid=True, phone_valid=True,
            email_exists=True, phone_carrier_valid=None
        )
        assert risk == 0  # 40 - 10 = 30, but min is 0
    
    def test_calculate_contact_validation_risk_all_valid(self):
        """Test contact risk when all contact info is valid"""
        risk = RiskCalculator.calculate_contact_validation_risk(
            email_valid=True, phone_valid=True,
            email_exists=True, phone_carrier_valid=True
        )
        assert risk == 0  # Both reduce risk by 10 each
    
    def test_calculate_domain_authenticity_risk_no_match(self):
        """Test domain authenticity risk when domain doesn't match company"""
        risk = RiskCalculator.calculate_domain_authenticity_risk(
            domain_matches_company=False
        )
        assert risk == 50
    
    def test_calculate_domain_authenticity_risk_no_ssl(self):
        """Test domain authenticity risk with invalid SSL"""
        risk = RiskCalculator.calculate_domain_authenticity_risk(
            domain_matches_company=True, ssl_valid=False
        )
        assert risk == 30
    
    def test_calculate_domain_authenticity_risk_valid_ssl(self):
        """Test domain authenticity risk with valid SSL (reduces risk)"""
        risk = RiskCalculator.calculate_domain_authenticity_risk(
            domain_matches_company=True, ssl_valid=True
        )
        assert risk == 0  # 0 - 15 = -15, but min is 0
    
    def test_calculate_domain_authenticity_risk_suspicious_keywords(self):
        """Test domain authenticity risk with suspicious keywords"""
        risk = RiskCalculator.calculate_domain_authenticity_risk(
            domain_matches_company=True, ssl_valid=True, suspicious_keywords=2
        )
        assert risk == 20  # 0 + (2 * 10) = 20
    
    def test_calculate_domain_authenticity_risk_max_keywords(self):
        """Test domain authenticity risk with max suspicious keywords"""
        risk = RiskCalculator.calculate_domain_authenticity_risk(
            domain_matches_company=True, ssl_valid=True, suspicious_keywords=10
        )
        assert risk == 30  # Capped at 30
    
    def test_calculate_cross_source_validation_risk_high_consistency(self):
        """Test cross-source risk with high consistency"""
        risk = RiskCalculator.calculate_cross_source_validation_risk(
            data_consistency_score=0.9, source_reliability_avg=0.8
        )
        # (1.0 - 0.9) * 60 = 6, (1.0 - 0.8) * 40 = 8, total = 14
        assert risk == 14
    
    def test_calculate_cross_source_validation_risk_low_consistency(self):
        """Test cross-source risk with low consistency"""
        risk = RiskCalculator.calculate_cross_source_validation_risk(
            data_consistency_score=0.3, source_reliability_avg=0.5
        )
        # (1.0 - 0.3) * 60 = 42, (1.0 - 0.5) * 40 = 20, total = 62
        assert risk == 62
    
    def test_calculate_cross_source_validation_risk_perfect(self):
        """Test cross-source risk with perfect scores"""
        risk = RiskCalculator.calculate_cross_source_validation_risk(
            data_consistency_score=1.0, source_reliability_avg=1.0
        )
        assert risk == 0
    
    def test_calculate_overall_risk_low_risk(self):
        """Test overall risk calculation for low-risk company"""
        result = RiskCalculator.calculate_overall_risk(
            dns_verified=True,
            domain_age_days=500,  # Established domain
            registration_matches=9,
            total_sources=10,  # High consistency
            email_valid=True,
            phone_valid=True,
            email_exists=True,
            phone_carrier_valid=True,
            domain_matches_company=True,
            ssl_valid=True,
            suspicious_keywords=0,
            data_consistency_score=0.9,
            source_reliability_avg=0.8
        )
        
        assert result["risk_score"] <= 30
        assert result["risk_category"] == RiskCategory.LOW
        assert "breakdown" in result
    
    def test_calculate_overall_risk_high_risk(self):
        """Test overall risk calculation for high-risk company"""
        result = RiskCalculator.calculate_overall_risk(
            dns_verified=False,  # DNS fails
            domain_age_days=None,
            registration_matches=2,
            total_sources=10,  # Low consistency
            email_valid=False,
            phone_valid=False,
            email_exists=False,
            phone_carrier_valid=False,
            domain_matches_company=False,
            ssl_valid=False,
            suspicious_keywords=3,
            data_consistency_score=0.2,
            source_reliability_avg=0.3
        )
        
        assert result["risk_score"] > 70
        assert result["risk_category"] == RiskCategory.HIGH
        assert "breakdown" in result
    
    def test_calculate_overall_risk_medium_risk(self):
        """Test overall risk calculation for medium-risk company"""
        result = RiskCalculator.calculate_overall_risk(
            dns_verified=True,
            domain_age_days=100,  # Young domain
            registration_matches=6,
            total_sources=10,  # Moderate consistency
            email_valid=True,
            phone_valid=True,
            email_exists=None,  # Not checked
            phone_carrier_valid=None,
            domain_matches_company=True,
            ssl_valid=True,
            suspicious_keywords=0,
            data_consistency_score=0.6,
            source_reliability_avg=0.6
        )
        
        assert 30 < result["risk_score"] <= 70
        assert result["risk_category"] == RiskCategory.MEDIUM
        assert "breakdown" in result
    
    def test_calculate_overall_risk_boundary_low_medium(self):
        """Test overall risk at boundary between LOW and MEDIUM"""
        # Score should be exactly 30
        result = RiskCalculator.calculate_overall_risk(
            dns_verified=True,
            domain_age_days=365,
            registration_matches=9,
            total_sources=10,
            email_valid=True,
            phone_valid=True,
            email_exists=True,
            phone_carrier_valid=True,
            domain_matches_company=True,
            ssl_valid=True,
            suspicious_keywords=0,
            data_consistency_score=0.9,
            source_reliability_avg=0.8
        )
        
        # Should be LOW (<= 30)
        assert result["risk_category"] == RiskCategory.LOW
    
    def test_calculate_overall_risk_boundary_medium_high(self):
        """Test overall risk at boundary between MEDIUM and HIGH"""
        result = RiskCalculator.calculate_overall_risk(
            dns_verified=True,
            domain_age_days=50,  # New domain
            registration_matches=4,
            total_sources=10,  # Low consistency
            email_valid=True,
            phone_valid=False,  # Invalid phone
            email_exists=None,
            phone_carrier_valid=None,
            domain_matches_company=False,  # Domain mismatch
            ssl_valid=False,
            suspicious_keywords=2,
            data_consistency_score=0.4,
            source_reliability_avg=0.5
        )
        
        # Should be HIGH (> 70)
        assert result["risk_category"] == RiskCategory.HIGH
    
    def test_calculate_overall_risk_score_range(self):
        """Test that overall risk score is always in valid range (0-100)"""
        # Test with extreme values
        result = RiskCalculator.calculate_overall_risk(
            dns_verified=True,
            domain_age_days=1000,
            registration_matches=10,
            total_sources=10,
            email_valid=True,
            phone_valid=True,
            email_exists=True,
            phone_carrier_valid=True,
            domain_matches_company=True,
            ssl_valid=True,
            suspicious_keywords=0,
            data_consistency_score=1.0,
            source_reliability_avg=1.0
        )
        
        assert 0 <= result["risk_score"] <= 100
    
    def test_calculate_overall_risk_breakdown_structure(self):
        """Test that breakdown contains all expected components"""
        result = RiskCalculator.calculate_overall_risk(
            dns_verified=True,
            domain_age_days=200,
            registration_matches=7,
            total_sources=10,
            email_valid=True,
            phone_valid=True,
            email_exists=True,
            phone_carrier_valid=True,
            domain_matches_company=True,
            ssl_valid=True,
            suspicious_keywords=0,
            data_consistency_score=0.7,
            source_reliability_avg=0.7
        )
        
        breakdown = result["breakdown"]
        assert "dns_risk" in breakdown
        assert "registration_risk" in breakdown
        assert "contact_risk" in breakdown
        assert "domain_risk" in breakdown
        assert "cross_source_risk" in breakdown
        assert "weights" in breakdown
        
        weights = breakdown["weights"]
        assert "dns" in weights
        assert "registration" in weights
        assert "contact" in weights
        assert "domain" in weights
        assert "cross_source" in weights

