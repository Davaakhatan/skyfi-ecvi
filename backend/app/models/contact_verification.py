"""Contact verification result model"""

from sqlalchemy import Column, String, Text, Boolean, Numeric, DateTime, ForeignKey, func, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.database import Base


class ContactType(str, enum.Enum):
    """Contact type enumeration"""
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    NAME = "NAME"


class ContactVerificationStatus(str, enum.Enum):
    """Contact verification status enumeration"""
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class ContactVerificationResult(Base):
    """Contact verification result model"""
    
    __tablename__ = "contact_verification_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    verification_result_id = Column(UUID(as_uuid=True), ForeignKey("verification_results.id"), nullable=True, index=True)
    
    # Contact information
    contact_type = Column(Enum(ContactType), nullable=False, index=True)
    contact_value = Column(String(255), nullable=False)  # email, phone, or name
    country_code = Column(String(10), nullable=True)  # For phone numbers
    
    # Verification results
    format_valid = Column(Boolean, default=False, nullable=False)
    domain_exists = Column(Boolean, nullable=True)  # For emails
    mx_record_exists = Column(Boolean, nullable=True)  # For emails
    email_exists = Column(Boolean, nullable=True)  # For emails - actual existence check
    carrier_valid = Column(Boolean, nullable=True)  # For phones
    carrier_name = Column(String(100), nullable=True)  # For phones
    line_type = Column(String(50), nullable=True)  # mobile, landline, voip - for phones
    name_verified = Column(Boolean, nullable=True)  # For names
    public_records_match = Column(Boolean, nullable=True)  # For names
    social_profiles_match = Column(Boolean, nullable=True)  # For names
    
    # Overall status
    status = Column(Enum(ContactVerificationStatus), default=ContactVerificationStatus.PENDING, nullable=False, index=True)
    confidence_score = Column(Numeric(5, 2), nullable=True)  # 0.00-1.00
    risk_score = Column(Numeric(5, 2), nullable=True)  # 0.00-100.00
    
    # Additional metadata
    verification_details = Column(JSON, nullable=True)  # Additional verification data
    errors = Column(JSON, nullable=True)  # List of errors encountered
    sources_checked = Column(JSON, nullable=True)  # List of sources checked
    
    # Timestamps
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="contact_verifications")
    verification_result = relationship("VerificationResult", back_populates="contact_verifications")
    
    def __repr__(self):
        return f"<ContactVerificationResult(id={self.id}, company_id={self.company_id}, contact_type={self.contact_type}, status={self.status})>"

