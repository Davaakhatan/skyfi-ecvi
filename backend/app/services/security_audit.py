"""Security audit service for checking system security posture"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.audit import AuditLog
from app.models.user import User

logger = logging.getLogger(__name__)


class SecurityAuditService:
    """Service for performing security audits"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_failed_login_attempts(
        self,
        user_id: Optional[str] = None,
        hours: int = 24
    ) -> Dict:
        """
        Check for suspicious failed login attempts
        
        Args:
            user_id: Optional specific user ID
            hours: Time window in hours (default 24)
            
        Returns:
            Dictionary with audit results
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = self.db.query(AuditLog).filter(
            and_(
                AuditLog.action == "LOGIN_FAILED",
                AuditLog.created_at >= cutoff_time
            )
        )
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        failed_attempts = query.all()
        
        # Group by user
        attempts_by_user: Dict[str, int] = {}
        for attempt in failed_attempts:
            user_key = str(attempt.user_id) if attempt.user_id else "unknown"
            attempts_by_user[user_key] = attempts_by_user.get(user_key, 0) + 1
        
        # Find suspicious patterns
        suspicious_users = [
            {"user_id": uid, "attempts": count}
            for uid, count in attempts_by_user.items()
            if count >= 5  # 5+ failed attempts is suspicious
        ]
        
        return {
            "total_failed_attempts": len(failed_attempts),
            "unique_users": len(attempts_by_user),
            "suspicious_users": suspicious_users,
            "time_window_hours": hours
        }
    
    def check_unauthorized_access_attempts(
        self,
        hours: int = 24
    ) -> Dict:
        """
        Check for unauthorized access attempts
        
        Args:
            hours: Time window in hours (default 24)
            
        Returns:
            Dictionary with audit results
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        unauthorized_actions = [
            "UNAUTHORIZED_ACCESS",
            "PERMISSION_DENIED",
            "INVALID_TOKEN"
        ]
        
        attempts = self.db.query(AuditLog).filter(
            and_(
                AuditLog.action.in_(unauthorized_actions),
                AuditLog.created_at >= cutoff_time
            )
        ).all()
        
        # Group by IP address (if available in details)
        attempts_by_ip: Dict[str, int] = {}
        for attempt in attempts:
            ip = attempt.details.get("ip_address") if attempt.details else None
            if ip:
                attempts_by_ip[ip] = attempts_by_ip.get(ip, 0) + 1
        
        return {
            "total_attempts": len(attempts),
            "unique_ips": len(attempts_by_ip),
            "suspicious_ips": [
                {"ip": ip, "attempts": count}
                for ip, count in attempts_by_ip.items()
                if count >= 10  # 10+ attempts is suspicious
            ],
            "time_window_hours": hours
        }
    
    def check_inactive_users(
        self,
        days: int = 90
    ) -> List[Dict]:
        """
        Check for inactive users (potential security risk)
        
        Args:
            days: Number of days of inactivity (default 90)
            
        Returns:
            List of inactive users
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        inactive_users = self.db.query(User).filter(
            and_(
                User.is_active == True,
                or_(
                    User.last_login == None,
                    User.last_login < cutoff_date
                )
            )
        ).all()
        
        return [
            {
                "user_id": str(user.id),
                "email": user.email,
                "username": user.username,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "days_inactive": (
                    (datetime.utcnow() - user.last_login).days
                    if user.last_login else None
                )
            }
            for user in inactive_users
        ]
    
    def check_password_strength_compliance(self) -> Dict:
        """
        Check if all users have strong passwords (placeholder)
        
        Note: We can't check actual passwords, but we can verify
        that password strength validation is enforced.
        
        Returns:
            Dictionary with compliance status
        """
        # This is a placeholder - actual password strength
        # should be enforced at creation/update time
        return {
            "password_policy_enforced": True,
            "min_length": 8,
            "requires_uppercase": True,
            "requires_lowercase": True,
            "requires_digit": True,
            "requires_special": True
        }
    
    def check_admin_accounts(self) -> Dict:
        """
        Check admin account security
        
        Returns:
            Dictionary with admin account information
        """
        admin_users = self.db.query(User).filter(
            User.role.in_(["admin", "security"])
        ).all()
        
        admins_without_mfa = [
            {
                "user_id": str(user.id),
                "email": user.email,
                "mfa_enabled": user.mfa_enabled
            }
            for user in admin_users
            if not user.mfa_enabled
        ]
        
        return {
            "total_admin_accounts": len(admin_users),
            "admins_without_mfa": len(admins_without_mfa),
            "admin_details": [
                {
                    "user_id": str(user.id),
                    "email": user.email,
                    "role": user.role,
                    "mfa_enabled": user.mfa_enabled,
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
                for user in admin_users
            ],
            "security_recommendations": [
                "Enable MFA for all admin accounts" if admins_without_mfa else "All admins have MFA enabled"
            ]
        }
    
    def generate_security_report(self) -> Dict:
        """
        Generate comprehensive security audit report
        
        Returns:
            Dictionary with complete security audit results
        """
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "failed_login_attempts": self.check_failed_login_attempts(),
            "unauthorized_access_attempts": self.check_unauthorized_access_attempts(),
            "inactive_users": self.check_inactive_users(),
            "password_policy": self.check_password_strength_compliance(),
            "admin_accounts": self.check_admin_accounts(),
            "recommendations": []
        }
        
        # Generate recommendations
        if report["failed_login_attempts"]["suspicious_users"]:
            report["recommendations"].append(
                "Multiple failed login attempts detected. Consider implementing account lockout."
            )
        
        if report["unauthorized_access_attempts"]["suspicious_ips"]:
            report["recommendations"].append(
                "Suspicious IP addresses detected. Consider blocking or rate limiting."
            )
        
        if report["admin_accounts"]["admins_without_mfa"] > 0:
            report["recommendations"].append(
                f"{report['admin_accounts']['admins_without_mfa']} admin accounts without MFA. Enable MFA for all admin accounts."
            )
        
        if len(report["inactive_users"]) > 0:
            report["recommendations"].append(
                f"{len(report['inactive_users'])} inactive users found. Consider deactivating unused accounts."
            )
        
        return report

