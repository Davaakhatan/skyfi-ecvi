"""Celery tasks for company analysis and verification"""

from datetime import datetime, timedelta
from uuid import UUID
from celery import Task
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.company import Company
from app.models.verification_result import VerificationResult, VerificationStatus
from app.services.verification_service import VerificationService


class VerificationTask(Task):
    """Custom task class with database session management"""
    
    _db: Session = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        """Clean up database session after task completion"""
        if self._db:
            self._db.close()
            self._db = None


@celery_app.task(
    bind=True,
    base=VerificationTask,
    name="verify_company",
    max_retries=3,
    default_retry_delay=60,  # 1 minute
    time_limit=7200,  # 2 hours hard limit
    soft_time_limit=7200,  # 2 hours soft limit
)
def verify_company_task(self, company_id: str, timeout_hours: float = 2.0):
    """
    Async task to verify a company
    
    Args:
        company_id: UUID string of company to verify
        timeout_hours: Maximum time to spend on verification (default 2 hours)
    
    Returns:
        Verification result ID
    """
    db = self.db
    company_uuid = UUID(company_id)
    
    try:
        # Check if verification is already in progress
        existing_result = db.query(VerificationResult).filter(
            VerificationResult.company_id == company_uuid,
            VerificationResult.verification_status == VerificationStatus.IN_PROGRESS
        ).first()
        
        if existing_result:
            # Update existing result
            verification_result = existing_result
        else:
            # Create new verification result
            verification_result = VerificationResult(
                company_id=company_uuid,
                risk_score=0,
                verification_status=VerificationStatus.IN_PROGRESS,
                analysis_started_at=datetime.utcnow()
            )
            db.add(verification_result)
            db.commit()
            db.refresh(verification_result)
        
        # Perform verification
        verification_service = VerificationService(db)
        
        # Calculate timeout
        start_time = datetime.utcnow()
        timeout_delta = timedelta(hours=timeout_hours)
        
        # Run verification (this is async in the service, but we're in a sync context)
        # Use asyncio.run to execute the async verification
        import asyncio
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # For Celery tasks, we need to create a new event loop
            # asyncio.run() creates a new event loop, runs the coroutine, and closes the loop
            result = asyncio.run(
                verification_service.verify_company(company_uuid, timeout_hours)
            )
        except RuntimeError as e:
            # Handle case where event loop already exists (shouldn't happen in Celery)
            logger.warning(f"Event loop issue: {e}. Attempting alternative approach.")
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    verification_service.verify_company(company_uuid, timeout_hours)
                )
                loop.close()
            except Exception as loop_error:
                logger.error(f"Failed to create event loop: {loop_error}")
                raise
        except Exception as e:
            logger.error(f"Error running verification: {e}")
            raise
        
        return str(result.id)
        
    except Exception as exc:
        # Mark verification as failed
        try:
            verification_result = db.query(VerificationResult).filter(
                VerificationResult.company_id == company_uuid
            ).order_by(VerificationResult.created_at.desc()).first()
            
            if verification_result:
                verification_result.verification_status = VerificationStatus.FAILED
                verification_result.analysis_completed_at = datetime.utcnow()
                db.commit()
        except Exception:
            pass
        
        # Retry on certain exceptions
        if isinstance(exc, (ConnectionError, TimeoutError)):
            raise self.retry(exc=exc)
        
        raise


@celery_app.task(
    bind=True,
    base=VerificationTask,
    name="get_verification_status",
    max_retries=2,
    default_retry_delay=10,
)
def get_verification_status_task(self, company_id: str):
    """
    Get current verification status for a company
    
    Args:
        company_id: UUID string of company
    
    Returns:
        Dictionary with verification status information
    """
    db = self.db
    company_uuid = UUID(company_id)
    
    try:
        verification_result = db.query(VerificationResult).filter(
            VerificationResult.company_id == company_uuid
        ).order_by(VerificationResult.created_at.desc()).first()
        
        if not verification_result:
            return {
                "status": "not_found",
                "company_id": company_id
            }
        
        # Check if task is still running
        task_id = None
        # TODO: Store task_id in verification_result or separate table
        
        return {
            "status": verification_result.verification_status.value,
            "company_id": company_id,
            "risk_score": verification_result.risk_score,
            "risk_category": verification_result.risk_category.value if verification_result.risk_category else None,
            "started_at": verification_result.analysis_started_at.isoformat() if verification_result.analysis_started_at else None,
            "completed_at": verification_result.analysis_completed_at.isoformat() if verification_result.analysis_completed_at else None,
            "task_id": task_id
        }
        
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    base=VerificationTask,
    name="cancel_verification",
    max_retries=2,
)
def cancel_verification_task(self, company_id: str):
    """
    Cancel an in-progress verification
    
    Args:
        company_id: UUID string of company
    
    Returns:
        Success status
    """
    db = self.db
    company_uuid = UUID(company_id)
    
    try:
        verification_result = db.query(VerificationResult).filter(
            VerificationResult.company_id == company_uuid,
            VerificationResult.verification_status == VerificationStatus.IN_PROGRESS
        ).first()
        
        if verification_result:
            verification_result.verification_status = VerificationStatus.FAILED
            verification_result.analysis_completed_at = datetime.utcnow()
            db.commit()
            
            # TODO: Revoke Celery task if we have task_id stored
        
        return {"success": True, "company_id": company_id}
        
    except Exception as exc:
        raise self.retry(exc=exc)

