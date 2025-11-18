"""Tests for verification service"""

import pytest
from uuid import uuid4
from app.services.verification_service import VerificationService
from app.models.verification_result import VerificationStatus, RiskCategory


class TestVerificationService:
    """Test VerificationService"""
    
    def test_verify_company_creates_result(self, db_session, test_company):
        """Test that verify_company creates a verification result"""
        service = VerificationService(db_session)
        
        result = service.verify_company(test_company.id)
        
        assert result is not None
        assert result.company_id == test_company.id
        assert result.verification_status in [VerificationStatus.COMPLETED, VerificationStatus.FAILED]
    
    def test_get_verification_result(self, db_session, test_company, test_verification_result):
        """Test getting verification result"""
        service = VerificationService(db_session)
        
        result = service.get_verification_result(test_company.id)
        
        assert result is not None
        assert result.company_id == test_company.id
        assert result.id == test_verification_result.id
    
    def test_get_verification_result_none(self, db_session, test_company):
        """Test getting verification result when none exists"""
        from uuid import uuid4
        service = VerificationService(db_session)
        
        # Use a different company ID
        result = service.get_verification_result(uuid4())
        
        assert result is None
    
    def test_store_company_data(self, db_session, test_company):
        """Test storing company data"""
        from app.models.company_data import DataType
        service = VerificationService(db_session)
        
        service._store_company_data(
            company_id=test_company.id,
            data_type=DataType.REGISTRATION,
            field_name="registration_number",
            field_value="12345678",
            source="test",
            confidence_score=0.9,
            verified=True
        )
        
        # Verify data was stored
        from app.models.company_data import CompanyData
        data = db_session.query(CompanyData).filter(
            CompanyData.company_id == test_company.id
        ).first()
        
        assert data is not None
        assert data.field_name == "registration_number"
        assert data.field_value == "12345678"

