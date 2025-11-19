"""Tests for confidence scoring service"""

import pytest
from app.services.confidence_scoring import ConfidenceScoringService


class TestConfidenceScoringService:
    """Test ConfidenceScoringService"""
    
    def test_calculate_source_confidence_high_reliability(self):
        """Test source confidence with high reliability"""
        service = ConfidenceScoringService()
        
        confidence = service.calculate_source_confidence(
            source="companies_house",
            source_type="official_registry",
            data_quality=0.9,
            verification_status=True
        )
        
        assert confidence >= 0.8
    
    def test_calculate_source_confidence_low_reliability(self):
        """Test source confidence with low reliability"""
        service = ConfidenceScoringService()
        
        confidence = service.calculate_source_confidence(
            source="user_input",
            source_type="user_provided",
            data_quality=0.3,
            verification_status=False
        )
        
        assert confidence < 0.5
    
    def test_calculate_field_confidence(self):
        """Test field confidence calculation"""
        service = ConfidenceScoringService()
        
        sources = [
            {"source": "api1", "value": "Company Inc", "confidence": 0.9},
            {"source": "api2", "value": "Company Inc", "confidence": 0.8},
            {"source": "api3", "value": "Company Inc", "confidence": 0.7}
        ]
        confidence = service.calculate_field_confidence(
            field_name="legal_name",
            field_value="Company Inc",
            sources=sources,
            cross_validation=True
        )
        
        assert 0.0 <= confidence <= 1.0
    
    def test_calculate_overall_confidence(self):
        """Test overall confidence calculation"""
        service = ConfidenceScoringService()
        
        confidence = service.calculate_overall_verification_confidence(
            dns_confidence=0.9,
            registration_confidence=0.8,
            contact_confidence=0.7,
            address_confidence=0.85,
            discrepancy_score=0.9
        )
        
        assert 0.0 <= confidence["overall_confidence"] <= 1.0
        assert "overall_confidence" in confidence
        assert "breakdown" in confidence

