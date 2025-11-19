"""Tests for report sharing service"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from app.services.report_sharing import ReportSharingService


class TestReportSharingService:
    """Test ReportSharingService"""
    
    def test_create_shareable_link(self, db_session, test_company, test_verification_result, test_user):
        """Test creating a shareable report link"""
        link = ReportSharingService.create_shareable_link(
            db=db_session,
            company_id=test_company.id,
            verification_result_id=test_verification_result.id,
            created_by=test_user.id,
            expires_in_days=7
        )
        
        assert link is not None
        assert "share_token" in link
        assert link["share_token"] is not None
        assert len(link["share_token"]) > 0
    
    def test_get_shared_report(self, db_session, test_company, test_verification_result, test_user):
        """Test getting shared report by token"""
        # Create shareable link
        link = ReportSharingService.create_shareable_link(
            db=db_session,
            company_id=test_company.id,
            verification_result_id=test_verification_result.id,
            created_by=test_user.id
        )
        
        # Get shared report
        shared = ReportSharingService.get_shared_report(db_session, link["share_token"])
        
        assert shared is not None
        assert shared.company_id == test_company.id
        assert shared.is_active is True
    
    def test_get_shared_report_invalid_token(self, db_session):
        """Test getting shared report with invalid token"""
        shared = ReportSharingService.get_shared_report(db_session, "invalid-token")
        assert shared is None
    
    def test_get_shared_report_expired(self, db_session, test_company, test_verification_result, test_user):
        """Test getting expired shared report"""
        from app.services.report_sharing import SharedReport
        
        # Create expired link
        link = ReportSharingService.create_shareable_link(
            db=db_session,
            company_id=test_company.id,
            verification_result_id=test_verification_result.id,
            created_by=test_user.id,
            expires_in_days=1
        )
        
        # Manually set expiration
        shared_report = db_session.query(SharedReport).filter(
            SharedReport.share_token == link["share_token"]
        ).first()
        shared_report.expires_at = datetime.utcnow() - timedelta(days=1)
        db_session.commit()
        
        shared = ReportSharingService.get_shared_report(db_session, link["share_token"])
        assert shared is None
    
    def test_increment_access_count(self, db_session, test_company, test_verification_result, test_user):
        """Test incrementing access count"""
        from app.services.report_sharing import SharedReport
        
        # Create shareable link
        link = ReportSharingService.create_shareable_link(
            db=db_session,
            company_id=test_company.id,
            verification_result_id=test_verification_result.id,
            created_by=test_user.id
        )
        
        shared_report = db_session.query(SharedReport).filter(
            SharedReport.share_token == link["share_token"]
        ).first()
        initial_count = shared_report.access_count
        
        # Increment access (this happens automatically in get_shared_report)
        ReportSharingService.get_shared_report(db_session, link["share_token"])
        
        db_session.refresh(shared_report)
        assert shared_report.access_count == initial_count + 1
    
    def test_deactivate_shareable_link(self, db_session, test_company, test_verification_result, test_user):
        """Test deactivating a shareable link"""
        from app.services.report_sharing import SharedReport
        
        # Create shareable link
        link = ReportSharingService.create_shareable_link(
            db=db_session,
            company_id=test_company.id,
            verification_result_id=test_verification_result.id,
            created_by=test_user.id
        )
        
        # Deactivate (revoke)
        result = ReportSharingService.revoke_shareable_link(
            db=db_session,
            share_token=link["share_token"]
        )
        assert result is True
        
        shared_report = db_session.query(SharedReport).filter(
            SharedReport.share_token == link["share_token"]
        ).first()
        assert shared_report.is_active is False

