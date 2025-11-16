"""Main verification orchestration service"""

from datetime import datetime
from typing import Dict, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.verification_result import VerificationResult, VerificationStatus, RiskCategory
from app.models.company_data import CompanyData, DataType
from app.services.dns_verification import DNSVerificationService
from app.services.risk_calculator import RiskCalculator
from app.services.contact_verification import ContactVerificationService
from app.services.registration_verification import RegistrationVerificationService
from app.utils.validators import validate_email, validate_phone, validate_domain


class VerificationService:
    """Orchestrates company verification process"""
    
    def __init__(self, db: Session):
        self.db = db
        self.dns_service = DNSVerificationService()
        self.risk_calculator = RiskCalculator()
        self.contact_service = ContactVerificationService()
        self.registration_service = RegistrationVerificationService()
    
    async def verify_company(
        self,
        company_id: UUID,
        timeout_hours: float = 2.0
    ) -> VerificationResult:
        """
        Verify a company (main orchestration method)
        
        Args:
            company_id: ID of company to verify
            timeout_hours: Maximum time to spend on verification (default 2 hours)
        
        Returns:
            VerificationResult with risk score and status
        """
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError(f"Company {company_id} not found")
        
        # Create verification result record
        verification_result = VerificationResult(
            company_id=company_id,
            risk_score=0,
            risk_category=RiskCategory.LOW,
            verification_status=VerificationStatus.IN_PROGRESS,
            analysis_started_at=datetime.utcnow()
        )
        self.db.add(verification_result)
        self.db.commit()
        
        try:
            # Step 1: DNS Verification
            dns_results = self.dns_service.verify_dns_records(company.domain or "")
            dns_verified = dns_results.get("verified", False)
            domain_age = self.dns_service.get_domain_age(company.domain or "") if company.domain else None
            ssl_valid = self.dns_service.check_ssl_certificate(company.domain or "") if company.domain else None
            domain_matches = self.dns_service.verify_domain_matches_company(
                company.domain or "", company.legal_name
            ) if company.domain else False
            
            # Store DNS data
            if company.domain:
                self._store_company_data(
                    company_id, DataType.REGISTRATION, "domain", company.domain, "dns_lookup", 1.0, dns_verified
                )
            
            # Step 2: Collect and validate contact information
            # Try to use AI service for data collection if available
            ai_collected_data = None
            try:
                from app.services.ai_service import AIOrchestrator
                ai_orchestrator = AIOrchestrator()
                if ai_orchestrator.is_available():
                    ai_result = ai_orchestrator.collect_company_data(
                        legal_name=company.legal_name,
                        registration_number=company.registration_number,
                        domain=company.domain,
                        jurisdiction=company.jurisdiction
                    )
                    if ai_result.get("success"):
                        ai_collected_data = ai_result.get("collected_data", {})
                        logger.info(f"AI data collection successful for company {company_id}")
            except Exception as e:
                logger.warning(f"AI data collection failed, falling back to basic validation: {e}")
            
            # Use AI collected data if available, otherwise use basic validation
            email_valid = False
            phone_valid = False
            email_exists = None
            phone_carrier_valid = None
            
            # If we have contact info in company data, verify it
            # TODO: Extract contact info from company_data or AI collection
            # For now, placeholder values
            
            # Step 3: Registration data consistency
            registration_result = self.registration_service.cross_reference_registration_data(
                legal_name=company.legal_name,
                registration_number=company.registration_number,
                jurisdiction=company.jurisdiction,
                domain=company.domain
            )
            registration_matches = registration_result.get("matches", 0)
            total_sources = registration_result.get("total_sources", 0)
            
            # Store registration data
            if company.registration_number:
                reg_verify = self.registration_service.verify_registration_number(
                    company.registration_number, company.jurisdiction
                )
                self._store_company_data(
                    company_id,
                    DataType.REGISTRATION,
                    "registration_number",
                    company.registration_number,
                    "format_validation",
                    0.8 if reg_verify["verified"] else 0.3,
                    reg_verify["verified"]
                )
            
            # Step 4: Calculate risk score
            risk_result = self.risk_calculator.calculate_overall_risk(
                dns_verified=dns_verified,
                domain_age_days=domain_age,
                registration_matches=registration_matches,
                total_sources=total_sources,
                email_valid=email_valid,
                phone_valid=phone_valid,
                email_exists=email_exists,
                phone_carrier_valid=phone_carrier_valid,
                domain_matches_company=domain_matches,
                ssl_valid=ssl_valid,
                suspicious_keywords=0,  # TODO: Implement keyword detection
                data_consistency_score=0.8,  # TODO: Calculate from actual data
                source_reliability_avg=0.7  # TODO: Calculate from source reliability
            )
            
            # Update verification result
            verification_result.risk_score = risk_result["risk_score"]
            verification_result.risk_category = risk_result["risk_category"]
            verification_result.verification_status = VerificationStatus.COMPLETED
            verification_result.analysis_completed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(verification_result)
            
            return verification_result
            
        except Exception as e:
            # Mark as failed
            try:
                verification_result.verification_status = VerificationStatus.FAILED
                verification_result.analysis_completed_at = datetime.utcnow()
                self.db.commit()
            except Exception as commit_error:
                logger.error(f"Failed to commit verification failure status: {commit_error}")
                self.db.rollback()
            raise
    
    def _store_company_data(
        self,
        company_id: UUID,
        data_type: DataType,
        field_name: str,
        field_value: str,
        source: str,
        confidence_score: float,
        verified: bool
    ):
        """Store company data in database"""
        try:
            company_data = CompanyData(
                company_id=company_id,
                data_type=data_type,
                field_name=field_name,
                field_value=field_value,
                source=source,
                confidence_score=confidence_score,
                verified=verified
            )
            self.db.add(company_data)
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to store company data: {e}")
            self.db.rollback()
            raise
    
    def get_verification_result(self, company_id: UUID) -> Optional[VerificationResult]:
        """Get latest verification result for a company"""
        return self.db.query(VerificationResult).filter(
            VerificationResult.company_id == company_id
        ).order_by(VerificationResult.created_at.desc()).first()

