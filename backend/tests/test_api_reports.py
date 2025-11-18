"""Tests for reports API endpoints"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.db.database import get_db

client = TestClient(app)


class TestReportsAPI:
    """Test reports API endpoints"""
    
    def test_generate_report(self, db_session, override_get_db, test_user, test_company, test_verification_result):
        """Test generating a verification report"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.get(
            f"/api/v1/reports/company/{test_company.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "company_info" in data
        assert "verification_summary" in data
        
        app.dependency_overrides.clear()
    
    def test_export_report_json(self, db_session, override_get_db, test_user, test_company, test_verification_result):
        """Test exporting report as JSON"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.get(
            f"/api/v1/reports/company/{test_company.id}/export",
            params={"format": "json"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        app.dependency_overrides.clear()
    
    def test_export_report_csv(self, db_session, override_get_db, test_user, test_company, test_verification_result):
        """Test exporting report as CSV"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.get(
            f"/api/v1/reports/company/{test_company.id}/export",
            params={"format": "csv"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        
        app.dependency_overrides.clear()
    
    def test_create_shareable_link(self, db_session, override_get_db, test_user, test_company, test_verification_result):
        """Test creating a shareable report link"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.post(
            f"/api/v1/reports/company/{test_company.id}/share",
            json={"expires_in_days": 7},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "share_token" in data
        assert "share_url" in data
        
        app.dependency_overrides.clear()
    
    def test_get_shared_report(self, db_session, override_get_db, test_user, test_company, test_verification_result):
        """Test getting shared report by token"""
        from app.core.auth import get_current_active_user
        from app.services.report_sharing import ReportSharingService
        
        # Create shareable link first
        sharing_service = ReportSharingService(db_session)
        link = sharing_service.create_shareable_link(
            company_id=test_company.id,
            verification_result_id=test_verification_result.id,
            created_by=test_user.id
        )
        
        app.dependency_overrides[get_db] = override_get_db
        
        # Get shared report (no auth required)
        response = client.get(f"/api/v1/reports/shared/{link.share_token}")
        
        assert response.status_code == 200
        data = response.json()
        assert "company_info" in data
        
        app.dependency_overrides.clear()

