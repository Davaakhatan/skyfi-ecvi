"""Data discrepancy detection service"""

from typing import Dict, List, Optional, Tuple
from collections import Counter


class DiscrepancyDetectionService:
    """Service for detecting discrepancies in company verification data"""
    
    @staticmethod
    def detect_name_discrepancies(
        legal_name: str,
        sources: List[Dict[str, str]]
    ) -> Dict:
        """
        Detect discrepancies in company name across sources
        
        Args:
            legal_name: Primary legal name
            sources: List of sources with name data [{"source": "api1", "name": "Company Inc"}, ...]
        
        Returns:
            Dictionary with discrepancy analysis
        """
        result = {
            "legal_name": legal_name,
            "sources_checked": len(sources),
            "matches": 0,
            "discrepancies": [],
            "confidence": 0.0,
            "severity": "none"  # none, low, medium, high
        }
        
        if not sources:
            result["confidence"] = 0.0
            result["severity"] = "high"
            return result
        
        # Normalize names for comparison
        normalized_primary = DiscrepancyDetectionService._normalize_name(legal_name)
        matches = 0
        
        for source in sources:
            source_name = source.get("name", "")
            normalized_source = DiscrepancyDetectionService._normalize_name(source_name)
            
            if normalized_primary == normalized_source:
                matches += 1
            else:
                similarity = DiscrepancyDetectionService._calculate_similarity(
                    normalized_primary, normalized_source
                )
                result["discrepancies"].append({
                    "source": source.get("source", "unknown"),
                    "reported_name": source_name,
                    "similarity": similarity,
                    "type": "name_mismatch"
                })
        
        result["matches"] = matches
        match_ratio = matches / len(sources) if sources else 0
        result["confidence"] = match_ratio
        
        # Determine severity
        if match_ratio >= 0.9:
            result["severity"] = "none"
        elif match_ratio >= 0.7:
            result["severity"] = "low"
        elif match_ratio >= 0.5:
            result["severity"] = "medium"
        else:
            result["severity"] = "high"
        
        return result
    
    @staticmethod
    def detect_address_discrepancies(
        primary_address: Dict[str, Optional[str]],
        sources: List[Dict[str, Dict[str, Optional[str]]]]
    ) -> Dict:
        """
        Detect discrepancies in address data across sources
        
        Args:
            primary_address: Primary address dict with keys: street, city, state, country, postal_code
            sources: List of sources with address dicts
        
        Returns:
            Dictionary with discrepancy analysis
        """
        result = {
            "primary_address": primary_address,
            "sources_checked": len(sources),
            "matches": 0,
            "discrepancies": [],
            "confidence": 0.0,
            "severity": "none"
        }
        
        if not sources:
            result["confidence"] = 0.0
            result["severity"] = "high"
            return result
        
        matches = 0
        address_fields = ["street", "city", "state", "country", "postal_code"]
        
        for source in sources:
            source_address = source.get("address", {})
            field_matches = 0
            field_discrepancies = []
            
            for field in address_fields:
                primary_value = DiscrepancyDetectionService._normalize_text(
                    primary_address.get(field) or ""
                )
                source_value = DiscrepancyDetectionService._normalize_text(
                    source_address.get(field) or ""
                )
                
                if primary_value and source_value:
                    if primary_value == source_value:
                        field_matches += 1
                    else:
                        similarity = DiscrepancyDetectionService._calculate_similarity(
                            primary_value, source_value
                        )
                        if similarity < 0.8:  # Significant difference
                            field_discrepancies.append({
                                "field": field,
                                "primary": primary_address.get(field),
                                "source": source_address.get(field),
                                "similarity": similarity
                            })
            
            match_ratio = field_matches / len([f for f in address_fields if primary_address.get(f)])
            
            if match_ratio >= 0.8:
                matches += 1
            else:
                result["discrepancies"].append({
                    "source": source.get("source", "unknown"),
                    "field_discrepancies": field_discrepancies,
                    "match_ratio": match_ratio,
                    "type": "address_mismatch"
                })
        
        result["matches"] = matches
        match_ratio = matches / len(sources) if sources else 0
        result["confidence"] = match_ratio
        
        # Determine severity
        if match_ratio >= 0.9:
            result["severity"] = "none"
        elif match_ratio >= 0.7:
            result["severity"] = "low"
        elif match_ratio >= 0.5:
            result["severity"] = "medium"
        else:
            result["severity"] = "high"
        
        return result
    
    @staticmethod
    def detect_registration_discrepancies(
        registration_number: str,
        jurisdiction: Optional[str],
        sources: List[Dict[str, str]]
    ) -> Dict:
        """
        Detect discrepancies in registration number across sources
        
        Args:
            registration_number: Primary registration number
            jurisdiction: Jurisdiction code
            sources: List of sources with registration data
        
        Returns:
            Dictionary with discrepancy analysis
        """
        result = {
            "registration_number": registration_number,
            "jurisdiction": jurisdiction,
            "sources_checked": len(sources),
            "matches": 0,
            "discrepancies": [],
            "confidence": 0.0,
            "severity": "none"
        }
        
        if not sources:
            result["confidence"] = 0.0
            result["severity"] = "high"
            return result
        
        matches = 0
        normalized_primary = registration_number.upper().strip() if registration_number else ""
        
        for source in sources:
            source_reg = source.get("registration_number", "").upper().strip()
            
            if normalized_primary == source_reg:
                matches += 1
            else:
                result["discrepancies"].append({
                    "source": source.get("source", "unknown"),
                    "reported_registration": source_reg,
                    "type": "registration_mismatch"
                })
        
        result["matches"] = matches
        match_ratio = matches / len(sources) if sources else 0
        result["confidence"] = match_ratio
        
        # Registration number should be exact match
        if match_ratio == 1.0:
            result["severity"] = "none"
        elif match_ratio >= 0.7:
            result["severity"] = "low"
        elif match_ratio >= 0.5:
            result["severity"] = "medium"
        else:
            result["severity"] = "high"
        
        return result
    
    @staticmethod
    def calculate_overall_consistency(
        name_result: Dict,
        address_result: Dict,
        registration_result: Dict
    ) -> Dict:
        """
        Calculate overall data consistency score
        
        Args:
            name_result: Name discrepancy detection result
            address_result: Address discrepancy detection result
            registration_result: Registration discrepancy detection result
        
        Returns:
            Dictionary with overall consistency metrics
        """
        results = [name_result, address_result, registration_result]
        
        # Calculate weighted average confidence
        weights = {"name": 0.3, "address": 0.3, "registration": 0.4}
        total_confidence = (
            name_result.get("confidence", 0) * weights["name"] +
            address_result.get("confidence", 0) * weights["address"] +
            registration_result.get("confidence", 0) * weights["registration"]
        )
        
        # Count total discrepancies
        total_discrepancies = sum(len(r.get("discrepancies", [])) for r in results)
        
        # Determine overall severity (worst case)
        severities = ["none", "low", "medium", "high"]
        severity_values = {s: i for i, s in enumerate(severities)}
        max_severity = max(
            (severity_values.get(r.get("severity", "high"), 3) for r in results),
            default=3
        )
        overall_severity = severities[max_severity]
        
        return {
            "overall_confidence": total_confidence,
            "total_discrepancies": total_discrepancies,
            "severity": overall_severity,
            "name_confidence": name_result.get("confidence", 0),
            "address_confidence": address_result.get("confidence", 0),
            "registration_confidence": registration_result.get("confidence", 0),
            "all_discrepancies": [
                {"type": "name", "data": name_result.get("discrepancies", [])},
                {"type": "address", "data": address_result.get("discrepancies", [])},
                {"type": "registration", "data": registration_result.get("discrepancies", [])},
            ]
        }
    
    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize company name for comparison"""
        if not name:
            return ""
        # Remove common suffixes and normalize
        normalized = name.upper().strip()
        # Remove common business suffixes
        suffixes = ["INC", "LLC", "LTD", "CORP", "CORPORATION", "CO", "LP", "LLP"]
        for suffix in suffixes:
            if normalized.endswith(f" {suffix}"):
                normalized = normalized[:-len(f" {suffix}")].strip()
        # Remove punctuation and extra spaces
        normalized = " ".join(normalized.split())
        return normalized
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        return " ".join(text.upper().strip().split())
    
    @staticmethod
    def _calculate_similarity(str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings (simple implementation)
        Uses Jaccard similarity on word sets
        """
        if not str1 or not str2:
            return 0.0
        
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0

