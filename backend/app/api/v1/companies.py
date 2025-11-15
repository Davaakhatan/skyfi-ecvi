"""Company API endpoints"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from pydantic import BaseModel
from uuid import UUID

from app.db.database import get_db
from app.models.company import Company
from app.models.verification_result import VerificationResult, RiskCategory, VerificationStatus
from app.models.review import Review, ReviewStatus
from app.models.user import User
from app.core.auth import get_current_active_user
from app.core.audit import log_audit_event
from fastapi import Request

router = APIRouter()


class CompanyCreate(BaseModel):
    """Company creation model"""
    legal_name: str
    registration_number: Optional[str] = None
    jurisdiction: Optional[str] = None
    domain: Optional[str] = None


class CompanyResponse(BaseModel):
    """Company response model"""
    id: str
    legal_name: str
    registration_number: Optional[str]
    jurisdiction: Optional[str]
    domain: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    """Company list response with pagination"""
    items: List[CompanyResponse]
    total: int
    skip: int
    limit: int


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Create a new company"""
    # Check if company already exists
    existing_company = db.query(Company).filter(
        Company.legal_name == company_data.legal_name
    ).first()
    
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this name already exists"
        )
    
    # Create new company
    new_company = Company(
        legal_name=company_data.legal_name,
        registration_number=company_data.registration_number,
        jurisdiction=company_data.jurisdiction,
        domain=company_data.domain
    )
    
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    
    # Log audit event
    log_audit_event(
        db=db,
        user=current_user,
        action="CREATE_COMPANY",
        resource_type="company",
        resource_id=new_company.id,
        details={"legal_name": new_company.legal_name},
        request=request
    )
    
    return new_company


@router.get("/", response_model=CompanyListResponse)
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    risk_score_min: Optional[int] = Query(None, ge=0, le=100),
    risk_score_max: Optional[int] = Query(None, ge=0, le=100),
    risk_category: Optional[RiskCategory] = Query(None),
    verification_status: Optional[VerificationStatus] = Query(None),
    reviewed: Optional[bool] = Query(None),
    reviewer_id: Optional[UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    sort_by: str = Query("created_at", regex="^(created_at|legal_name|risk_score)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of companies with filtering and pagination"""
    query = db.query(Company)
    
    # Search filter
    if search:
        query = query.filter(
            or_(
                Company.legal_name.ilike(f"%{search}%"),
                Company.domain.ilike(f"%{search}%"),
                Company.registration_number.ilike(f"%{search}%")
            )
        )
    
    # Date range filter
    if start_date:
        query = query.filter(Company.created_at >= start_date)
    if end_date:
        query = query.filter(Company.created_at <= end_date)
    
    # Join with verification results for risk filtering
    if risk_score_min is not None or risk_score_max is not None or risk_category or verification_status:
        query = query.join(VerificationResult)
        
        if risk_score_min is not None:
            query = query.filter(VerificationResult.risk_score >= risk_score_min)
        if risk_score_max is not None:
            query = query.filter(VerificationResult.risk_score <= risk_score_max)
        if risk_category:
            query = query.filter(VerificationResult.risk_category == risk_category)
        if verification_status:
            query = query.filter(VerificationResult.verification_status == verification_status)
    
    # Review status filter
    if reviewed is not None or reviewer_id:
        query = query.join(Review)
        if reviewed is not None:
            status_filter = ReviewStatus.REVIEWED if reviewed else ReviewStatus.PENDING
            query = query.filter(Review.status == status_filter)
        if reviewer_id:
            query = query.filter(Review.reviewer_id == reviewer_id)
    
    # Get total count before pagination
    total = query.count()
    
    # Sorting
    if sort_by == "legal_name":
        order_by = Company.legal_name.desc() if sort_order == "desc" else Company.legal_name.asc()
    elif sort_by == "risk_score":
        # Need to join with VerificationResult for risk_score sorting
        # Check if already joined (from risk filtering above)
        has_verification_join = any(
            entity.class_ == VerificationResult for entity in query._join_entities
        ) if hasattr(query, '_join_entities') else False
        if not has_verification_join:
            query = query.outerjoin(VerificationResult)
        order_by = VerificationResult.risk_score.desc() if sort_order == "desc" else VerificationResult.risk_score.asc()
    else:  # created_at
        order_by = Company.created_at.desc() if sort_order == "desc" else Company.created_at.asc()
    
    query = query.order_by(order_by)
    
    # Pagination
    companies = query.offset(skip).limit(limit).all()
    
    return {
        "items": companies,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific company by ID"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: UUID,
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Update a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Update fields
    company.legal_name = company_data.legal_name
    company.registration_number = company_data.registration_number
    company.jurisdiction = company_data.jurisdiction
    company.domain = company_data.domain
    
    db.commit()
    db.refresh(company)
    
    # Log audit event
    log_audit_event(
        db=db,
        user=current_user,
        action="UPDATE_COMPANY",
        resource_type="company",
        resource_id=company.id,
        details={"legal_name": company.legal_name},
        request=request
    )
    
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Delete a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Log audit event before deletion
    log_audit_event(
        db=db,
        user=current_user,
        action="DELETE_COMPANY",
        resource_type="company",
        resource_id=company.id,
        details={"legal_name": company.legal_name},
        request=request
    )
    
    db.delete(company)
    db.commit()
    
    return None

