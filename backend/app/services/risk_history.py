"""Risk score history tracking service"""

from typing import List, Dict, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.verification_result import VerificationResult, VerificationStatus


class RiskHistoryService:
    """Service for tracking and retrieving historical risk scores"""
    
    @staticmethod
    def get_risk_history(
        db: Session,
        company_id: UUID,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get historical risk scores for a company
        
        Args:
            db: Database session
            company_id: Company ID
            limit: Maximum number of records to return (None = all)
        
        Returns:
            List of historical risk score records
        """
        query = db.query(VerificationResult).filter(
            VerificationResult.company_id == company_id,
            VerificationResult.verification_status == VerificationStatus.COMPLETED
        ).order_by(desc(VerificationResult.created_at))
        
        if limit:
            query = query.limit(limit)
        
        results = query.all()
        
        history = []
        for result in results:
            history.append({
                "verification_id": str(result.id),
                "risk_score": result.risk_score,
                "risk_category": result.risk_category.value if result.risk_category else None,
                "verified_at": result.analysis_completed_at.isoformat() if result.analysis_completed_at else None,
                "created_at": result.created_at.isoformat() if result.created_at else None,
            })
        
        return history
    
    @staticmethod
    def get_risk_trend(
        db: Session,
        company_id: UUID,
        days: int = 30
    ) -> Dict:
        """
        Get risk score trend over time
        
        Args:
            db: Database session
            company_id: Company ID
            days: Number of days to look back
        
        Returns:
            Dictionary with trend analysis
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        results = db.query(VerificationResult).filter(
            VerificationResult.company_id == company_id,
            VerificationResult.verification_status == VerificationStatus.COMPLETED,
            VerificationResult.created_at >= cutoff_date
        ).order_by(VerificationResult.created_at).all()
        
        if not results:
            return {
                "company_id": str(company_id),
                "period_days": days,
                "total_verifications": 0,
                "average_score": None,
                "trend": "no_data",
                "score_changes": []
            }
        
        scores = [r.risk_score for r in results]
        average_score = sum(scores) / len(scores)
        
        # Calculate trend
        if len(scores) >= 2:
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            if second_avg < first_avg - 5:
                trend = "improving"
            elif second_avg > first_avg + 5:
                trend = "worsening"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Calculate score changes
        score_changes = []
        for i in range(1, len(results)):
            prev_score = results[i-1].risk_score
            curr_score = results[i].risk_score
            change = curr_score - prev_score
            score_changes.append({
                "from_score": prev_score,
                "to_score": curr_score,
                "change": change,
                "change_percentage": round((change / prev_score * 100) if prev_score > 0 else 0, 2),
                "date": results[i].created_at.isoformat() if results[i].created_at else None
            })
        
        return {
            "company_id": str(company_id),
            "period_days": days,
            "total_verifications": len(results),
            "average_score": round(average_score, 2),
            "min_score": min(scores),
            "max_score": max(scores),
            "latest_score": scores[-1],
            "trend": trend,
            "score_changes": score_changes
        }
    
    @staticmethod
    def get_latest_risk_score(
        db: Session,
        company_id: UUID
    ) -> Optional[Dict]:
        """
        Get the latest risk score for a company
        
        Args:
            db: Database session
            company_id: Company ID
        
        Returns:
            Latest risk score record or None
        """
        result = db.query(VerificationResult).filter(
            VerificationResult.company_id == company_id,
            VerificationResult.verification_status == VerificationStatus.COMPLETED
        ).order_by(desc(VerificationResult.created_at)).first()
        
        if not result:
            return None
        
        return {
            "verification_id": str(result.id),
            "risk_score": result.risk_score,
            "risk_category": result.risk_category.value if result.risk_category else None,
            "verified_at": result.analysis_completed_at.isoformat() if result.analysis_completed_at else None,
            "created_at": result.created_at.isoformat() if result.created_at else None,
        }

