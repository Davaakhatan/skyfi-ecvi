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
    verified_at: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


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
            results.append(email_result)
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
            results.append(phone_result)
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
            results.append(name_result)
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
    
    return verifications


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
    
    return verification

