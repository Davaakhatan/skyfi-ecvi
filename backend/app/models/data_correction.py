"""Data correction model for tracking corrections and version history"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.database import Base


class CorrectionStatus(str, enum.Enum):
    """Correction status enumeration"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class DataCorrection(Base):
    """Data correction model for tracking corrections and version history"""
    
    __tablename__ = "data_corrections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    company_data_id = Column(UUID(as_uuid=True), ForeignKey("company_data.id"), nullable=True, index=True)
    
    # Field being corrected
    field_name = Column(String(100), nullable=False)
    field_type = Column(String(50), nullable=False)  # e.g., "legal_name", "registration_number", "address", etc.
    
    # Correction data
    old_value = Column(Text, nullable=True)  # Previous value
    new_value = Column(Text, nullable=False)  # Corrected value
    correction_reason = Column(Text, nullable=True)  # Reason for correction
    
    # Status and approval
    status = Column(Enum(CorrectionStatus), default=CorrectionStatus.PENDING, nullable=False, index=True)
    corrected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Version tracking
    version = Column(String(20), nullable=False, default="1.0")  # Version number
    previous_correction_id = Column(UUID(as_uuid=True), ForeignKey("data_corrections.id"), nullable=True)  # Link to previous correction
    
    # Metadata
    metadata = Column(JSON, nullable=True)  # Additional metadata (source, confidence, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="data_corrections")
    company_data = relationship("CompanyData", foreign_keys=[company_data_id])
    corrector = relationship("User", foreign_keys=[corrected_by])
    approver = relationship("User", foreign_keys=[approved_by])
    previous_correction = relationship("DataCorrection", remote_side=[id], foreign_keys=[previous_correction_id])
    
    def __repr__(self):
        return f"<DataCorrection(id={self.id}, company_id={self.company_id}, field_name={self.field_name}, status={self.status})>"

