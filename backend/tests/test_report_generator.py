"""Tests for report generator service"""

import pytest
from app.services.report_generator import ReportGenerator
from app.models.company_data import DataType


class TestReportGenerator:
    """Test ReportGenerator"""
    
    def test_generate_report(self, db_session, test_company, test_verification_result):
        """Test generating a verification report"""
        from app.models.company_data import CompanyData
        
        # Create some company data
        company_data = CompanyData(
            company_id=test_company.id,
            data_type=DataType.REGISTRATION,
            field_name="registration_number",
            field_value=test_company.registration_number,
            source="test",
            confidence_score=0.9,
            verified=True
        )
        db_session.add(company_data)
        db_session.commit()
        
        generator = ReportGenerator(db_session)
        report = generator.generate_report(test_company.id, test_verification_result.id)
        
        assert report is not None
        assert "company_info" in report
        assert "risk_assessment" in report
        assert "verification_details" in report
        assert report["company_info"]["legal_name"] == test_company.legal_name
    
    def test_generate_report_no_data(self, db_session, test_company, test_verification_result):
        """Test generating report with no company data"""
        generator = ReportGenerator(db_session)
        report = generator.generate_report(test_company.id, test_verification_result.id)
        
        assert report is not None
        assert "company_info" in report
    
    def test_generate_contact_section(self, db_session, test_company):
        """Test generating contact section"""
        from app.models.company_data import CompanyData
        
        # Create contact data
        email_data = CompanyData(
            company_id=test_company.id,
            data_type=DataType.CONTACT,
            field_name="email",
            field_value="test@example.com",
            source="test",
            confidence_score=0.8,
            verified=True
        )
        phone_data = CompanyData(
            company_id=test_company.id,
            data_type=DataType.CONTACT,
            field_name="phone",
            field_value="+1234567890",
            source="test",
            confidence_score=0.7,
            verified=False
        )
        db_session.add(email_data)
        db_session.add(phone_data)
        db_session.commit()
        
        generator = ReportGenerator(db_session)
        contact_data = db_session.query(CompanyData).filter(
            CompanyData.company_id == test_company.id,
            CompanyData.data_type == DataType.CONTACT
        ).all()
        
        section = generator._generate_contact_section(contact_data)
        
        assert section["email"] is not None
        assert section["email"]["value"] == "test@example.com"
        assert section["phone"] is not None
        assert section["phone"]["value"] == "+1234567890"

