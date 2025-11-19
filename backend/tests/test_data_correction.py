"""Tests for data correction service"""

import pytest
from uuid import uuid4
from datetime import datetime
from app.services.data_correction import DataCorrectionService
from app.models.data_correction import CorrectionStatus


class TestDataCorrectionService:
    """Test DataCorrectionService"""
    
    def test_create_correction(self, db_session, test_company, test_user):
        """Test creating a data correction"""
        service = DataCorrectionService(db_session)
        correction = service.create_correction(
            company_id=test_company.id,
            field_name="legal_name",
            field_type="legal_name",
            old_value=test_company.legal_name,
            new_value="New Name",
            correction_reason="Updated information",
            corrected_by=test_user.id
        )
        assert correction.company_id == test_company.id
        assert correction.field_name == "legal_name"
        assert correction.old_value == test_company.legal_name
        assert correction.new_value == "New Name"
        assert correction.status == CorrectionStatus.PENDING
        assert correction.version == "1.0"
    
    def test_create_correction_with_versioning(self, db_session, test_company, test_user):
        """Test correction versioning"""
        service = DataCorrectionService(db_session)
        
        # Create first correction
        correction1 = service.create_correction(
            company_id=test_company.id,
            field_name="legal_name",
            field_type="legal_name",
            old_value=test_company.legal_name,
            new_value="New Name",
            correction_reason="First correction",
            corrected_by=test_user.id
        )
        
        # Approve first correction
        service.approve_correction(correction1.id, test_user.id)
        
        # Create second correction
        correction2 = service.create_correction(
            company_id=test_company.id,
            field_name="legal_name",
            field_type="legal_name",
            old_value="New Name",
            new_value="Newer Name",
            correction_reason="Second correction",
            corrected_by=test_user.id
        )
        
        assert correction2.version == "1.1"
        assert correction2.previous_correction_id == correction1.id
    
    def test_approve_correction(self, db_session, test_company, test_user):
        """Test approving a correction"""
        service = DataCorrectionService(db_session)
        
        # Create correction
        correction = service.create_correction(
            company_id=test_company.id,
            field_name="legal_name",
            field_type="legal_name",
            old_value=test_company.legal_name,
            new_value="Updated Name",
            correction_reason="Update name",
            corrected_by=test_user.id
        )
        
        # Approve correction
        approved = service.approve_correction(correction.id, test_user.id)
        
        assert approved.status == CorrectionStatus.APPROVED
        assert approved.approved_by == test_user.id
        assert approved.approved_at is not None
        
        # Verify company was updated
        db_session.refresh(test_company)
        assert test_company.legal_name == "Updated Name"
    
    def test_approve_correction_already_approved(self, db_session, test_company, test_user):
        """Test approving an already approved correction"""
        service = DataCorrectionService(db_session)
        
        correction = service.create_correction(
            company_id=test_company.id,
            field_name="legal_name",
            field_type="legal_name",
            old_value="Old",
            new_value="New",
            correction_reason="Test",
            corrected_by=test_user.id
        )
        
        service.approve_correction(correction.id, test_user.id)
        
        # Try to approve again
        with pytest.raises(ValueError, match="not pending"):
            service.approve_correction(correction.id, test_user.id)
    
    def test_reject_correction(self, db_session, test_company, test_user):
        """Test rejecting a correction"""
        service = DataCorrectionService(db_session)
        
        correction = service.create_correction(
            company_id=test_company.id,
            field_name="legal_name",
            field_type="legal_name",
            old_value=test_company.legal_name,
            new_value="New",
            correction_reason="Test",
            corrected_by=test_user.id
        )
        
        rejected = service.reject_correction(
            correction.id,
            test_user.id,
            "Invalid correction"
        )
        
        assert rejected.status == CorrectionStatus.REJECTED
        assert rejected.approved_by == test_user.id
        assert rejected.correction_metadata is not None
        assert rejected.correction_metadata.get("rejection_reason") == "Invalid correction"
    
    def test_get_correction_history(self, db_session, test_company, test_user):
        """Test getting correction history"""
        service = DataCorrectionService(db_session)
        
        # Create multiple corrections
        for i in range(3):
            service.create_correction(
                company_id=test_company.id,
                field_name=f"field_{i}",
                field_type="legal_name",
                old_value=f"Old {i}",
                new_value=f"New {i}",
                correction_reason=f"Correction {i}",
                corrected_by=test_user.id
            )
        
        history = service.get_correction_history(test_company.id)
        assert len(history) >= 3
    
    def test_get_correction_history_with_field_filter(self, db_session, test_company, test_user):
        """Test getting correction history filtered by field"""
        service = DataCorrectionService(db_session)
        
        # Create corrections for different fields
        service.create_correction(
            company_id=test_company.id,
            field_name="legal_name",
            field_type="legal_name",
            old_value=test_company.legal_name,
            new_value="New",
            correction_reason="Test",
            corrected_by=test_user.id
        )
        service.create_correction(
            company_id=test_company.id,
            field_name="domain",
            field_type="domain",
            old_value=test_company.domain,
            new_value="new.com",
            correction_reason="Test",
            corrected_by=test_user.id
        )
        
        history = service.get_correction_history(test_company.id, field_name="legal_name")
        assert len(history) == 1
        assert history[0].field_name == "legal_name"
    
    def test_get_latest_correction(self, db_session, test_company, test_user):
        """Test getting latest correction for a field"""
        service = DataCorrectionService(db_session)
        
        # Create and approve first correction
        correction1 = service.create_correction(
            company_id=test_company.id,
            field_name="legal_name",
            field_type="legal_name",
            old_value=test_company.legal_name,
            new_value="New",
            correction_reason="First",
            corrected_by=test_user.id
        )
        service.approve_correction(correction1.id, test_user.id)
        
        # Create second correction (not approved)
        correction2 = service.create_correction(
            company_id=test_company.id,
            field_name="legal_name",
            field_type="legal_name",
            old_value="New",
            new_value="Newer",
            correction_reason="Second",
            corrected_by=test_user.id
        )
        
        latest = service.get_latest_correction(test_company.id, "legal_name")
        assert latest is not None
        assert latest.id == correction1.id  # Should return approved one
    
    def test_approve_correction_updates_company_data(self, db_session, test_company, test_user):
        """Test that approving correction updates company data"""
        from app.models.company_data import CompanyData, DataType
        
        service = DataCorrectionService(db_session)
        
        # Create company data
        company_data = CompanyData(
            company_id=test_company.id,
            data_type=DataType.CONTACT,
            field_name="email",
            field_value="old@example.com",
            source="test",
            confidence_score=0.8,
            verified=False
        )
        db_session.add(company_data)
        db_session.commit()
        
        # Create correction for company data
        correction = service.create_correction(
            company_id=test_company.id,
            field_name="email",
            field_type="email",
            old_value="old@example.com",
            new_value="new@example.com",
            correction_reason="Update email",
            corrected_by=test_user.id,
            company_data_id=company_data.id
        )
        
        # Approve correction
        service.approve_correction(correction.id, test_user.id)
        
        # Verify company data was updated
        db_session.refresh(company_data)
        assert company_data.field_value == "new@example.com"
        assert company_data.verified is True

