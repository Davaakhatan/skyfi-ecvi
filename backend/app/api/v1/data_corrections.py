"""Data correction API endpoints"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.models.company import Company
from app.models.data_correction import DataCorrection, CorrectionStatus
from app.models.user import User
from app.core.auth import get_current_active_user, require_roles
from app.core.audit import log_audit_event
from app.services.data_correction import DataCorrectionService
from app.services.task_queue import TaskQueueService
from fastapi import Request

router = APIRouter()


class CorrectionCreate(BaseModel):
    """Schema for creating a correction"""
    field_name: str
    field_type: str  # e.g., "legal_name", "registration_number", "address", etc.
    new_value: str
    correction_reason: Optional[str] = None
    company_data_id: Optional[UUID] = None
    metadata: Optional[dict] = None


class CorrectionUpdate(BaseModel):
    """Schema for updating correction status"""
    status: CorrectionStatus
    rejection_reason: Optional[str] = None


class CorrectionResponse(BaseModel):
    """Schema for returning a correction"""
    id: UUID
    company_id: UUID
    company_data_id: Optional[UUID]
    field_name: str
    field_type: str
    old_value: Optional[str]
    new_value: str
    correction_reason: Optional[str]
    status: CorrectionStatus
    version: str
    corrected_by: UUID
    corrector_name: str
    approved_by: Optional[UUID]
    approver_name: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/company/{company_id}/corrections", response_model=CorrectionResponse, status_code=status.HTTP_201_CREATED)
@require_roles(["admin", "compliance", "operator"])
async def create_correction(
    company_id: UUID,
    correction_data: CorrectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Create a new data correction"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    
    # Get current value for the field
    old_value = None
    if correction_data.field_type == "legal_name":
        old_value = company.legal_name
    elif correction_data.field_type == "registration_number":
        old_value = company.registration_number
    elif correction_data.field_type == "jurisdiction":
        old_value = company.jurisdiction
    elif correction_data.field_type == "domain":
        old_value = company.domain
    
    # Validate that the value is actually different
    if old_value == correction_data.new_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New value must be different from current value"
        )
    
    # Create correction
    correction_service = DataCorrectionService(db)
    try:
        correction = correction_service.create_correction(
            company_id=company_id,
            field_name=correction_data.field_name,
            field_type=correction_data.field_type,
            old_value=old_value,
            new_value=correction_data.new_value,
            correction_reason=correction_data.correction_reason,
            corrected_by=current_user.id,
            company_data_id=correction_data.company_data_id,
            metadata=correction_data.metadata
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create correction: {str(e)}"
        )
    
    # Log audit event
    log_audit_event(
        db=db,
        user=current_user,
        action="CREATE_CORRECTION",
        resource_type="data_correction",
        resource_id=correction.id,
        details={
            "company_id": str(company_id),
            "field_name": correction_data.field_name,
            "field_type": correction_data.field_type,
            "old_value": old_value,
            "new_value": correction_data.new_value
        },
        request=request
    )
    
    # Build response
    corrector_name = current_user.username if current_user.username else current_user.email
    
    return CorrectionResponse(
        id=correction.id,
        company_id=correction.company_id,
        company_data_id=correction.company_data_id,
        field_name=correction.field_name,
        field_type=correction.field_type,
        old_value=correction.old_value,
        new_value=correction.new_value,
        correction_reason=correction.correction_reason,
        status=correction.status,
        version=correction.version,
        corrected_by=correction.corrected_by,
        corrector_name=corrector_name,
        approved_by=correction.approved_by,
        approver_name=None,
        approved_at=correction.approved_at,
        created_at=correction.created_at,
        updated_at=correction.updated_at
    )


@router.post("/corrections/{correction_id}/approve", response_model=CorrectionResponse)
@require_roles(["admin", "compliance"])
async def approve_correction(
    correction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Approve and apply a correction"""
    correction = db.query(DataCorrection).filter(DataCorrection.id == correction_id).first()
    if not correction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Correction not found")
    
    correction_service = DataCorrectionService(db)
    try:
        correction = correction_service.approve_correction(
            correction_id=correction_id,
            approved_by=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve correction: {str(e)}"
        )
    
    # Log audit event
    log_audit_event(
        db=db,
        user=current_user,
        action="APPROVE_CORRECTION",
        resource_type="data_correction",
        resource_id=correction.id,
        details={
            "company_id": str(correction.company_id),
            "field_name": correction.field_name,
            "old_value": correction.old_value,
            "new_value": correction.new_value
        },
        request=request
    )
    
    # Get approver name
    approver = db.query(User).filter(User.id == correction.approved_by).first()
    approver_name = approver.username if approver and approver.username else approver.email if approver else None
    
    # Get corrector name
    corrector = db.query(User).filter(User.id == correction.corrected_by).first()
    corrector_name = corrector.username if corrector and corrector.username else corrector.email if corrector else "Unknown"
    
    return CorrectionResponse(
        id=correction.id,
        company_id=correction.company_id,
        company_data_id=correction.company_data_id,
        field_name=correction.field_name,
        field_type=correction.field_type,
        old_value=correction.old_value,
        new_value=correction.new_value,
        correction_reason=correction.correction_reason,
        status=correction.status,
        version=correction.version,
        corrected_by=correction.corrected_by,
        corrector_name=corrector_name,
        approved_by=correction.approved_by,
        approver_name=approver_name,
        approved_at=correction.approved_at,
        created_at=correction.created_at,
        updated_at=correction.updated_at
    )


