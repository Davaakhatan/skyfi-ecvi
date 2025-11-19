"""Tests for data corrections API endpoints"""

import pytest
from app.core.security import create_access_token
from app.db.database import get_db
from app.main import app


class TestDataCorrectionsAPI:
    """Test data corrections API endpoints"""
    
    def test_create_correction(self, client, db_session, override_get_db, test_user, test_company):
        """Test creating a data correction"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.post(
            f"/api/v1/company/{test_company.id}/corrections",
            json={
                "field_name": "Legal Name",
                "field_type": "legal_name",
                "new_value": "Updated Company Name",
                "correction_reason": "Name change"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["field_name"] == "Legal Name"
        assert data["new_value"] == "Updated Company Name"
        assert data["status"] == "PENDING"
        
        app.dependency_overrides.clear()
    
    def test_create_correction_same_value(self, client, db_session, override_get_db, test_user, test_company):
        """Test creating correction with same value"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.post(
            f"/api/v1/company/{test_company.id}/corrections",
            json={
                "field_name": "Legal Name",
                "field_type": "legal_name",
                "new_value": test_company.legal_name,
                "correction_reason": "No change"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        
        app.dependency_overrides.clear()
    
    def test_approve_correction(self, client, db_session, override_get_db, test_admin_user, test_company):
        """Test approving a correction"""
        from app.core.auth import get_current_active_user
        from app.services.data_correction import DataCorrectionService
        
        # Create a correction first
        service = DataCorrectionService(db_session)
        correction = service.create_correction(
            company_id=test_company.id,
            field_name="legal_name",
            field_type="legal_name",
            old_value=test_company.legal_name,
            new_value="Updated Name",
            correction_reason="Test",
            corrected_by=test_admin_user.id
        )
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_admin_user
        
        token = create_access_token(data={"sub": test_admin_user.email})
        response = client.post(
            f"/api/v1/corrections/{correction.id}/approve",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "APPROVED"
        
        app.dependency_overrides.clear()
    
    def test_reject_correction(self, client, db_session, override_get_db, test_admin_user, test_company):
        """Test rejecting a correction"""
        from app.core.auth import get_current_active_user
        from app.services.data_correction import DataCorrectionService
        
        # Create a correction first
        service = DataCorrectionService(db_session)
        correction = service.create_correction(
            company_id=test_company.id,
            field_name="legal_name",
            field_type="legal_name",
            old_value="Old",
            new_value="New",
            correction_reason="Test",
            corrected_by=test_admin_user.id
        )
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_admin_user
        
        token = create_access_token(data={"sub": test_admin_user.email})
        response = client.post(
            f"/api/v1/corrections/{correction.id}/reject",
            params={"rejection_reason": "Invalid correction"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "REJECTED"
        
        app.dependency_overrides.clear()
    
    def test_get_correction_history(self, client, db_session, override_get_db, test_user, test_company):
        """Test getting correction history"""
        from app.core.auth import get_current_active_user
        from app.services.data_correction import DataCorrectionService
        
        # Create some corrections
        service = DataCorrectionService(db_session)
        for i in range(2):
            service.create_correction(
                company_id=test_company.id,
                field_name=f"field_{i}",
                field_type="legal_name",
                old_value=f"Old {i}",
                new_value=f"New {i}",
                correction_reason=f"Test {i}",
                corrected_by=test_user.id
            )
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.get(
            f"/api/v1/company/{test_company.id}/corrections",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        
        app.dependency_overrides.clear()

