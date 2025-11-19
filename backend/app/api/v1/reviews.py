"""Review API endpoints"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from app.db.database import get_db
from app.models.company import Company
from app.models.review import Review, ReviewStatus
from app.models.user import User
from app.core.auth import get_current_active_user
from app.core.audit import log_audit_event
from fastapi import Request

router = APIRouter()


class ReviewCreate(BaseModel):
    """Review creation model"""
    status: ReviewStatus
    notes: Optional[str] = None


class ReviewUpdate(BaseModel):
    """Review update model"""
    status: Optional[ReviewStatus] = None
    notes: Optional[str] = None


class ReviewResponse(BaseModel):
    """Review response model"""
    id: str
    company_id: str
    reviewer_id: str
    reviewer_name: str
    reviewed_at: datetime
    notes: Optional[str]
    status: ReviewStatus
    
    class Config:
        from_attributes = True


class BulkReviewRequest(BaseModel):
    """Bulk review request model"""
    company_ids: List[str]
    status: ReviewStatus
    notes: Optional[str] = None


@router.post("/company/{company_id}/review", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    company_id: UUID,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Create or update a review for a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Check if review already exists
    existing_review = db.query(Review).filter(
        and_(
            Review.company_id == company_id,
            Review.reviewer_id == current_user.id
        )
    ).first()
    
    try:
        if existing_review:
            # Update existing review
            existing_review.status = review_data.status
            existing_review.notes = review_data.notes
            existing_review.reviewed_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_review)
            review = existing_review
        else:
            # Create new review
            review = Review(
                company_id=company_id,
                reviewer_id=current_user.id,
                status=review_data.status,
                notes=review_data.notes
            )
            db.add(review)
            db.commit()
            db.refresh(review)
        
        # Log audit event
        log_audit_event(
            db=db,
            user=current_user,
            action="CREATE_REVIEW" if not existing_review else "UPDATE_REVIEW",
            resource_type="review",
            resource_id=review.id,
            details={
                "company_id": str(company_id),
                "status": review_data.status.value,
                "has_notes": bool(review_data.notes)
            },
            request=request
        )
        
        # Get reviewer name
        reviewer = db.query(User).filter(User.id == current_user.id).first()
        reviewer_name = reviewer.username if reviewer else current_user.email
        
        return ReviewResponse(
            id=str(review.id),
            company_id=str(review.company_id),
            reviewer_id=str(review.reviewer_id),
            reviewer_name=reviewer_name,
            reviewed_at=review.reviewed_at,
            notes=review.notes,
            status=review.status
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create/update review"
        )


@router.get("/company/{company_id}/review", response_model=Optional[ReviewResponse])
async def get_review(
    company_id: UUID,
    reviewer_id: Optional[UUID] = Query(None, description="Optional specific reviewer ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get review for a company. Returns null if no review exists."""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    query = db.query(Review).filter(Review.company_id == company_id)
    
    # If reviewer_id is specified, get that specific review
    # Otherwise, get the most recent review
    if reviewer_id:
        query = query.filter(Review.reviewer_id == reviewer_id)
    
    review = query.order_by(desc(Review.reviewed_at)).first()
    
    if not review:
        # Return null JSON response with 200 status
        # FastAPI will serialize None as null in JSON
        return None
    
    # Performance optimization: Use eager loading if available, otherwise query
    if hasattr(review, 'reviewer') and review.reviewer:
        reviewer = review.reviewer
    else:
        reviewer = db.query(User).filter(User.id == review.reviewer_id).first()
    reviewer_name = reviewer.username if reviewer else reviewer.email if reviewer else "Unknown"
    
    return ReviewResponse(
        id=str(review.id),
        company_id=str(review.company_id),
        reviewer_id=str(review.reviewer_id),
        reviewer_name=reviewer_name,
        reviewed_at=review.reviewed_at,
        notes=review.notes,
        status=review.status
    )


@router.get("/company/{company_id}/reviews", response_model=List[ReviewResponse])
async def get_review_history(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get review history for a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    reviews = db.query(Review).filter(
        Review.company_id == company_id
    ).order_by(desc(Review.reviewed_at)).all()
    
    result = []
    for review in reviews:
        reviewer = db.query(User).filter(User.id == review.reviewer_id).first()
        reviewer_name = reviewer.username if reviewer else reviewer.email if reviewer else "Unknown"
        
        result.append(ReviewResponse(
            id=str(review.id),
            company_id=str(review.company_id),
            reviewer_id=str(review.reviewer_id),
            reviewer_name=reviewer_name,
            reviewed_at=review.reviewed_at,
            notes=review.notes,
            status=review.status
        ))
    
    return result


@router.delete("/company/{company_id}/review", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Delete (unmark) a review for a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    review = db.query(Review).filter(
        and_(
            Review.company_id == company_id,
            Review.reviewer_id == current_user.id
        )
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No review found for this company"
        )
    
    try:
        # Log audit event before deletion
        log_audit_event(
            db=db,
            user=current_user,
            action="DELETE_REVIEW",
            resource_type="review",
            resource_id=review.id,
            details={"company_id": str(company_id)},
            request=request
        )
        
        db.delete(review)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete review"
        )
    
    return None


@router.post("/reviews/bulk", status_code=status.HTTP_200_OK)
async def bulk_review(
    bulk_data: BulkReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Bulk mark companies as reviewed"""
    if not bulk_data.company_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No company IDs provided"
        )
    
    # Validate all companies exist
    companies = db.query(Company).filter(
        Company.id.in_([UUID(cid) for cid in bulk_data.company_ids])
    ).all()
    
    if len(companies) != len(bulk_data.company_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more company IDs not found"
        )
    
    created_count = 0
    updated_count = 0
    
    try:
        for company_id_str in bulk_data.company_ids:
            company_id = UUID(company_id_str)
            
            # Check if review exists
            existing_review = db.query(Review).filter(
                and_(
                    Review.company_id == company_id,
                    Review.reviewer_id == current_user.id
                )
            ).first()
            
            if existing_review:
                existing_review.status = bulk_data.status
                existing_review.notes = bulk_data.notes
                existing_review.reviewed_at = datetime.utcnow()
                updated_count += 1
            else:
                review = Review(
                    company_id=company_id,
                    reviewer_id=current_user.id,
                    status=bulk_data.status,
                    notes=bulk_data.notes
                )
                db.add(review)
                created_count += 1
        
        db.commit()
        
        # Log audit event
        log_audit_event(
            db=db,
            user=current_user,
            action="BULK_REVIEW",
            resource_type="review",
            resource_id=None,
            details={
                "company_count": len(bulk_data.company_ids),
                "status": bulk_data.status.value,
                "created": created_count,
                "updated": updated_count
            },
            request=request
        )
        
        return {
            "message": "Bulk review completed",
            "total": len(bulk_data.company_ids),
            "created": created_count,
            "updated": updated_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform bulk review"
        )

