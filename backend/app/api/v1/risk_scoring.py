"""Risk scoring API endpoints"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID

from app.db.database import get_db
from app.models.company import Company
from app.models.verification_result import VerificationResult, RiskCategory
from app.core.auth import get_current_active_user
from app.models.user import User
from app.services.risk_calculator import RiskCalculator
from app.services.risk_history import RiskHistoryService

router = APIRouter()


class RiskScoreResponse(BaseModel):
    """Risk score response model"""
    risk_score: int
    risk_category: RiskCategory
    breakdown: dict


class RiskCalculationRequest(BaseModel):
    """Risk calculation request model"""
    dns_verified: bool
    domain_age_days: Optional[int] = None
    registration_matches: int = 0
    total_sources: int = 0
    email_valid: bool = False
    phone_valid: bool = False
    email_exists: Optional[bool] = None
    phone_carrier_valid: Optional[bool] = None
    domain_matches_company: bool = False
    ssl_valid: Optional[bool] = None
    suspicious_keywords: int = 0
    data_consistency_score: float = 0.0
    source_reliability_avg: float = 0.0


@router.post("/calculate", response_model=RiskScoreResponse)
async def calculate_risk_score(
    request: RiskCalculationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Calculate risk score based on verification data"""
    result = RiskCalculator.calculate_overall_risk(
        dns_verified=request.dns_verified,
        domain_age_days=request.domain_age_days,
        registration_matches=request.registration_matches,
        total_sources=request.total_sources,
        email_valid=request.email_valid,
        phone_valid=request.phone_valid,
        email_exists=request.email_exists,
        phone_carrier_valid=request.phone_carrier_valid,
        domain_matches_company=request.domain_matches_company,
        ssl_valid=request.ssl_valid,
        suspicious_keywords=request.suspicious_keywords,
        data_consistency_score=request.data_consistency_score,
        source_reliability_avg=request.source_reliability_avg
    )
    
    return result


@router.get("/company/{company_id}", response_model=RiskScoreResponse)
async def get_company_risk_score(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get risk score for a specific company"""
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
    
    return {
        "risk_score": verification_result.risk_score,
        "risk_category": verification_result.risk_category,
        "breakdown": {}  # TODO: Store breakdown in database or recalculate
    }


@router.get("/company/{company_id}/history")
async def get_company_risk_history(
    company_id: UUID,
    limit: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get historical risk scores for a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    history = RiskHistoryService.get_risk_history(db, company_id, limit)
    
    return {
        "company_id": str(company_id),
        "history": history,
        "total_records": len(history)
    }


@router.get("/company/{company_id}/trend")
async def get_company_risk_trend(
    company_id: UUID,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get risk score trend for a company over time"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    if days < 1 or days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days must be between 1 and 365"
        )
    
    trend = RiskHistoryService.get_risk_trend(db, company_id, days)
    
    return trend


@router.get("/company/{company_id}/latest")
async def get_company_latest_risk_score(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the latest risk score for a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    latest = RiskHistoryService.get_latest_risk_score(db, company_id)
    
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verification results found for this company"
        )
    
    return latest

