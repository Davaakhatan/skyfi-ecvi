"""Company data model"""

from sqlalchemy import Column, String, Text, Boolean, Numeric, DateTime, ForeignKey, func, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.database import Base


class DataType(str, enum.Enum):
    """Data type enumeration"""
    REGISTRATION = "REGISTRATION"
    CONTACT = "CONTACT"
    ADDRESS = "ADDRESS"


class CompanyData(Base):
    """Company data model"""
    
    __tablename__ = "company_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    data_type = Column(Enum(DataType), nullable=False, index=True)
    field_name = Column(String(100), nullable=False)
    field_value = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)  # Source of the data
    confidence_score = Column(Numeric(5, 2), nullable=True)  # 0.00-1.00
    verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="company_data")
    
    def __repr__(self):
        return f"<CompanyData(id={self.id}, company_id={self.company_id}, data_type={self.data_type}, field_name={self.field_name})>"