@router.post("/corrections/{correction_id}/reject", response_model=CorrectionResponse)
@require_roles(["admin", "compliance"])
async def reject_correction(
    correction_id: UUID,
    rejection_reason: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Reject a correction"""
    correction = db.query(DataCorrection).filter(DataCorrection.id == correction_id).first()
    if not correction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Correction not found")
    
    correction_service = DataCorrectionService(db)
    try:
        correction = correction_service.reject_correction(
            correction_id=correction_id,
            rejected_by=current_user.id,
            rejection_reason=rejection_reason
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject correction: {str(e)}"
        )
    
    # Log audit event
    log_audit_event(
        db=db,
        user=current_user,
        action="REJECT_CORRECTION",
        resource_type="data_correction",
        resource_id=correction.id,
        details={
            "company_id": str(correction.company_id),
            "field_name": correction.field_name,
            "rejection_reason": rejection_reason
        },
        request=request
    )
    
    # Get approver name
    approver = db.query(User).filter(User.id == correction.approved_by).first()
    approver_name = approver.username if approver and approver.username else approver.email if approver else None
    
    # Get corrector name
    corrector = db.query(User).filter(User.id == correction.corrected_by).first()
    corrector_name = corrector.username if corrector and corrector.username else corrector.email if corrector else "Unknown"
    
    return CorrectionResponse(
        id=correction.id,
        company_id=correction.company_id,
        company_data_id=correction.company_data_id,
        field_name=correction.field_name,
        field_type=correction.field_type,
        old_value=correction.old_value,
        new_value=correction.new_value,
        correction_reason=correction.correction_reason,
        status=correction.status,
        version=correction.version,
        corrected_by=correction.corrected_by,
        corrector_name=corrector_name,
        approved_by=correction.approved_by,
        approver_name=approver_name,
        approved_at=correction.approved_at,
        created_at=correction.created_at,
        updated_at=correction.updated_at
    )


@router.get("/company/{company_id}/corrections", response_model=List[CorrectionResponse])
async def get_correction_history(
    company_id: UUID,
    field_name: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get correction history for a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    
    correction_service = DataCorrectionService(db)
    corrections = correction_service.get_correction_history(
        company_id=company_id,
        field_name=field_name,
        limit=limit
    )
    
    # Performance optimization: Batch load users to avoid N+1 queries
    user_ids = [str(correction.corrected_by) for correction in corrections]
    user_ids.extend([str(correction.approved_by) for correction in corrections if correction.approved_by])
    
    users = {}
    if user_ids:
        from uuid import UUID
        uuids = [UUID(uid) for uid in set(user_ids) if uid]
        if uuids:
            user_objects = db.query(User).filter(User.id.in_(uuids)).all()
            users = {str(user.id): user for user in user_objects}
    
    # Build response with user names
    response = []
    for correction in corrections:
        corrector = users.get(str(correction.corrected_by))
        corrector_name = corrector.username if corrector and corrector.username else corrector.email if corrector else "Unknown"
        
        approver_name = None
        if correction.approved_by:
            approver = users.get(str(correction.approved_by))
            approver_name = approver.username if approver and approver.username else approver.email if approver else None
        
        response.append(CorrectionResponse(
            id=correction.id,
            company_id=correction.company_id,
            company_data_id=correction.company_data_id,
            field_name=correction.field_name,
            field_type=correction.field_type,
            old_value=correction.old_value,
            new_value=correction.new_value,
            correction_reason=correction.correction_reason,
            status=correction.status,
            version=correction.version,
            corrected_by=correction.corrected_by,
            corrector_name=corrector_name,
            approved_by=correction.approved_by,
            approver_name=approver_name,
            approved_at=correction.approved_at,
            created_at=correction.created_at,
            updated_at=correction.updated_at
        ))
    
    return response


@router.post("/company/{company_id}/corrections/{correction_id}/re-run", status_code=status.HTTP_202_ACCEPTED)
@require_roles(["admin", "compliance", "operator"])
async def re_run_analysis_with_corrections(
    company_id: UUID,
    correction_id: UUID,
    timeout_hours: float = Query(2.0, ge=0.1, le=24.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Re-run verification analysis after applying corrections"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    
    correction = db.query(DataCorrection).filter(DataCorrection.id == correction_id).first()
    if not correction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Correction not found")
    
    if correction.status != CorrectionStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Correction must be approved before re-running analysis"
        )
    
    # Log audit event
    log_audit_event(
        db=db,
        user=current_user,
        action="RE_RUN_ANALYSIS_WITH_CORRECTIONS",
        resource_type="company",
        resource_id=company_id,
        details={
            "correction_id": str(correction_id),
            "field_name": correction.field_name,
            "timeout_hours": timeout_hours
        },
        request=request
    )
    
    # Start async verification via Celery
    task_info = TaskQueueService.start_verification(company_id, timeout_hours)
    
    return {
        "message": "Analysis re-run initiated with corrected data",
        "task_id": task_info.get("task_id"),
        "company_id": str(company_id),
        "correction_id": str(correction_id)
    }

