"""User model"""

from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class User(Base):
    """User/Operator model"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="operator")  # operator, admin, compliance, security
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")
    reviews = relationship("Review", back_populates="reviewer")
    corrections_made = relationship("DataCorrection", foreign_keys="DataCorrection.corrected_by", back_populates="corrector")
    corrections_approved = relationship("DataCorrection", foreign_keys="DataCorrection.approved_by", back_populates="approver")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

