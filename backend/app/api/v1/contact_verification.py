"""Contact verification API endpoints"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.db.database import get_db
from app.models.company import Company
from app.models.contact_verification import ContactVerificationResult, ContactType, ContactVerificationStatus
from app.models.user import User
from app.core.auth import get_current_active_user
from app.services.contact_verification_enhanced import EnhancedContactVerificationService

router = APIRouter()


class ContactVerificationRequest(BaseModel):
    """Schema for contact verification request"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    country_code: Optional[str] = None


class ContactVerificationResponse(BaseModel):
    """Schema for contact verification response"""
    id: UUID
    company_id: UUID
    verification_result_id: Optional[UUID]
    contact_type: ContactType
    contact_value: str
    country_code: Optional[str]
    format_valid: bool
    domain_exists: Optional[bool]
    mx_record_exists: Optional[bool]
    email_exists: Optional[bool]
    carrier_valid: Optional[bool]
    carrier_name: Optional[str]
    line_type: Optional[str]
    name_verified: Optional[bool]
    public_records_match: Optional[bool]
    social_profiles_match: Optional[bool]
    status: ContactVerificationStatus
    confidence_score: Optional[float]
    risk_score: Optional[float]
    verification_details: Optional[dict]
    errors: Optional[List[str]]
    sources_checked: Optional[List[str]]
    verified_at: Optional[str] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to response model with proper datetime serialization"""
        from datetime import datetime
        data = {
            "id": obj.id,
            "company_id": obj.company_id,
            "verification_result_id": obj.verification_result_id,
            "contact_type": obj.contact_type,
            "contact_value": obj.contact_value,
            "country_code": obj.country_code,
            "format_valid": obj.format_valid,
            "domain_exists": obj.domain_exists,
            "mx_record_exists": obj.mx_record_exists,
            "email_exists": obj.email_exists,
            "carrier_valid": obj.carrier_valid,
            "carrier_name": obj.carrier_name,
            "line_type": obj.line_type,
            "name_verified": obj.name_verified,
            "public_records_match": obj.public_records_match,
            "social_profiles_match": obj.social_profiles_match,
            "status": obj.status,
            "confidence_score": float(obj.confidence_score) if obj.confidence_score is not None else None,
            "risk_score": float(obj.risk_score) if obj.risk_score is not None else None,
            "verification_details": obj.verification_details,
            "errors": obj.errors,
            "sources_checked": obj.sources_checked,
            "verified_at": obj.verified_at.isoformat() if obj.verified_at else None,
            "created_at": obj.created_at.isoformat() if isinstance(obj.created_at, datetime) else str(obj.created_at),
            "updated_at": obj.updated_at.isoformat() if isinstance(obj.updated_at, datetime) else str(obj.updated_at),
        }
        return cls(**data)


@router.post("/company/{company_id}/contact/verify", response_model=List[ContactVerificationResponse], status_code=status.HTTP_201_CREATED)
async def verify_contact_info(
    company_id: UUID,
    contact_data: ContactVerificationRequest,
    verification_result_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Verify contact information for a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    
    if not contact_data.email and not contact_data.phone and not contact_data.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one contact method (email, phone, or name) must be provided"
        )
    
    service = EnhancedContactVerificationService(db)
    results = []
    
    # Verify email if provided
    if contact_data.email:
        try:
            email_result = service.verify_and_store_email(
                company_id=company_id,
                verification_result_id=verification_result_id,
                email=contact_data.email
            )
            results.append(ContactVerificationResponse.from_orm(email_result))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to verify email: {str(e)}"
            )
    
    # Verify phone if provided
    if contact_data.phone:
        try:
            phone_result = service.verify_and_store_phone(
                company_id=company_id,
                verification_result_id=verification_result_id,
                phone=contact_data.phone,
                country_code=contact_data.country_code
            )
            results.append(ContactVerificationResponse.from_orm(phone_result))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to verify phone: {str(e)}"
            )
    
    # Verify name if provided
    if contact_data.name:
        try:
            name_result = service.verify_and_store_name(
                company_id=company_id,
                verification_result_id=verification_result_id,
                name=contact_data.name
            )
            results.append(ContactVerificationResponse.from_orm(name_result))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to verify name: {str(e)}"
            )
    
    return results


@router.get("/company/{company_id}/contact/verifications", response_model=List[ContactVerificationResponse])
async def get_contact_verifications(
    company_id: UUID,
    verification_result_id: Optional[UUID] = Query(None),
    contact_type: Optional[ContactType] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get contact verification results for a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    
    service = EnhancedContactVerificationService(db)
    verifications = service.get_contact_verifications(
        company_id=company_id,
        verification_result_id=verification_result_id
    )
    
    # Filter by contact type if provided
    if contact_type:
        verifications = [v for v in verifications if v.contact_type == contact_type]
    
    # Convert to response models
    return [ContactVerificationResponse.from_orm(v) for v in verifications]


@router.get("/contact/verification/{verification_id}", response_model=ContactVerificationResponse)
async def get_contact_verification(
    verification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific contact verification result"""
    verification = db.query(ContactVerificationResult).filter(
        ContactVerificationResult.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification not found")
    
    return ContactVerificationResponse.from_orm(verification)

