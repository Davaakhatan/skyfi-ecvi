"""Confidence scoring service for verification results"""

from typing import Dict, List, Optional
from decimal import Decimal


class ConfidenceScoringService:
    """Service for calculating confidence scores for verification data"""
    
    @staticmethod
    def calculate_source_confidence(
        source: str,
        source_type: str,
        data_quality: float,
        verification_status: bool
    ) -> float:
        """
        Calculate confidence score for a data source
        
        Args:
            source: Source identifier (e.g., "companies_house", "dns_lookup")
            source_type: Type of source ("official_registry", "public_api", "web_scraping", etc.)
            data_quality: Data quality score (0.0-1.0)
            verification_status: Whether data was verified
        
        Returns:
            Confidence score (0.0-1.0)
        """
        # Base confidence by source type
        source_type_weights = {
            "official_registry": 0.95,  # Government registries are highly trusted
            "public_api": 0.80,  # Public APIs are generally reliable
            "dns_lookup": 0.75,  # DNS data is reliable but can be manipulated
            "web_scraping": 0.60,  # Web scraping is less reliable
            "user_provided": 0.50,  # User-provided data needs verification
            "ai_inferred": 0.65,  # AI-inferred data has moderate confidence
        }
        
        base_confidence = source_type_weights.get(source_type, 0.50)
        
        # Adjust based on data quality
        quality_adjustment = data_quality * 0.2  # Up to 20% adjustment
        
        # Adjust based on verification status
        verification_adjustment = 0.1 if verification_status else -0.1
        
        confidence = base_confidence + quality_adjustment + verification_adjustment
        
        # Clamp to 0.0-1.0
        return max(0.0, min(1.0, confidence))
    
    @staticmethod
    def calculate_field_confidence(
        field_name: str,
        field_value: Optional[str],
        sources: List[Dict],
        cross_validation: bool = True
    ) -> float:
        """
        Calculate confidence score for a specific field based on multiple sources
        
        Args:
            field_name: Name of the field (e.g., "legal_name", "address")
            field_value: The field value to score
            sources: List of sources with this field [{"source": "api1", "value": "Company Inc", "confidence": 0.8}, ...]
            cross_validation: Whether to use cross-validation across sources
        
        Returns:
            Confidence score (0.0-1.0)
        """
        if not sources:
            return 0.0
        
        if not field_value:
            return 0.0
        
        if not cross_validation:
            # Return highest source confidence
            return max((s.get("confidence", 0.5) for s in sources), default=0.5)
        
        # Calculate weighted average based on source confidence
        total_weight = 0.0
        weighted_sum = 0.0
        
        for source in sources:
            source_confidence = source.get("confidence", 0.5)
            source_value = source.get("value", "")
            
            # Check if value matches
            if source_value and source_value.lower().strip() == field_value.lower().strip():
                # Matching value gets full weight
                weight = source_confidence
            else:
                # Non-matching value reduces confidence
                weight = source_confidence * 0.3
            
            weighted_sum += weight
            total_weight += source_confidence
        
        if total_weight == 0:
            return 0.0
        
        # Calculate consistency bonus
        matching_sources = sum(
            1 for s in sources
            if s.get("value", "").lower().strip() == field_value.lower().strip()
        )
        consistency_ratio = matching_sources / len(sources) if sources else 0
        
        # Base confidence from weighted average
        base_confidence = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Apply consistency bonus
        consistency_bonus = consistency_ratio * 0.2
        
        confidence = base_confidence + consistency_bonus
        
        return max(0.0, min(1.0, confidence))
    
    @staticmethod
    def calculate_overall_verification_confidence(
        dns_confidence: float,
        registration_confidence: float,
        contact_confidence: float,
        address_confidence: float,
        discrepancy_score: float
    ) -> Dict:
        """
        Calculate overall confidence score for verification
        
        Args:
            dns_confidence: DNS verification confidence (0.0-1.0)
            registration_confidence: Registration data confidence (0.0-1.0)
            contact_confidence: Contact information confidence (0.0-1.0)
            address_confidence: Address verification confidence (0.0-1.0)
            discrepancy_score: Data consistency score from discrepancy detection (0.0-1.0)
        
        Returns:
            Dictionary with overall confidence and breakdown
        """
        # Weighted average with weights
        weights = {
            "dns": 0.20,
            "registration": 0.35,  # Most important
            "contact": 0.25,
            "address": 0.20,
        }
        
        weighted_sum = (
            dns_confidence * weights["dns"] +
            registration_confidence * weights["registration"] +
            contact_confidence * weights["contact"] +
            address_confidence * weights["address"]
        )
        
        # Apply discrepancy penalty
        discrepancy_penalty = (1.0 - discrepancy_score) * 0.15
        
        overall_confidence = weighted_sum - discrepancy_penalty
        
        # Clamp to 0.0-1.0
        overall_confidence = max(0.0, min(1.0, overall_confidence))
        
        # Determine confidence level
        if overall_confidence >= 0.9:
            level = "very_high"
        elif overall_confidence >= 0.75:
            level = "high"
        elif overall_confidence >= 0.60:
            level = "medium"
        elif overall_confidence >= 0.40:
            level = "low"
        else:
            level = "very_low"
        
        return {
            "overall_confidence": round(overall_confidence, 3),
            "confidence_level": level,
            "breakdown": {
                "dns": round(dns_confidence, 3),
                "registration": round(registration_confidence, 3),
                "contact": round(contact_confidence, 3),
                "address": round(address_confidence, 3),
            },
            "discrepancy_score": round(discrepancy_score, 3),
            "discrepancy_penalty": round(discrepancy_penalty, 3)
        }
    
    @staticmethod
    def calculate_source_reliability_avg(sources: List[Dict]) -> float:
        """
        Calculate average source reliability from list of sources
        
        Args:
            sources: List of source dictionaries with reliability scores
        
        Returns:
            Average reliability (0.0-1.0)
        """
        if not sources:
            return 0.5  # Default moderate reliability
        
        reliabilities = [s.get("reliability", 0.5) for s in sources]
        return sum(reliabilities) / len(reliabilities) if reliabilities else 0.5

