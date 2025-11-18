"""Tests for confidence scoring service"""

import pytest
from app.services.confidence_scoring import ConfidenceScoringService


class TestConfidenceScoringService:
    """Test ConfidenceScoringService"""
    
    def test_calculate_source_confidence_high_reliability(self):
        """Test source confidence with high reliability"""
        service = ConfidenceScoringService()
        
        confidence = service.calculate_source_confidence(
            source_type="official_registry",
            data_quality=0.9,
            cross_references=5
        )
        
        assert confidence >= 0.8
    
    def test_calculate_source_confidence_low_reliability(self):
        """Test source confidence with low reliability"""
        service = ConfidenceScoringService()
        
        confidence = service.calculate_source_confidence(
            source_type="user_submitted",
            data_quality=0.3,
            cross_references=0
        )
        
        assert confidence < 0.5
    
    def test_calculate_field_confidence(self):
        """Test field confidence calculation"""
        service = ConfidenceScoringService()
        
        source_confidences = [0.9, 0.8, 0.7]
        confidence = service.calculate_field_confidence(source_confidences)
        
        assert 0.0 <= confidence <= 1.0
    
    def test_calculate_overall_confidence(self):
        """Test overall confidence calculation"""
        service = ConfidenceScoringService()
        
        confidence = service.calculate_overall_confidence(
            dns_confidence=0.9,
            registration_confidence=0.8,
            contact_confidence=0.7,
            address_confidence=0.85
        )
        
        assert 0.0 <= confidence <= 1.0
        assert "overall" in confidence
        assert "breakdown" in confidence

