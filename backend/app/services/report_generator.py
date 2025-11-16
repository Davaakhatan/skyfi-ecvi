"""Verification report generation service"""

from typing import Dict, List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.company import Company
from app.models.verification_result import VerificationResult, VerificationStatus
from app.models.company_data import CompanyData, DataType
from app.services.risk_history import RiskHistoryService
from app.services.confidence_scoring import ConfidenceScoringService
from app.services.discrepancy_detection import DiscrepancyDetectionService


class ReportGenerator:
    """Service for generating verification reports"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_report(
        self,
        company_id: UUID,
        verification_result_id: Optional[UUID] = None
    ) -> Dict:
        """
        Generate comprehensive verification report
        
        Optimized to minimize database queries and improve performance.
        Target: < 30 seconds for report generation.
        
        Args:
            company_id: Company ID
            verification_result_id: Optional specific verification result ID
        
        Returns:
            Dictionary with complete report data
        """
        # Optimize: Single query to get company with relationships
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError(f"Company {company_id} not found")
        
        # Optimize: Get verification result with single query
        if verification_result_id:
            verification_result = self.db.query(VerificationResult).filter(
                VerificationResult.id == verification_result_id,
                VerificationResult.company_id == company_id
            ).first()
        else:
            verification_result = self.db.query(VerificationResult).filter(
                VerificationResult.company_id == company_id,
                VerificationResult.verification_status == VerificationStatus.COMPLETED
            ).order_by(desc(VerificationResult.created_at)).first()
        
        if not verification_result:
            raise ValueError(f"No verification result found for company {company_id}")
        
        # Optimize: Single query to get all company data (eager loading)
        company_data = self.db.query(CompanyData).filter(
            CompanyData.company_id == company_id
        ).all()
        
        # Build report sections (optimized: process data once, reuse in multiple sections)
        # Pre-process company_data to avoid repeated filtering
        registration_data = [d for d in company_data if d.data_type == DataType.REGISTRATION]
        contact_data = [d for d in company_data if d.data_type == DataType.CONTACT]
        address_data = [d for d in company_data if d.data_type == DataType.ADDRESS]
        
        # Build report sections (reuse pre-filtered data)
        report = {
            "report_metadata": self._generate_metadata(company, verification_result),
            "company_info": self._generate_company_info(company),
            "risk_assessment": self._generate_risk_assessment(verification_result),
            "registration_data": self._generate_registration_section(company, registration_data),
            "contact_information": self._generate_contact_section(contact_data),
            "address_information": self._generate_address_section(address_data),
            "verification_details": self._generate_verification_details(verification_result, company_data),
            "data_sources": self._generate_data_sources(company_data),
            "confidence_scores": self._generate_confidence_scores(company_data, verification_result),
            "discrepancies": self._generate_discrepancies(company, company_data),
            "summary": self._generate_summary(company, verification_result, company_data)
        }
        
        return report
    
    def _generate_metadata(self, company: Company, verification_result: VerificationResult) -> Dict:
        """Generate report metadata"""
        return {
            "report_id": str(verification_result.id),
            "company_id": str(company.id),
            "company_name": company.legal_name,
            "generated_at": datetime.utcnow().isoformat(),
            "verification_date": verification_result.analysis_completed_at.isoformat() if verification_result.analysis_completed_at else None,
            "verification_status": verification_result.verification_status.value
        }
    
    def _generate_company_info(self, company: Company) -> Dict:
        """Generate company information section"""
        return {
            "legal_name": company.legal_name,
            "registration_number": company.registration_number,
            "jurisdiction": company.jurisdiction,
            "domain": company.domain,
            "created_at": company.created_at.isoformat() if company.created_at else None,
            "updated_at": company.updated_at.isoformat() if company.updated_at else None
        }
    
    def _generate_risk_assessment(self, verification_result: VerificationResult) -> Dict:
        """Generate risk assessment section"""
        return {
            "risk_score": verification_result.risk_score,
            "risk_category": verification_result.risk_category.value if verification_result.risk_category else None,
            "analysis_started_at": verification_result.analysis_started_at.isoformat() if verification_result.analysis_started_at else None,
            "analysis_completed_at": verification_result.analysis_completed_at.isoformat() if verification_result.analysis_completed_at else None,
            "verification_status": verification_result.verification_status.value
        }
    
    def _generate_registration_section(
        self,
        company: Company,
        registration_data: List[CompanyData]
    ) -> Dict:
        """Generate company registration data section"""
        
        section = {
            "legal_name": company.legal_name,
            "registration_number": company.registration_number,
            "jurisdiction": company.jurisdiction,
            "domain": company.domain,
            "verified_fields": [],
            "data_points": []
        }
        
        for data in registration_data:
            section["data_points"].append({
                "field_name": data.field_name,
                "field_value": data.field_value,
                "source": data.source,
                "confidence_score": float(data.confidence_score) if data.confidence_score else None,
                "verified": data.verified,
                "collected_at": data.created_at.isoformat() if data.created_at else None
            })
            
            if data.verified:
                section["verified_fields"].append(data.field_name)
        
        return section
    
    def _generate_contact_section(self, contact_data: List[CompanyData]) -> Dict:
        """Generate contact information section"""
        
        section = {
            "email": None,
            "phone": None,
            "data_points": []
        }
        
        for data in contact_data:
            data_point = {
                "field_name": data.field_name,
                "field_value": data.field_value,
                "source": data.source,
                "confidence_score": float(data.confidence_score) if data.confidence_score else None,
                "verified": data.verified,
                "collected_at": data.created_at.isoformat() if data.created_at else None
            }
            
            section["data_points"].append(data_point)
            
            # Extract email and phone if available
            if data.field_name == "email":
                section["email"] = {
                    "value": data.field_value,
                    "verified": data.verified,
                    "confidence": float(data.confidence_score) if data.confidence_score else None
                }
            elif data.field_name == "phone":
                section["phone"] = {
                    "value": data.field_value,
                    "verified": data.verified,
                    "confidence": float(data.confidence_score) if data.confidence_score else None
                }
        
        return section
    
    def _generate_address_section(self, address_data: List[CompanyData]) -> Dict:
        """Generate HQ address section"""
        
        section = {
            "address": {},
            "data_points": []
        }
        
        for data in address_data:
            data_point = {
                "field_name": data.field_name,
                "field_value": data.field_value,
                "source": data.source,
                "confidence_score": float(data.confidence_score) if data.confidence_score else None,
                "verified": data.verified,
                "collected_at": data.created_at.isoformat() if data.created_at else None
            }
            
            section["data_points"].append(data_point)
            
            # Build address dictionary
            if data.field_name in ["street", "city", "state", "country", "postal_code"]:
                section["address"][data.field_name] = {
                    "value": data.field_value,
                    "verified": data.verified,
                    "confidence": float(data.confidence_score) if data.confidence_score else None
                }
        
        return section
    
    def _generate_verification_details(
        self,
        verification_result: VerificationResult,
        company_data: List[CompanyData]
    ) -> Dict:
        """Generate verification details section"""
        verified_count = sum(1 for d in company_data if d.verified)
        total_count = len(company_data)
        
        return {
            "verification_id": str(verification_result.id),
            "verification_status": verification_result.verification_status.value,
            "total_data_points": total_count,
            "verified_data_points": verified_count,
            "verification_rate": round(verified_count / total_count * 100, 2) if total_count > 0 else 0,
            "analysis_duration": self._calculate_duration(
                verification_result.analysis_started_at,
                verification_result.analysis_completed_at
            )
        }
    
    def _generate_data_sources(self, company_data: List[CompanyData]) -> Dict:
        """Generate data source attribution section"""
        sources = {}
        
        for data in company_data:
            source = data.source or "unknown"
            if source not in sources:
                sources[source] = {
                    "source_name": source,
                    "data_points_count": 0,
                    "verified_count": 0,
                    "average_confidence": 0.0,
                    "data_types": set()
                }
            
            sources[source]["data_points_count"] += 1
            if data.verified:
                sources[source]["verified_count"] += 1
            sources[source]["data_types"].add(data.data_type.value)
        
        # Calculate averages and convert sets to lists
        result = []
        for source_name, source_data in sources.items():
            confidences = [
                float(d.confidence_score) for d in company_data
                if d.source == source_name and d.confidence_score is not None
            ]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            result.append({
                "source_name": source_name,
                "data_points_count": source_data["data_points_count"],
                "verified_count": source_data["verified_count"],
                "verification_rate": round(
                    source_data["verified_count"] / source_data["data_points_count"] * 100, 2
                ) if source_data["data_points_count"] > 0 else 0,
                "average_confidence": round(avg_confidence, 3),
                "data_types": list(source_data["data_types"])
            })
        
        return {
            "total_sources": len(result),
            "sources": result
        }
    
    def _generate_confidence_scores(
        self,
        company_data: List[CompanyData],
        verification_result: VerificationResult
    ) -> Dict:
        """Generate confidence scores section"""
        # Calculate average confidence by data type
        confidence_by_type = {}
        
        for data in company_data:
            data_type = data.data_type.value
            if data_type not in confidence_by_type:
                confidence_by_type[data_type] = []
            
            if data.confidence_score is not None:
                confidence_by_type[data_type].append(float(data.confidence_score))
        
        # Calculate averages
        averages = {}
        for data_type, scores in confidence_by_type.items():
            averages[data_type] = round(sum(scores) / len(scores), 3) if scores else 0.0
        
        # Calculate overall confidence
        all_scores = [
            float(d.confidence_score) for d in company_data
            if d.confidence_score is not None
        ]
        overall_confidence = round(sum(all_scores) / len(all_scores), 3) if all_scores else 0.0
        
        return {
            "overall_confidence": overall_confidence,
            "confidence_by_type": averages,
            "total_data_points": len(company_data),
            "data_points_with_confidence": len(all_scores)
        }
    
    def _generate_discrepancies(
        self,
        company: Company,
        company_data: List[CompanyData]
    ) -> Dict:
        """Generate discrepancies section"""
        # Group data by field name to find discrepancies
        field_data = {}
        
        for data in company_data:
            field_name = data.field_name
            if field_name not in field_data:
                field_data[field_name] = []
            
            field_data[field_name].append({
                "value": data.field_value,
                "source": data.source,
                "confidence": float(data.confidence_score) if data.confidence_score else None,
                "verified": data.verified
            })
        
        discrepancies = []
        matches = []
        
        for field_name, values in field_data.items():
            if len(values) > 1:
                # Multiple sources for same field - check for discrepancies
                unique_values = set(v["value"] for v in values if v["value"])
                
                if len(unique_values) > 1:
                    # Discrepancy found
                    discrepancies.append({
                        "field_name": field_name,
                        "values": [
                            {
                                "value": v["value"],
                                "source": v["source"],
                                "confidence": v["confidence"],
                                "verified": v["verified"]
                            }
                            for v in values
                        ],
                        "discrepancy_type": "value_mismatch"
                    })
                else:
                    # All values match
                    matches.append({
                        "field_name": field_name,
                        "value": values[0]["value"],
                        "sources": [v["source"] for v in values],
                        "verified": all(v["verified"] for v in values)
                    })
        
        return {
            "total_discrepancies": len(discrepancies),
            "total_matches": len(matches),
            "discrepancies": discrepancies,
            "matches": matches
        }
    
    def _generate_summary(
        self,
        company: Company,
        verification_result: VerificationResult,
        company_data: List[CompanyData]
    ) -> Dict:
        """Generate report summary"""
        verified_count = sum(1 for d in company_data if d.verified)
        total_count = len(company_data)
        
        return {
            "company_name": company.legal_name,
            "risk_score": verification_result.risk_score,
            "risk_category": verification_result.risk_category.value if verification_result.risk_category else None,
            "verification_status": verification_result.verification_status.value,
            "total_data_points": total_count,
            "verified_data_points": verified_count,
            "verification_rate": round(verified_count / total_count * 100, 2) if total_count > 0 else 0,
            "key_findings": self._generate_key_findings(verification_result, company_data)
        }
    
    def _generate_key_findings(
        self,
        verification_result: VerificationResult,
        company_data: List[CompanyData]
    ) -> List[str]:
        """Generate key findings summary"""
        findings = []
        
        # Risk score findings
        if verification_result.risk_score <= 30:
            findings.append("Low risk score indicates reliable company information")
        elif verification_result.risk_score > 70:
            findings.append("High risk score - multiple verification concerns identified")
        else:
            findings.append("Moderate risk score - some verification concerns present")
        
        # Verification findings
        verified_count = sum(1 for d in company_data if d.verified)
        total_count = len(company_data)
        
        if verified_count == total_count and total_count > 0:
            findings.append("All data points successfully verified")
        elif verified_count == 0:
            findings.append("No data points verified - manual review recommended")
        else:
            findings.append(f"{verified_count} of {total_count} data points verified")
        
        # Domain findings
        domain_data = [d for d in company_data if d.field_name == "domain" and d.verified]
        if domain_data:
            findings.append("Domain verification successful")
        else:
            domain_data = [d for d in company_data if d.field_name == "domain"]
            if domain_data:
                findings.append("Domain verification incomplete or failed")
        
        return findings
    
    def _calculate_duration(
        self,
        start: Optional[datetime],
        end: Optional[datetime]
    ) -> Optional[str]:
        """Calculate duration between two timestamps"""
        if not start or not end:
            return None
        
        duration = end - start
        total_seconds = int(duration.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

