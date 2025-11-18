"""Verification result model"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.database import Base


class RiskCategory(str, enum.Enum):
    """Risk category enumeration"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class VerificationStatus(str, enum.Enum):
    """Verification status enumeration"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class VerificationResult(Base):
    """Verification result model"""
    
    __tablename__ = "verification_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    risk_score = Column(Integer, nullable=False, index=True)  # 0-100
    risk_category = Column(Enum(RiskCategory), nullable=False, index=True)
    verification_status = Column(Enum(VerificationStatus), nullable=False, default=VerificationStatus.PENDING, index=True)
    analysis_started_at = Column(DateTime(timezone=True), nullable=True)
    analysis_completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="verification_results")
    contact_verifications = relationship("ContactVerificationResult", back_populates="verification_result", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<VerificationResult(id={self.id}, company_id={self.company_id}, risk_score={self.risk_score})>"

