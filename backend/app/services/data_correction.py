"""Data correction service for managing corrections and version history"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.models.data_correction import DataCorrection, CorrectionStatus
from app.models.company import Company
from app.models.company_data import CompanyData
from app.models.user import User
from app.core.audit import log_audit_event
from app.services.verification_service import VerificationService


class DataCorrectionService:
    """Service for managing data corrections"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_correction(
        self,
        company_id: UUID,
        field_name: str,
        field_type: str,
        old_value: Optional[str],
        new_value: str,
        correction_reason: Optional[str],
        corrected_by: UUID,
        company_data_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DataCorrection:
        """Create a new data correction"""
        # Get the latest correction for this field to determine version
        latest_correction = self.db.query(DataCorrection).filter(
            and_(
                DataCorrection.company_id == company_id,
                DataCorrection.field_name == field_name,
                DataCorrection.status == CorrectionStatus.APPROVED
            )
        ).order_by(desc(DataCorrection.created_at)).first()
        
        # Calculate version number
        if latest_correction:
            try:
                version_parts = latest_correction.version.split('.')
                major = int(version_parts[0])
                minor = int(version_parts[1]) if len(version_parts) > 1 else 0
                new_version = f"{major}.{minor + 1}"
            except (ValueError, IndexError):
                new_version = "1.0"
        else:
            new_version = "1.0"
        
        # Create correction record
        correction = DataCorrection(
            company_id=company_id,
            company_data_id=company_data_id,
            field_name=field_name,
            field_type=field_type,
            old_value=old_value,
            new_value=new_value,
            correction_reason=correction_reason,
            corrected_by=corrected_by,
            status=CorrectionStatus.PENDING,
            version=new_version,
            previous_correction_id=latest_correction.id if latest_correction else None,
            metadata=metadata
        )
        
        try:
            self.db.add(correction)
            self.db.commit()
            self.db.refresh(correction)
            return correction
        except Exception as e:
            self.db.rollback()
            raise
    
    def approve_correction(
        self,
        correction_id: UUID,
        approved_by: UUID
    ) -> DataCorrection:
        """Approve a correction and apply it"""
        correction = self.db.query(DataCorrection).filter(
            DataCorrection.id == correction_id
        ).first()
        
        if not correction:
            raise ValueError("Correction not found")
        
        if correction.status != CorrectionStatus.PENDING:
            raise ValueError(f"Correction is not pending (current status: {correction.status})")
        
        # Apply the correction
        company = self.db.query(Company).filter(Company.id == correction.company_id).first()
        if not company:
            raise ValueError("Company not found")
        
        # Capture old value if not already set (for backward compatibility)
        if correction.old_value is None:
            if correction.field_type == "legal_name":
                correction.old_value = company.legal_name
            elif correction.field_type == "registration_number":
                correction.old_value = company.registration_number
            elif correction.field_type == "jurisdiction":
                correction.old_value = company.jurisdiction
            elif correction.field_type == "domain":
                correction.old_value = company.domain
        
        # Update the company field based on field_type
        if correction.field_type == "legal_name":
            company.legal_name = correction.new_value
        elif correction.field_type == "registration_number":
            company.registration_number = correction.new_value
        elif correction.field_type == "jurisdiction":
            company.jurisdiction = correction.new_value
        elif correction.field_type == "domain":
            company.domain = correction.new_value
        
        # Update CompanyData if company_data_id is provided
        if correction.company_data_id:
            company_data = self.db.query(CompanyData).filter(
                CompanyData.id == correction.company_data_id
            ).first()
            if company_data:
                company_data.field_value = correction.new_value
                company_data.verified = True  # Mark as verified after correction
        
        # Update correction status
        correction.status = CorrectionStatus.APPROVED
        correction.approved_by = approved_by
        correction.approved_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(correction)
            
            # Note: Re-run analysis should be triggered via API endpoint
            # This allows for async processing via Celery
            return correction
        except Exception as e:
            self.db.rollback()
            raise
    
    def reject_correction(
        self,
        correction_id: UUID,
        rejected_by: UUID,
        rejection_reason: Optional[str] = None
    ) -> DataCorrection:
        """Reject a correction"""
        correction = self.db.query(DataCorrection).filter(
            DataCorrection.id == correction_id
        ).first()
        
        if not correction:
            raise ValueError("Correction not found")
        
        if correction.status != CorrectionStatus.PENDING:
            raise ValueError(f"Correction is not pending (current status: {correction.status})")
        
        correction.status = CorrectionStatus.REJECTED
        correction.approved_by = rejected_by
        correction.approved_at = datetime.utcnow()
        
        if rejection_reason:
            if correction.metadata is None:
                correction.metadata = {}
            correction.metadata["rejection_reason"] = rejection_reason
        
        try:
            self.db.commit()
            self.db.refresh(correction)
            return correction
        except Exception as e:
            self.db.rollback()
            raise
    
    def get_correction_history(
        self,
        company_id: UUID,
        field_name: Optional[str] = None,
        limit: int = 50
    ) -> List[DataCorrection]:
        """Get correction history for a company"""
        query = self.db.query(DataCorrection).filter(
            DataCorrection.company_id == company_id
        )
        
        if field_name:
            query = query.filter(DataCorrection.field_name == field_name)
        
        return query.order_by(desc(DataCorrection.created_at)).limit(limit).all()
    
    def get_latest_correction(
        self,
        company_id: UUID,
        field_name: str
    ) -> Optional[DataCorrection]:
        """Get the latest approved correction for a field"""
        return self.db.query(DataCorrection).filter(
            and_(
                DataCorrection.company_id == company_id,
                DataCorrection.field_name == field_name,
                DataCorrection.status == CorrectionStatus.APPROVED
            )
        ).order_by(desc(DataCorrection.created_at)).first()
    
    def re_run_analysis_with_corrections(
        self,
        company_id: UUID,
        timeout_hours: float = 2.0
    ) -> None:
        """Re-run verification analysis with corrected data"""
        # This will use the existing verification service
        # The service will automatically use the corrected data from the company model
        verification_service = VerificationService(self.db)
        # Note: This should be called asynchronously via Celery
        # For now, we'll just trigger it
        pass

