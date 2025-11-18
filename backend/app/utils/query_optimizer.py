"""Query optimization utilities"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session, Query
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import desc


def optimize_company_list_query(
    query: Query,
    include_reviews: bool = True,
    include_verifications: bool = True
) -> Query:
    """
    Optimize company list query with eager loading
    
    Args:
        query: Base company query
        include_reviews: Whether to eager load reviews
        include_verifications: Whether to eager load verification results
        
    Returns:
        Optimized query with eager loading
    """
    from app.models.company import Company
    from app.models.review import Review
    from app.models.verification_result import VerificationResult
    
    options = []
    
    if include_verifications:
        options.append(
            selectinload(Company.verification_results)
            .order_by(desc(VerificationResult.created_at))
            .limit(1)
        )
    
    if include_reviews:
        options.append(
            selectinload(Company.reviews)
            .order_by(desc(Review.reviewed_at))
            .limit(1)
        )
    
    if options:
        query = query.options(*options)
    
    return query


def batch_load_users(db: Session, user_ids: List[str]) -> Dict[str, Any]:
    """
    Batch load users to avoid N+1 queries
    
    Args:
        db: Database session
        user_ids: List of user IDs to load
        
    Returns:
        Dictionary mapping user ID to user object
    """
    from app.models.user import User
    from uuid import UUID
    
    if not user_ids:
        return {}
    
    # Convert string IDs to UUIDs
    uuids = []
    for uid in user_ids:
        try:
            uuids.append(UUID(uid))
        except ValueError:
            continue
    
    if not uuids:
        return {}
    
    users = db.query(User).filter(User.id.in_(uuids)).all()
    return {str(user.id): user for user in users}

