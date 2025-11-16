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
from app.services.verification_service import VerificationService
from app.services.task_queue import TaskQueueService
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


class VerificationResponse(BaseModel):
    """Verification result response model"""
    id: str
    company_id: str
    risk_score: int
    risk_category: RiskCategory
    verification_status: VerificationStatus
    analysis_started_at: Optional[datetime]
    analysis_completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


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


@router.post("/{company_id}/verify", response_model=VerificationResponse, status_code=status.HTTP_202_ACCEPTED)
async def verify_company(
    company_id: UUID,
    timeout_hours: float = Query(2.0, ge=0.1, le=24.0),
    async_mode: bool = Query(False, description="Run verification asynchronously using Celery"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Initiate company verification (sync or async)"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Log audit event
    log_audit_event(
        db=db,
        user=current_user,
        action="VERIFY_COMPANY",
        resource_type="company",
        resource_id=company.id,
        details={"legal_name": company.legal_name, "timeout_hours": timeout_hours, "async_mode": async_mode},
        request=request
    )
    
    if async_mode:
        # Start async verification via Celery
        task_info = TaskQueueService.start_verification(company_id, timeout_hours)
        
        # Create initial verification result record
        verification_result = VerificationResult(
            company_id=company_id,
            risk_score=0,
            risk_category=RiskCategory.LOW,
            verification_status=VerificationStatus.IN_PROGRESS,
            analysis_started_at=datetime.utcnow()
        )
        db.add(verification_result)
        db.commit()
        db.refresh(verification_result)
        
        # Store task_id in details (we could add a task_id field to VerificationResult in future)
        # For now, return the verification result with status IN_PROGRESS
        
        return verification_result
    else:
        # Synchronous verification
        verification_service = VerificationService(db)
        verification_result = await verification_service.verify_company(company_id, timeout_hours)
        
        return verification_result


@router.get("/{company_id}/verification", response_model=VerificationResponse)
async def get_verification_result(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get latest verification result for a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    verification_service = VerificationService(db)
    verification_result = verification_service.get_verification_result(company_id)
    
    if not verification_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verification result found for this company"
        )
    
    return verification_result


@router.get("/{company_id}/verification/status")
async def get_verification_status(
    company_id: UUID,
    task_id: Optional[str] = Query(None, description="Optional Celery task ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get verification status for a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Get latest verification result
    verification_result = db.query(VerificationResult).filter(
        VerificationResult.company_id == company_id
    ).order_by(VerificationResult.created_at.desc()).first()
    
    if not verification_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verification result found for this company"
        )
    
    response = {
        "company_id": str(company_id),
        "verification_status": verification_result.verification_status.value,
        "risk_score": verification_result.risk_score,
        "risk_category": verification_result.risk_category.value if verification_result.risk_category else None,
        "started_at": verification_result.analysis_started_at.isoformat() if verification_result.analysis_started_at else None,
        "completed_at": verification_result.analysis_completed_at.isoformat() if verification_result.analysis_completed_at else None,
    }
    
    # If task_id provided, get Celery task status
    if task_id:
        task_status = TaskQueueService.get_task_status(task_id)
        response["task_status"] = task_status
    
    return response


@router.post("/{company_id}/verification/cancel")
async def cancel_verification(
    company_id: UUID,
    task_id: Optional[str] = Query(None, description="Optional Celery task ID to cancel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Cancel an in-progress verification"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Log audit event
    log_audit_event(
        db=db,
        user=current_user,
        action="CANCEL_VERIFICATION",
        resource_type="company",
        resource_id=company.id,
        details={"legal_name": company.legal_name, "task_id": task_id},
        request=request
    )
    
    # Cancel Celery task if task_id provided
    if task_id:
        cancel_result = TaskQueueService.cancel_task(task_id)
    
    # Mark verification as failed
    verification_result = db.query(VerificationResult).filter(
        VerificationResult.company_id == company_id,
        VerificationResult.verification_status == VerificationStatus.IN_PROGRESS
    ).first()
    
    if verification_result:
        verification_result.verification_status = VerificationStatus.FAILED
        verification_result.analysis_completed_at = datetime.utcnow()
        db.commit()
    
    return {
        "success": True,
        "company_id": str(company_id),
        "message": "Verification cancelled"
    }


@router.get("/queue/stats")
async def get_queue_stats(
    current_user: User = Depends(get_current_active_user)
):
    """Get task queue statistics (admin only)"""
    # TODO: Add admin role check
    stats = TaskQueueService.get_queue_stats()
    worker_stats = TaskQueueService.get_worker_stats()
    
    return {
        "queue": stats,
        "workers": worker_stats
    }

