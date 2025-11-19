"""Report sharing service for generating shareable links"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
import secrets
import hashlib

from app.db.database import Base
from app.models.company import Company
from app.models.verification_result import VerificationResult


class SharedReport(Base):
    """Model for shared report links"""
    
    __tablename__ = "shared_reports"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    verification_result_id = Column(PGUUID(as_uuid=True), ForeignKey("verification_results.id"), nullable=True, index=True)
    share_token = Column(String(64), unique=True, nullable=False, index=True)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    access_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="shared_reports")
    verification_result = relationship("VerificationResult")


class ReportSharingService:
    """Service for managing shareable report links"""
    
    @staticmethod
    def generate_share_token() -> str:
        """Generate a secure share token"""
        # Generate a cryptographically secure random token
        token = secrets.token_urlsafe(32)
        return token
    
    @staticmethod
    def create_shareable_link(
        db: Session,
        company_id: UUID,
        verification_result_id: Optional[UUID] = None,
        created_by: Optional[UUID] = None,
        expires_in_days: Optional[int] = 30
    ) -> Dict:
        """
        Create a shareable link for a report
        
        Args:
            db: Database session
            company_id: Company ID
            verification_result_id: Optional specific verification result ID
            created_by: User ID who created the link
            expires_in_days: Number of days until link expires (None = never expires)
        
        Returns:
            Dictionary with share token and link information
        """
        # Check if company exists
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError(f"Company {company_id} not found")
        
        # Check if verification result exists (if specified)
        if verification_result_id:
            verification_result = db.query(VerificationResult).filter(
                VerificationResult.id == verification_result_id,
                VerificationResult.company_id == company_id
            ).first()
            if not verification_result:
                raise ValueError(f"Verification result {verification_result_id} not found")
        
        # Generate share token
        share_token = ReportSharingService.generate_share_token()
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create shared report record
        try:
            shared_report = SharedReport(
                company_id=company_id,
                verification_result_id=verification_result_id,
                share_token=share_token,
                created_by=created_by,
                expires_at=expires_at,
                is_active=True,
                access_count=0
            )
            
            db.add(shared_report)
            db.commit()
            db.refresh(shared_report)
        except Exception as e:
            logger.error(f"Failed to create shareable link: {e}")
            db.rollback()
            raise
        
        return {
            "share_token": share_token,
            "share_url": f"/api/v1/reports/shared/{share_token}",
            "expires_at": expires_at.isoformat() if expires_at else None,
            "created_at": shared_report.created_at.isoformat() if shared_report.created_at else None
        }
    
    @staticmethod
    def get_shared_report(
        db: Session,
        share_token: str
    ) -> Optional[SharedReport]:
        """
        Get shared report by token
        
        Args:
            db: Database session
            share_token: Share token
        
        Returns:
            SharedReport object or None if not found/invalid
        """
        shared_report = db.query(SharedReport).filter(
            SharedReport.share_token == share_token,
            SharedReport.is_active == True
        ).first()
        
        if not shared_report:
            return None
        
        # Check if expired
        if shared_report.expires_at:
            # Handle timezone-aware and timezone-naive datetimes
            expires_at = shared_report.expires_at
            now = datetime.utcnow()
            # Make both timezone-aware or both naive for comparison
            if expires_at.tzinfo is not None and now.tzinfo is None:
                from datetime import timezone
                now = now.replace(tzinfo=timezone.utc)
            elif expires_at.tzinfo is None and now.tzinfo is not None:
                expires_at = expires_at.replace(tzinfo=now.tzinfo)
            if expires_at < now:
                return None
        
        # Update access statistics
        try:
            shared_report.access_count += 1
            shared_report.last_accessed_at = datetime.utcnow()
            db.commit()
        except Exception as e:
            logger.error(f"Failed to update shared report access statistics: {e}")
            db.rollback()
            # Still return the report even if statistics update fails
        
        return shared_report
    
    @staticmethod
    def revoke_shareable_link(
        db: Session,
        share_token: str,
        user_id: Optional[UUID] = None
    ) -> bool:
        """
        Revoke a shareable link
        
        Args:
            db: Database session
            share_token: Share token to revoke
            user_id: Optional user ID (for authorization check)
        
        Returns:
            True if revoked, False if not found
        """
        shared_report = db.query(SharedReport).filter(
            SharedReport.share_token == share_token
        ).first()
        
        if not shared_report:
            return False
        
        # Optional: Check if user has permission to revoke
        # (e.g., created_by == user_id or user is admin)
        
        try:
            shared_report.is_active = False
            db.commit()
        except Exception as e:
            logger.error(f"Failed to revoke shareable link: {e}")
            db.rollback()
            return False
        
        return True
    
    @staticmethod
    def list_shared_links(
        db: Session,
        company_id: UUID,
        user_id: Optional[UUID] = None
    ) -> List[Dict]:
        """
        List all shared links for a company
        
        Args:
            db: Database session
            company_id: Company ID
            user_id: Optional user ID (for filtering)
        
        Returns:
            List of shared link information
        """
        query = db.query(SharedReport).filter(
            SharedReport.company_id == company_id
        )
        
        if user_id:
            query = query.filter(SharedReport.created_by == user_id)
        
        shared_reports = query.order_by(SharedReport.created_at.desc()).all()
        
        result = []
        for shared_report in shared_reports:
            result.append({
                "share_token": shared_report.share_token,
                "share_url": f"/api/v1/reports/shared/{shared_report.share_token}",
                "verification_result_id": str(shared_report.verification_result_id) if shared_report.verification_result_id else None,
                "created_at": shared_report.created_at.isoformat() if shared_report.created_at else None,
                "expires_at": shared_report.expires_at.isoformat() if shared_report.expires_at else None,
                "is_active": shared_report.is_active,
                "access_count": shared_report.access_count,
                "last_accessed_at": shared_report.last_accessed_at.isoformat() if shared_report.last_accessed_at else None
            })
        
        return result

