"""Tests for reviews API endpoints"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.db.database import get_db

client = TestClient(app)


class TestReviewsAPI:
    """Test reviews API endpoints"""
    
    def test_create_review(self, db_session, override_get_db, test_user, test_company):
        """Test creating a review"""
        from app.core.auth import get_current_active_user
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.post(
            f"/api/v1/reviews/company/{test_company.id}",
            json={
                "status": "REVIEWED",
                "notes": "Company looks legitimate"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "REVIEWED"
        assert data["notes"] == "Company looks legitimate"
        
        app.dependency_overrides.clear()
    
    def test_get_review(self, db_session, override_get_db, test_user, test_company):
        """Test getting a review"""
        from app.core.auth import get_current_active_user
        from app.models.review import Review, ReviewStatus
        
        # Create review first
        review = Review(
            company_id=test_company.id,
            reviewer_id=test_user.id,
            status=ReviewStatus.REVIEWED,
            notes="Test review"
        )
        db_session.add(review)
        db_session.commit()
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.get(
            f"/api/v1/reviews/company/{test_company.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "REVIEWED"
        
        app.dependency_overrides.clear()
    
    def test_update_review(self, db_session, override_get_db, test_user, test_company):
        """Test updating a review"""
        from app.core.auth import get_current_active_user
        from app.models.review import Review, ReviewStatus
        
        # Create review first
        review = Review(
            company_id=test_company.id,
            reviewer_id=test_user.id,
            status=ReviewStatus.REVIEWED,
            notes="Original notes"
        )
        db_session.add(review)
        db_session.commit()
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.put(
            f"/api/v1/reviews/{review.id}",
            json={
                "status": "FLAGGED",
                "notes": "Updated notes - flagged for review"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "FLAGGED"
        assert "Updated notes" in data["notes"]
        
        app.dependency_overrides.clear()
    
    def test_get_reviews_bulk(self, db_session, override_get_db, test_user, test_company):
        """Test getting reviews in bulk"""
        from app.core.auth import get_current_active_user
        from app.models.review import Review, ReviewStatus
        
        # Create multiple reviews
        for i in range(3):
            review = Review(
                company_id=test_company.id,
                reviewer_id=test_user.id,
                status=ReviewStatus.REVIEWED,
                notes=f"Review {i}"
            )
            db_session.add(review)
        db_session.commit()
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = lambda: test_user
        
        token = create_access_token(data={"sub": test_user.email})
        response = client.post(
            "/api/v1/reviews/bulk",
            json={"company_ids": [str(test_company.id)]},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        app.dependency_overrides.clear()

