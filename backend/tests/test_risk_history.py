"""Tests for risk history service"""

import pytest
from uuid import uuid4
from app.services.risk_history import RiskHistoryService
from app.models.verification_result import RiskCategory


class TestRiskHistoryService:
    """Test RiskHistoryService"""
    
    def test_store_risk_score(self, db_session, test_company, test_verification_result):
        """Test storing risk score"""
        service = RiskHistoryService(db_session)
        
        service.store_risk_score(
            company_id=test_company.id,
            verification_result_id=test_verification_result.id,
            risk_score=75,
            risk_category=RiskCategory.HIGH
        )
        
        # Verify it was stored
        history = service.get_risk_history(test_company.id)
        assert len(history) >= 1
        assert history[0].risk_score == 75
    
    def test_get_risk_history(self, db_session, test_company, test_verification_result):
        """Test getting risk history"""
        service = RiskHistoryService(db_session)
        
        # Store multiple scores
        for score in [50, 60, 70]:
            service.store_risk_score(
                company_id=test_company.id,
                verification_result_id=test_verification_result.id,
                risk_score=score,
                risk_category=RiskCategory.MEDIUM
            )
        
        history = service.get_risk_history(test_company.id)
        assert len(history) >= 3
    
    def test_get_risk_trend(self, db_session, test_company, test_verification_result):
        """Test getting risk trend"""
        service = RiskHistoryService(db_session)
        
        # Store scores over time
        for score in [50, 55, 60, 65]:
            service.store_risk_score(
                company_id=test_company.id,
                verification_result_id=test_verification_result.id,
                risk_score=score,
                risk_category=RiskCategory.MEDIUM
            )
        
        trend = service.get_risk_trend(test_company.id)
        assert "trend" in trend
        assert "current_score" in trend
        assert "previous_score" in trend

