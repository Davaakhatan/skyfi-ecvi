"""Tests for companies API endpoints"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.db.database import get_db

client = TestClient(app)


class TestCompaniesAPI:
    """Test companies API endpoints"""
    
    def test_create_company(self, db_session, override_get_db, test_user):
        """Test creating a company"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.post(
            "/api/v1/companies",
            json={
                "legal_name": "New Company Inc",
                "registration_number": "98765432",
                "jurisdiction": "US",
                "domain": "newcompany.com"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["legal_name"] == "New Company Inc"
        assert data["registration_number"] == "98765432"
        
        app.dependency_overrides.clear()
    
    def test_create_company_invalid_domain(self, db_session, override_get_db, test_user):
        """Test creating company with invalid domain"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.post(
            "/api/v1/companies",
            json={
                "legal_name": "New Company",
                "domain": "invalid-domain"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        
        app.dependency_overrides.clear()
    
    def test_get_companies_list(self, db_session, override_get_db, test_user, test_company):
        """Test getting companies list"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.get(
            "/api/v1/companies",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1
        
        app.dependency_overrides.clear()
    
    def test_get_company_by_id(self, db_session, override_get_db, test_user, test_company):
        """Test getting company by ID"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.get(
            f"/api/v1/companies/{test_company.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_company.id)
        assert data["legal_name"] == test_company.legal_name
        
        app.dependency_overrides.clear()
    
    def test_get_company_not_found(self, db_session, override_get_db, test_user):
        """Test getting non-existent company"""
        from app.core.auth import get_current_active_user
        from uuid import uuid4
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.get(
            f"/api/v1/companies/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        
        app.dependency_overrides.clear()
    
    def test_update_company(self, db_session, override_get_db, test_user, test_company):
        """Test updating a company"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.put(
            f"/api/v1/companies/{test_company.id}",
            json={
                "legal_name": "Updated Company Name",
                "registration_number": test_company.registration_number,
                "jurisdiction": test_company.jurisdiction,
                "domain": test_company.domain
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["legal_name"] == "Updated Company Name"
        
        app.dependency_overrides.clear()
    
    def test_delete_company(self, db_session, override_get_db, test_user, test_company):
        """Test deleting a company"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.delete(
            f"/api/v1/companies/{test_company.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204
        
        # Verify company is deleted
        get_response = client.get(
            f"/api/v1/companies/{test_company.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 404
        
        app.dependency_overrides.clear()
    
    def test_get_companies_with_filters(self, db_session, override_get_db, test_user, test_company):
        """Test getting companies with filters"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.get(
            "/api/v1/companies",
            params={"search": "Test", "limit": 10},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        
        app.dependency_overrides.clear()

