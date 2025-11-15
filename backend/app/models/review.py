"""Review model"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.database import Base


class ReviewStatus(str, enum.Enum):
    """Review status enumeration"""
    PENDING = "PENDING"
    REVIEWED = "REVIEWED"
    FLAGGED = "FLAGGED"


class Review(Base):
    """Review model"""
    
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    status = Column(Enum(ReviewStatus), nullable=False, default=ReviewStatus.PENDING, index=True)
    
    # Relationships
    company = relationship("Company", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(id={self.id}, company_id={self.company_id}, reviewer_id={self.reviewer_id}, status={self.status})>"

