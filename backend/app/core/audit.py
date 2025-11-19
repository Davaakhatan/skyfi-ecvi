"""Audit logging functionality"""

from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request

from app.models.audit import AuditLog
from app.models.user import User
import uuid


def log_audit_event(
    db: Session,
    user: Optional[User],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[uuid.UUID] = None,
    details: Optional[dict] = None,
    request: Optional[Request] = None
) -> AuditLog:
    """Log an audit event"""
    ip_address = None
    user_agent = None
    
    if request:
        # Get IP address - handle test client and proxy scenarios
        ip_address = None
        if request.client:
            ip = request.client.host
            # TestClient uses "testclient" as hostname, convert to valid IP
            if ip == "testclient":
                ip_address = "127.0.0.1"
            elif ip and ip != "testclient":
                ip_address = ip
        # Also check X-Forwarded-For header for proxy scenarios
        if not ip_address:
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                # Take first IP from comma-separated list
                ip_address = forwarded.split(",")[0].strip()
        user_agent = request.headers.get("user-agent")
    
    audit_log = AuditLog(
        user_id=user.id if user else None,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    
    return audit_log

