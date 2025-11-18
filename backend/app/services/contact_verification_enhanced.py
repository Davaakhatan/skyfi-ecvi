"""Enhanced contact verification service with external API integration support"""

from typing import Dict, Optional, List
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.contact_verification import ContactVerificationResult, ContactType, ContactVerificationStatus
from app.services.contact_verification import ContactVerificationService
from app.services.risk_calculator import RiskCalculator


class EnhancedContactVerificationService:
    """Enhanced service for contact verification with database persistence and risk scoring"""
    
    def __init__(self, db: Session):
        self.db = db
        self.contact_service = ContactVerificationService()
    
    def verify_and_store_email(
        self,
        company_id: UUID,
        verification_result_id: Optional[UUID],
        email: str
    ) -> ContactVerificationResult:
        """Verify email and store result in database"""
        # Verify email using existing service
        verification_result = self.contact_service.verify_email(email)
        
        # Calculate confidence score
        confidence = self._calculate_email_confidence(verification_result)
        
        # Calculate risk score
        risk_score = RiskCalculator.calculate_contact_validation_risk(
            email_valid=verification_result["format_valid"],
            phone_valid=False,
            email_exists=verification_result.get("email_exists"),
            phone_carrier_valid=None
        )
        
        # Determine status
        status = self._determine_email_status(verification_result)
        
        # Store in database
        contact_verification = ContactVerificationResult(
            company_id=company_id,
            verification_result_id=verification_result_id,
            contact_type=ContactType.EMAIL,
            contact_value=email,
            format_valid=verification_result["format_valid"],
            domain_exists=verification_result.get("domain_exists"),
            mx_record_exists=verification_result.get("mx_record_exists"),
            email_exists=verification_result.get("email_exists"),
            status=status,
            confidence_score=confidence,
            risk_score=risk_score,
            verification_details={
                "mx_records": verification_result.get("mx_records", []),
                "domain": email.split("@")[1] if "@" in email else None
            },
            errors=verification_result.get("errors", []),
            sources_checked=["dns", "smtp"],
            verified_at=datetime.utcnow() if status != ContactVerificationStatus.PENDING else None
        )
        
        try:
            self.db.add(contact_verification)
            self.db.commit()
            self.db.refresh(contact_verification)
            return contact_verification
        except Exception as e:
            self.db.rollback()
            raise
    
    def verify_and_store_phone(
        self,
        company_id: UUID,
        verification_result_id: Optional[UUID],
        phone: str,
        country_code: Optional[str] = None
    ) -> ContactVerificationResult:
        """Verify phone and store result in database"""
        # Verify phone using existing service
        verification_result = self.contact_service.verify_phone(phone, country_code)
        
        # Calculate confidence score
        confidence = self._calculate_phone_confidence(verification_result)
        
        # Calculate risk score
        risk_score = RiskCalculator.calculate_contact_validation_risk(
            email_valid=False,
            phone_valid=verification_result["format_valid"],
            email_exists=None,
            phone_carrier_valid=verification_result.get("carrier_valid")
        )
        
        # Determine status
        status = self._determine_phone_status(verification_result)
        
        # Store in database
        contact_verification = ContactVerificationResult(
            company_id=company_id,
            verification_result_id=verification_result_id,
            contact_type=ContactType.PHONE,
            contact_value=phone,
            country_code=country_code,
            format_valid=verification_result["format_valid"],
            carrier_valid=verification_result.get("carrier_valid"),
            carrier_name=verification_result.get("carrier_name"),
            line_type=verification_result.get("line_type"),
            status=status,
            confidence_score=confidence,
            risk_score=risk_score,
            verification_details={
                "cleaned_number": phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            },
            errors=verification_result.get("errors", []),
            sources_checked=["format_validation"],
            verified_at=datetime.utcnow() if status != ContactVerificationStatus.PENDING else None
        )
        
        try:
            self.db.add(contact_verification)
            self.db.commit()
            self.db.refresh(contact_verification)
            return contact_verification
        except Exception as e:
            self.db.rollback()
            raise
    
    def verify_and_store_name(
        self,
        company_id: UUID,
        verification_result_id: Optional[UUID],
        name: str
    ) -> ContactVerificationResult:
        """Verify name against public records and social profiles"""
        # Basic name validation
        name_valid = len(name.strip()) >= 2 and name.strip().isalpha()
        
        # TODO: Integrate with public records API (e.g., Whitepages, Spokeo)
        # TODO: Integrate with social profile APIs (e.g., LinkedIn, Facebook Graph API)
        public_records_match = None
        social_profiles_match = None
        
        # For now, mark as partial if name is valid
        name_verified = name_valid
        
        # Calculate confidence (lower without external APIs)
        confidence = 0.5 if name_valid else 0.0
        
        # Calculate risk (higher risk if name can't be verified)
        risk_score = 30.0 if not name_verified else 10.0
        
        # Determine status
        if name_verified:
            status = ContactVerificationStatus.PARTIAL  # Partial because external APIs not integrated
        else:
            status = ContactVerificationStatus.FAILED
        
        # Store in database
        contact_verification = ContactVerificationResult(
            company_id=company_id,
            verification_result_id=verification_result_id,
            contact_type=ContactType.NAME,
            contact_value=name,
            format_valid=name_valid,
            name_verified=name_verified,
            public_records_match=public_records_match,
            social_profiles_match=social_profiles_match,
            status=status,
            confidence_score=confidence,
            risk_score=risk_score,
            verification_details={
                "name_length": len(name),
                "external_apis_available": False
            },
            errors=[] if name_valid else ["Name format invalid"],
            sources_checked=["format_validation"],
            verified_at=datetime.utcnow() if status != ContactVerificationStatus.PENDING else None
        )
        
        try:
            self.db.add(contact_verification)
            self.db.commit()
            self.db.refresh(contact_verification)
            return contact_verification
        except Exception as e:
            self.db.rollback()
            raise
    
    def get_contact_verifications(
        self,
        company_id: UUID,
        verification_result_id: Optional[UUID] = None
    ) -> List[ContactVerificationResult]:
        """Get all contact verifications for a company"""
        query = self.db.query(ContactVerificationResult).filter(
            ContactVerificationResult.company_id == company_id
        )
        
        if verification_result_id:
            query = query.filter(
                ContactVerificationResult.verification_result_id == verification_result_id
            )
        
        return query.order_by(ContactVerificationResult.created_at.desc()).all()
    
    def _calculate_email_confidence(self, verification_result: Dict) -> float:
        """Calculate confidence score for email verification"""
        confidence = 0.0
        
        if verification_result.get("format_valid"):
            confidence += 0.2
        
        if verification_result.get("domain_exists"):
            confidence += 0.3
        
        if verification_result.get("mx_record_exists"):
            confidence += 0.3
        
        if verification_result.get("email_exists") is True:
            confidence += 0.2
        elif verification_result.get("email_exists") is False:
            confidence -= 0.1  # Penalty for non-existent email
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_phone_confidence(self, verification_result: Dict) -> float:
        """Calculate confidence score for phone verification"""
        confidence = 0.0
        
        if verification_result.get("format_valid"):
            confidence += 0.4
        
        if verification_result.get("carrier_valid") is True:
            confidence += 0.4
        elif verification_result.get("carrier_valid") is False:
            confidence -= 0.2  # Penalty for invalid carrier
        
        if verification_result.get("line_type"):
            confidence += 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _determine_email_status(self, verification_result: Dict) -> ContactVerificationStatus:
        """Determine verification status for email"""
        if not verification_result.get("format_valid"):
            return ContactVerificationStatus.FAILED
        
        if (verification_result.get("domain_exists") and 
            verification_result.get("mx_record_exists") and
            verification_result.get("email_exists") is True):
            return ContactVerificationStatus.VERIFIED
        
        if (verification_result.get("domain_exists") and 
            verification_result.get("mx_record_exists")):
            return ContactVerificationStatus.PARTIAL
        
        return ContactVerificationStatus.FAILED
    
    def _determine_phone_status(self, verification_result: Dict) -> ContactVerificationStatus:
        """Determine verification status for phone"""
        if not verification_result.get("format_valid"):
            return ContactVerificationStatus.FAILED
        
        if verification_result.get("carrier_valid") is True:
            return ContactVerificationStatus.VERIFIED
        
        if verification_result.get("format_valid") and verification_result.get("carrier_valid") is None:
            return ContactVerificationStatus.PARTIAL
        
        return ContactVerificationStatus.FAILED

