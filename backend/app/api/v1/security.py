"""Security audit API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import User
from app.core.auth import get_current_active_user, require_role
from app.services.security_audit import SecurityAuditService

router = APIRouter()


class SecurityReportResponse(BaseModel):
    """Security audit report response"""
    generated_at: str
    failed_login_attempts: dict
    unauthorized_access_attempts: dict
    inactive_users: list
    password_policy: dict
    admin_accounts: dict
    recommendations: list


@router.get("/audit/report", response_model=SecurityReportResponse)
async def get_security_audit_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "security"))
):
    """
    Generate comprehensive security audit report
    
    Requires admin or security role.
    """
    audit_service = SecurityAuditService(db)
    report = audit_service.generate_security_report()
    
    return report


@router.get("/audit/failed-logins")
async def get_failed_login_attempts(
    user_id: Optional[str] = Query(None, description="Optional user ID filter"),
    hours: int = Query(24, ge=1, le=168, description="Time window in hours"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "security"))
):
    """
    Get failed login attempt statistics
    
    Requires admin or security role.
    """
    audit_service = SecurityAuditService(db)
    result = audit_service.check_failed_login_attempts(
        user_id=user_id,
        hours=hours
    )
    
    return result


@router.get("/audit/unauthorized-access")
async def get_unauthorized_access_attempts(
    hours: int = Query(24, ge=1, le=168, description="Time window in hours"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "security"))
):
    """
    Get unauthorized access attempt statistics
    
    Requires admin or security role.
    """
    audit_service = SecurityAuditService(db)
    result = audit_service.check_unauthorized_access_attempts(hours=hours)
    
    return result


@router.get("/audit/inactive-users")
async def get_inactive_users(
    days: int = Query(90, ge=1, le=365, description="Days of inactivity"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "security"))
):
    """
    Get list of inactive users
    
    Requires admin or security role.
    """
    audit_service = SecurityAuditService(db)
    result = audit_service.check_inactive_users(days=days)
    
    return {
        "inactive_users": result,
        "total_count": len(result),
        "days_threshold": days
    }


@router.get("/audit/admin-accounts")
async def get_admin_accounts_security(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "security"))
):
    """
    Get admin account security status
    
    Requires admin or security role.
    """
    audit_service = SecurityAuditService(db)
    result = audit_service.check_admin_accounts()
    
    return result

