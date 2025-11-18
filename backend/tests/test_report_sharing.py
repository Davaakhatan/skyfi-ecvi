"""Tests for report sharing service"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from app.services.report_sharing import ReportSharingService


class TestReportSharingService:
    """Test ReportSharingService"""
    
    def test_create_shareable_link(self, db_session, test_company, test_verification_result, test_user):
        """Test creating a shareable report link"""
        service = ReportSharingService(db_session)
        
        link = service.create_shareable_link(
            company_id=test_company.id,
            verification_result_id=test_verification_result.id,
            created_by=test_user.id,
            expires_in_days=7
        )
        
        assert link is not None
        assert link.company_id == test_company.id
        assert link.share_token is not None
        assert len(link.share_token) > 0
    
    def test_get_shared_report(self, db_session, test_company, test_verification_result, test_user):
        """Test getting shared report by token"""
        service = ReportSharingService(db_session)
        
        # Create shareable link
        link = service.create_shareable_link(
            company_id=test_company.id,
            verification_result_id=test_verification_result.id,
            created_by=test_user.id
        )
        
        # Get shared report
        shared = service.get_shared_report(link.share_token)
        
        assert shared is not None
        assert shared.id == link.id
        assert shared.is_active is True
    
    def test_get_shared_report_invalid_token(self, db_session):
        """Test getting shared report with invalid token"""
        service = ReportSharingService(db_session)
        
        shared = service.get_shared_report("invalid-token")
        assert shared is None
    
    def test_get_shared_report_expired(self, db_session, test_company, test_verification_result, test_user):
        """Test getting expired shared report"""
        service = ReportSharingService(db_session)
        
        # Create expired link
        link = service.create_shareable_link(
            company_id=test_company.id,
            verification_result_id=test_verification_result.id,
            created_by=test_user.id,
            expires_in_days=-1  # Already expired
        )
        
        # Manually set expiration
        link.expires_at = datetime.utcnow() - timedelta(days=1)
        db_session.commit()
        
        shared = service.get_shared_report(link.share_token)
        assert shared is None or shared.is_active is False
    
    def test_increment_access_count(self, db_session, test_company, test_verification_result, test_user):
        """Test incrementing access count"""
        service = ReportSharingService(db_session)
        
        # Create shareable link
        link = service.create_shareable_link(
            company_id=test_company.id,
            verification_result_id=test_verification_result.id,
            created_by=test_user.id
        )
        
        initial_count = link.access_count
        
        # Increment access
        service.increment_access_count(link.share_token)
        
        db_session.refresh(link)
        assert link.access_count == initial_count + 1
    
    def test_deactivate_shareable_link(self, db_session, test_company, test_verification_result, test_user):
        """Test deactivating a shareable link"""
        service = ReportSharingService(db_session)
        
        # Create shareable link
        link = service.create_shareable_link(
            company_id=test_company.id,
            verification_result_id=test_verification_result.id,
            created_by=test_user.id
        )
        
        # Deactivate
        service.deactivate_shareable_link(link.share_token)
        
        db_session.refresh(link)
        assert link.is_active is False

