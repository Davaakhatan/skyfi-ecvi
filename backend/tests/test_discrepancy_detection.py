"""Tests for discrepancy detection service"""

import pytest
from app.services.discrepancy_detection import DiscrepancyDetectionService


class TestDiscrepancyDetectionService:
    """Test DiscrepancyDetectionService"""
    
    def test_detect_name_discrepancies_no_discrepancies(self):
        """Test name discrepancy detection with no discrepancies"""
        service = DiscrepancyDetectionService()
        
        sources = [
            {"source": "registry1", "name": "Example Company Inc"},
            {"source": "registry2", "name": "Example Company Inc"},
            {"source": "registry3", "name": "Example Company Inc"},
        ]
        
        result = service.detect_name_discrepancies("Example Company Inc", sources)
        
        assert result["severity"] == "low"
        assert len(result.get("discrepancies", [])) == 0
    
    def test_detect_name_discrepancies_with_discrepancies(self):
        """Test name discrepancy detection with discrepancies"""
        service = DiscrepancyDetectionService()
        
        sources = [
            {"source": "registry1", "name": "Example Company Inc"},
            {"source": "registry2", "name": "Example Company LLC"},
            {"source": "registry3", "name": "Example Company Inc"},
        ]
        
        result = service.detect_name_discrepancies("Example Company Inc", sources)
        
        assert result["severity"] in ["medium", "high"]
        assert len(result.get("discrepancies", [])) > 0
    
    def test_detect_address_discrepancies(self):
        """Test address discrepancy detection"""
        service = DiscrepancyDetectionService()
        
        sources = [
            {"source": "registry1", "address": "123 Main St, New York, NY 10001"},
            {"source": "registry2", "address": "123 Main Street, New York, NY 10001"},
        ]
        
        result = service.detect_address_discrepancies("123 Main St, New York, NY 10001", sources)
        
        assert "severity" in result
        assert "discrepancies" in result
    
    def test_detect_registration_discrepancies(self):
        """Test registration number discrepancy detection"""
        service = DiscrepancyDetectionService()
        
        sources = [
            {"source": "registry1", "registration_number": "12345678"},
            {"source": "registry2", "registration_number": "12345678"},
        ]
        
        result = service.detect_registration_discrepancies("12345678", sources)
        
        assert "severity" in result
        assert "discrepancies" in result

