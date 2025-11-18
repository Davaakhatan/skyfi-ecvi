"""Tests for authentication API endpoints"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.db.database import get_db

client = TestClient(app)


class TestAuthAPI:
    """Test authentication API endpoints"""
    
    def test_register_user(self, db_session, override_get_db):
        """Test user registration"""
        app.dependency_overrides[get_db] = override_get_db
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "password123",
                "role": "operator"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["username"] == "newuser"
        
        app.dependency_overrides.clear()
    
    def test_register_duplicate_email(self, db_session, override_get_db, test_user):
        """Test registration with duplicate email"""
        app.dependency_overrides[get_db] = override_get_db
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "username": "differentuser",
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()
        
        app.dependency_overrides.clear()
    
    def test_login_success(self, db_session, override_get_db, test_user):
        """Test successful login"""
        app.dependency_overrides[get_db] = override_get_db
        
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        app.dependency_overrides.clear()
    
    def test_login_invalid_credentials(self, db_session, override_get_db, test_user):
        """Test login with invalid credentials"""
        app.dependency_overrides[get_db] = override_get_db
        
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        
        app.dependency_overrides.clear()
    
    def test_get_current_user(self, db_session, override_get_db, test_user):
        """Test getting current user info"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        
        app.dependency_overrides.clear()
    
    def test_get_current_user_unauthorized(self):
        """Test getting current user without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

