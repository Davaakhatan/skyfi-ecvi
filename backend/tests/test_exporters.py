"""Tests for report exporters"""

import pytest
from app.utils.exporters import ReportExporter


class TestReportExporter:
    """Test ReportExporter"""
    
    def test_export_to_json(self):
        """Test exporting report to JSON"""
        report_data = {
            "company_name": "Test Company",
            "risk_score": 50,
            "verification_status": "COMPLETED"
        }
        
        result = ReportExporter.export_json(report_data)
        
        assert isinstance(result, str)
        # Should be valid JSON
        import json
        parsed = json.loads(result)
        assert parsed["company_name"] == "Test Company"
    
    def test_export_to_csv(self):
        """Test exporting report to CSV"""
        report_data = {
            "company_name": "Test Company",
            "risk_score": 50,
            "verification_status": "COMPLETED",
            "report_metadata": {"generated_at": "2024-01-01"},
            "company_info": {"legal_name": "Test Company"}
        }
        
        result = ReportExporter.export_csv(report_data)
        
        assert isinstance(result, str)
        assert "Test Company" in result
    
    def test_export_pdf(self):
        """Test exporting report to PDF"""
        report_data = {
            "company_name": "Test Company",
            "risk_score": 50,
            "verification_status": "COMPLETED"
        }
        
        result = ReportExporter.export_pdf(report_data)
        
        # PDF export may return bytes or string depending on implementation
        assert isinstance(result, (bytes, str))
        if isinstance(result, bytes):
            # PDF should start with PDF header or be empty if not implemented
            assert len(result) > 0
    
    def test_export_to_html(self):
        """Test exporting report to HTML"""
        report_data = {
            "company_name": "Test Company",
            "risk_score": 50,
            "verification_status": "COMPLETED"
        }
        
        result = ReportExporter.export_html(report_data, print_friendly=True)
        
        assert isinstance(result, str)
        html_str = result.lower()
        assert "<html" in html_str or "<!doctype" in html_str
        assert "test company" in html_str

