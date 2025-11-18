"""Tests for contact verification API endpoints"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.db.database import get_db

client = TestClient(app)


class TestContactVerificationAPI:
    """Test contact verification API endpoints"""
    
    def test_verify_contact_email(self, db_session, override_get_db, test_user, test_company):
        """Test verifying email contact"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.post(
            f"/api/v1/company/{test_company.id}/contact/verify",
            json={
                "email": "test@example.com"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data) > 0
        assert data[0]["contact_type"] == "EMAIL"
        assert data[0]["contact_value"] == "test@example.com"
        
        app.dependency_overrides.clear()
    
    def test_verify_contact_phone(self, db_session, override_get_db, test_user, test_company):
        """Test verifying phone contact"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.post(
            f"/api/v1/company/{test_company.id}/contact/verify",
            json={
                "phone": "+1234567890",
                "country_code": "US"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data) > 0
        assert data[0]["contact_type"] == "PHONE"
        
        app.dependency_overrides.clear()
    
    def test_verify_contact_no_contact_info(self, db_session, override_get_db, test_user, test_company):
        """Test verifying contact with no contact info provided"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.post(
            f"/api/v1/company/{test_company.id}/contact/verify",
            json={},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        
        app.dependency_overrides.clear()
    
    def test_get_contact_verifications(self, db_session, override_get_db, test_user, test_company):
        """Test getting contact verifications"""
        from app.core.auth import get_current_active_user
        from app.services.contact_verification_enhanced import EnhancedContactVerificationService
        
        # Create a verification first
        service = EnhancedContactVerificationService(db_session)
        service.verify_and_store_email(
            company_id=test_company.id,
            verification_result_id=None,
            email="test@example.com"
        )
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.get(
            f"/api/v1/company/{test_company.id}/contact/verifications",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        app.dependency_overrides.clear()
    
    def test_get_contact_verification_by_id(self, db_session, override_get_db, test_user, test_company):
        """Test getting specific contact verification"""
        from app.core.auth import get_current_active_user
        from app.services.contact_verification_enhanced import EnhancedContactVerificationService
        
        # Create a verification first
        service = EnhancedContactVerificationService(db_session)
        verification = service.verify_and_store_email(
            company_id=test_company.id,
            verification_result_id=None,
            email="test@example.com"
        )
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.get(
            f"/api/v1/contact/verification/{verification.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(verification.id)
        
        app.dependency_overrides.clear()

