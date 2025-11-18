"""Tests for risk scoring API endpoints"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.db.database import get_db

client = TestClient(app)


class TestRiskScoringAPI:
    """Test risk scoring API endpoints"""
    
    def test_get_risk_score(self, db_session, override_get_db, test_user, test_company, test_verification_result):
        """Test getting risk score for a company"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.get(
            f"/api/v1/risk/company/{test_company.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data
        assert "risk_category" in data
        assert 0 <= data["risk_score"] <= 100
        
        app.dependency_overrides.clear()
    
    def test_get_risk_history(self, db_session, override_get_db, test_user, test_company, test_verification_result):
        """Test getting risk score history"""
        from app.core.auth import get_current_active_user
        from app.services.risk_history import RiskHistoryService
        from app.models.verification_result import RiskCategory
        
        # Create some risk history
        history_service = RiskHistoryService(db_session)
        for score in [50, 60, 70]:
            history_service.store_risk_score(
                company_id=test_company.id,
                verification_result_id=test_verification_result.id,
                risk_score=score,
                risk_category=RiskCategory.MEDIUM
            )
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.get(
            f"/api/v1/risk/company/{test_company.id}/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        app.dependency_overrides.clear()
    
    def test_get_risk_trend(self, db_session, override_get_db, test_user, test_company, test_verification_result):
        """Test getting risk trend analysis"""
        from app.core.auth import get_current_active_user
        from app.services.risk_history import RiskHistoryService
        from app.models.verification_result import RiskCategory
        
        # Create risk history
        history_service = RiskHistoryService(db_session)
        for score in [50, 55, 60]:
            history_service.store_risk_score(
                company_id=test_company.id,
                verification_result_id=test_verification_result.id,
                risk_score=score,
                risk_category=RiskCategory.MEDIUM
            )
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.get(
            f"/api/v1/risk/company/{test_company.id}/trend",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "trend" in data
        assert "current_score" in data
        
        app.dependency_overrides.clear()

