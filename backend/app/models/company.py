"""Company model"""

from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Company(Base):
    """Company model"""
    
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    legal_name = Column(String(255), nullable=False, index=True)
    registration_number = Column(String(100), nullable=True)
    jurisdiction = Column(String(100), nullable=True)
    domain = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    verification_results = relationship("VerificationResult", back_populates="company", cascade="all, delete-orphan")
    company_data = relationship("CompanyData", back_populates="company", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="company", cascade="all, delete-orphan")
    shared_reports = relationship("SharedReport", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company(id={self.id}, legal_name={self.legal_name})>"

