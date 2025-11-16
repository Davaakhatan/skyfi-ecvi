"""Report export utilities (PDF, CSV, JSON)"""

import json
import csv
import io
from typing import Dict, Any
from datetime import datetime


class ReportExporter:
    """Service for exporting reports in various formats"""
    
    @staticmethod
    def export_json(report_data: Dict[str, Any]) -> str:
        """
        Export report as JSON
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            JSON string
        """
        return json.dumps(report_data, indent=2, default=str)
    
    @staticmethod
    def export_csv(report_data: Dict[str, Any]) -> str:
        """
        Export report as CSV
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write metadata
        metadata = report_data.get("report_metadata", {})
        writer.writerow(["Report Metadata"])
        writer.writerow(["Field", "Value"])
        for key, value in metadata.items():
            writer.writerow([key, str(value)])
        writer.writerow([])
        
        # Write company info
        company_info = report_data.get("company_info", {})
        writer.writerow(["Company Information"])
        writer.writerow(["Field", "Value"])
        for key, value in company_info.items():
            writer.writerow([key, str(value)])
        writer.writerow([])
        
        # Write risk assessment
        risk = report_data.get("risk_assessment", {})
        writer.writerow(["Risk Assessment"])
        writer.writerow(["Field", "Value"])
        for key, value in risk.items():
            writer.writerow([key, str(value)])
        writer.writerow([])
        
        # Write registration data
        registration = report_data.get("registration_data", {})
        writer.writerow(["Registration Data"])
        writer.writerow(["Field", "Value", "Source", "Verified", "Confidence"])
        for data_point in registration.get("data_points", []):
            writer.writerow([
                data_point.get("field_name", ""),
                data_point.get("field_value", ""),
                data_point.get("source", ""),
                data_point.get("verified", False),
                data_point.get("confidence_score", "")
            ])
        writer.writerow([])
        
        # Write contact information
        contact = report_data.get("contact_information", {})
        writer.writerow(["Contact Information"])
        writer.writerow(["Type", "Value", "Verified", "Confidence"])
        if contact.get("email"):
            email = contact["email"]
            writer.writerow(["Email", email.get("value", ""), email.get("verified", False), email.get("confidence", "")])
        if contact.get("phone"):
            phone = contact["phone"]
            writer.writerow(["Phone", phone.get("value", ""), phone.get("verified", False), phone.get("confidence", "")])
        writer.writerow([])
        
        # Write summary
        summary = report_data.get("summary", {})
        writer.writerow(["Summary"])
        writer.writerow(["Field", "Value"])
        for key, value in summary.items():
            if key != "key_findings":
                writer.writerow([key, str(value)])
        writer.writerow([])
        writer.writerow(["Key Findings"])
        for finding in summary.get("key_findings", []):
            writer.writerow([finding])
        
        return output.getvalue()
    
    @staticmethod
    def export_pdf(report_data: Dict[str, Any]) -> bytes:
        """
        Export report as PDF
        
        Note: This is a placeholder implementation.
        For production, use a library like reportlab or weasyprint
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            PDF bytes
        """
        # TODO: Implement PDF generation using reportlab or weasyprint
        # For now, return a simple text representation
        # In production, this should generate a proper PDF document
        
        pdf_content = f"""
VERIFICATION REPORT
===================

Report ID: {report_data.get('report_metadata', {}).get('report_id', 'N/A')}
Company: {report_data.get('report_metadata', {}).get('company_name', 'N/A')}
Generated: {report_data.get('report_metadata', {}).get('generated_at', 'N/A')}

COMPANY INFORMATION
-------------------
{json.dumps(report_data.get('company_info', {}), indent=2)}

RISK ASSESSMENT
---------------
Risk Score: {report_data.get('risk_assessment', {}).get('risk_score', 'N/A')}
Risk Category: {report_data.get('risk_assessment', {}).get('risk_category', 'N/A')}

SUMMARY
-------
{json.dumps(report_data.get('summary', {}), indent=2)}
"""
        
        # Return as bytes (in production, this would be actual PDF bytes)
        return pdf_content.encode('utf-8')
    
    @staticmethod
    def export_print_friendly(report_data: Dict[str, Any]) -> str:
        """
        Export report in print-friendly format (HTML)
        
        Args:
            report_data: Report data dictionary
        
        Returns:
            HTML string
        """
        metadata = report_data.get("report_metadata", {})
        company_info = report_data.get("company_info", {})
        risk = report_data.get("risk_assessment", {})
        summary = report_data.get("summary", {})
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Verification Report - {metadata.get('company_name', 'N/A')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            color: #333;
        }}
        .header {{
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .section {{
            margin-bottom: 30px;
            page-break-inside: avoid;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        .risk-low {{ color: green; font-weight: bold; }}
        .risk-medium {{ color: orange; font-weight: bold; }}
        .risk-high {{ color: red; font-weight: bold; }}
        @media print {{
            body {{
                margin: 0;
            }}
            .section {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Company Verification Report</h1>
        <p><strong>Report ID:</strong> {metadata.get('report_id', 'N/A')}</p>
        <p><strong>Generated:</strong> {metadata.get('generated_at', 'N/A')}</p>
    </div>
    
    <div class="section">
        <div class="section-title">Company Information</div>
        <table>
            <tr><th>Field</th><th>Value</th></tr>
            <tr><td>Legal Name</td><td>{company_info.get('legal_name', 'N/A')}</td></tr>
            <tr><td>Registration Number</td><td>{company_info.get('registration_number', 'N/A')}</td></tr>
            <tr><td>Jurisdiction</td><td>{company_info.get('jurisdiction', 'N/A')}</td></tr>
            <tr><td>Domain</td><td>{company_info.get('domain', 'N/A')}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <div class="section-title">Risk Assessment</div>
        <table>
            <tr><th>Field</th><th>Value</th></tr>
            <tr>
                <td>Risk Score</td>
                <td class="risk-{risk.get('risk_category', '').lower() if risk.get('risk_category') else ''}">
                    {risk.get('risk_score', 'N/A')} ({risk.get('risk_category', 'N/A')})
                </td>
            </tr>
            <tr><td>Verification Status</td><td>{risk.get('verification_status', 'N/A')}</td></tr>
            <tr><td>Analysis Completed</td><td>{risk.get('analysis_completed_at', 'N/A')}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <div class="section-title">Summary</div>
        <table>
            <tr><th>Field</th><th>Value</th></tr>
            <tr><td>Total Data Points</td><td>{summary.get('total_data_points', 0)}</td></tr>
            <tr><td>Verified Data Points</td><td>{summary.get('verified_data_points', 0)}</td></tr>
            <tr><td>Verification Rate</td><td>{summary.get('verification_rate', 0)}%</td></tr>
        </table>
        <h3>Key Findings</h3>
        <ul>
            {''.join(f'<li>{finding}</li>' for finding in summary.get('key_findings', []))}
        </ul>
    </div>
</body>
</html>
"""
        return html

