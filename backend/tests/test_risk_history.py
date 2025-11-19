"""Tests for risk history service"""

import pytest
from uuid import uuid4
from app.services.risk_history import RiskHistoryService
from app.models.verification_result import RiskCategory, VerificationStatus


class TestRiskHistoryService:
    """Test RiskHistoryService"""
    
    def test_store_risk_score(self, db_session, test_company, test_verification_result):
        """Test storing risk score"""
        # Update the verification result's risk score
        test_verification_result.risk_score = 75
        test_verification_result.risk_category = RiskCategory.HIGH
        test_verification_result.verification_status = VerificationStatus.COMPLETED
        db_session.commit()
        
        # Verify it was stored
        history = RiskHistoryService.get_risk_history(db_session, test_company.id)
        assert len(history) >= 1
        assert history[0]["risk_score"] == 75
    
    def test_get_risk_history(self, db_session, test_company, test_verification_result):
        """Test getting risk history"""
        from app.models.verification_result import VerificationResult
        
        # Create multiple verification results with different scores
        for score in [50, 60, 70]:
            vr = VerificationResult(
                company_id=test_company.id,
                risk_score=score,
                risk_category=RiskCategory.MEDIUM,
                verification_status=VerificationStatus.COMPLETED
            )
            db_session.add(vr)
        db_session.commit()
        
        history = RiskHistoryService.get_risk_history(db_session, test_company.id)
        assert len(history) >= 3
    
    def test_get_risk_trend(self, db_session, test_company, test_verification_result):
        """Test getting risk trend"""
        from app.models.verification_result import VerificationResult
        
        # Create multiple verification results with different scores over time
        for score in [50, 55, 60, 65]:
            vr = VerificationResult(
                company_id=test_company.id,
                risk_score=score,
                risk_category=RiskCategory.MEDIUM,
                verification_status=VerificationStatus.COMPLETED
            )
            db_session.add(vr)
        db_session.commit()
        
        trend = RiskHistoryService.get_risk_trend(db_session, test_company.id)
        assert "trend" in trend
        assert "latest_score" in trend
        assert "average_score" in trend

