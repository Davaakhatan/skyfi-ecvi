"""Business directory API integrations for company data collection"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import httpx

from app.core.config import settings
from app.services.data_collection import DataCollectionService

logger = logging.getLogger(__name__)


class BusinessDirectoryService:
    """Service for collecting company data from business directories"""
    
    def __init__(self, data_collection_service: Optional[DataCollectionService] = None):
        self.data_collection = data_collection_service or DataCollectionService()
    
    def search_opencorporates(
        self,
        company_name: str,
        jurisdiction: Optional[str] = None,
        registration_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search OpenCorporates API for company information
        
        OpenCorporates provides free access to company registry data from multiple jurisdictions.
        API Documentation: https://api.opencorporates.com/documentation/API_Reference
        
        Args:
            company_name: Company name to search
            jurisdiction: Jurisdiction code (e.g., 'gb', 'us_ca', 'us_ny')
            registration_number: Company registration number (optional)
        
        Returns:
            Dictionary with company data from OpenCorporates
        """
        try:
            base_url = "https://api.opencorporates.com/v0.4/companies/search"
            params = {
                "q": company_name,
                "format": "json"
            }
            
            if jurisdiction:
                params["jurisdiction_code"] = jurisdiction
            
            if registration_number:
                params["company_number"] = registration_number
            
            result = self.data_collection.collect_from_api(
                source="opencorporates",
                endpoint=base_url,
                params=params,
                use_cache=True
            )
            
            if result.get("success"):
                data = result.get("data", {})
                companies = data.get("results", {}).get("companies", [])
                
                if companies:
                    # Return the first match
                    company_data = companies[0].get("company", {})
                    return {
                        "success": True,
                        "source": "opencorporates",
                        "data": {
                            "name": company_data.get("name"),
                            "company_number": company_data.get("company_number"),
                            "jurisdiction_code": company_data.get("jurisdiction_code"),
                            "company_type": company_data.get("company_type"),
                            "status": company_data.get("current_status"),
                            "incorporation_date": company_data.get("incorporation_date"),
                            "dissolution_date": company_data.get("dissolution_date"),
                            "registered_address": company_data.get("registered_address_in_full"),
                            "officers": company_data.get("officers", []),
                            "opencorporates_url": company_data.get("opencorporates_url")
                        },
                        "match_count": len(companies),
                        "collected_at": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": "No companies found",
                        "source": "opencorporates"
                    }
            else:
                return result
                
        except Exception as e:
            logger.error(f"OpenCorporates search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "opencorporates"
            }
    
    def search_crunchbase(
        self,
        company_name: str,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search Crunchbase API for company information
        
        Crunchbase provides company data including funding, employees, and business information.
        Requires API key from https://data.crunchbase.com/
        
        Args:
            company_name: Company name to search
            api_key: Crunchbase API key (optional, can be set in config)
        
        Returns:
            Dictionary with company data from Crunchbase
        """
        api_key = api_key or getattr(settings, 'CRUNCHBASE_API_KEY', None)
        
        if not api_key:
            logger.warning("Crunchbase API key not configured")
            return {
                "success": False,
                "error": "API key not configured",
                "source": "crunchbase"
            }
        
        try:
            base_url = "https://api.crunchbase.com/v4/searches/organizations"
            headers = {
                "X-cb-user-key": api_key
            }
            params = {
                "name": company_name,
                "limit": 10
            }
            
            result = self.data_collection.collect_from_api(
                source="crunchbase",
                endpoint=base_url,
                params=params,
                headers=headers,
                use_cache=True
            )
            
            if result.get("success"):
                data = result.get("data", {})
                entities = data.get("entities", [])
                
                if entities:
                    # Return the first match
                    company_data = entities[0].get("properties", {})
                    return {
                        "success": True,
                        "source": "crunchbase",
                        "data": {
                            "name": company_data.get("name"),
                            "permalink": company_data.get("permalink"),
                            "website": company_data.get("website"),
                            "description": company_data.get("short_description"),
                            "founded_on": company_data.get("founded_on"),
                            "closed_on": company_data.get("closed_on"),
                            "num_employees": company_data.get("num_employees_enum"),
                            "total_funding": company_data.get("total_funding_usd"),
                            "categories": company_data.get("categories", []),
                            "locations": company_data.get("locations", []),
                            "crunchbase_url": f"https://www.crunchbase.com/organization/{company_data.get('permalink')}"
                        },
                        "match_count": len(entities),
                        "collected_at": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": "No companies found",
                        "source": "crunchbase"
                    }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Crunchbase search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "crunchbase"
            }
    
    def search_google_business(
        self,
        company_name: str,
        location: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search Google Business Profile (formerly Google My Business) API
        
        Requires Google Places API key from https://console.cloud.google.com/
        
        Args:
            company_name: Company name to search
            location: Location hint (city, state, country)
            api_key: Google Places API key (optional, can be set in config)
        
        Returns:
            Dictionary with company data from Google Business
        """
        api_key = api_key or getattr(settings, 'GOOGLE_PLACES_API_KEY', None)
        
        if not api_key:
            logger.warning("Google Places API key not configured")
            return {
                "success": False,
                "error": "API key not configured",
                "source": "google_business"
            }
        
        try:
            base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": company_name,
                "key": api_key,
                "type": "establishment"
            }
            
            if location:
                params["location"] = location
            
            result = self.data_collection.collect_from_api(
                source="google_business",
                endpoint=base_url,
                params=params,
                use_cache=True
            )
            
            if result.get("success"):
                data = result.get("data", {})
                places = data.get("results", [])
                
                if places:
                    # Return the first match
                    place = places[0]
                    return {
                        "success": True,
                        "source": "google_business",
                        "data": {
                            "name": place.get("name"),
                            "formatted_address": place.get("formatted_address"),
                            "place_id": place.get("place_id"),
                            "rating": place.get("rating"),
                            "user_ratings_total": place.get("user_ratings_total"),
                            "types": place.get("types", []),
                            "website": place.get("website"),
                            "phone_number": place.get("formatted_phone_number"),
                            "opening_hours": place.get("opening_hours"),
                            "geometry": place.get("geometry"),
                            "google_maps_url": f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id')}"
                        },
                        "match_count": len(places),
                        "collected_at": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": "No businesses found",
                        "source": "google_business"
                    }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Google Business search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "google_business"
            }
    
    def search_yelp(
        self,
        company_name: str,
        location: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search Yelp Business API
        
        Requires Yelp Fusion API key from https://www.yelp.com/developers
        
        Args:
            company_name: Company name to search
            location: Location (city, state, or address)
            api_key: Yelp API key (optional, can be set in config)
        
        Returns:
            Dictionary with company data from Yelp
        """
        api_key = api_key or getattr(settings, 'YELP_API_KEY', None)
        
        if not api_key:
            logger.warning("Yelp API key not configured")
            return {
                "success": False,
                "error": "API key not configured",
                "source": "yelp"
            }
        
        try:
            base_url = "https://api.yelp.com/v3/businesses/search"
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            params = {
                "term": company_name,
                "limit": 10
            }
            
            if location:
                params["location"] = location
            
            result = self.data_collection.collect_from_api(
                source="yelp",
                endpoint=base_url,
                params=params,
                headers=headers,
                use_cache=True
            )
            
            if result.get("success"):
                data = result.get("data", {})
                businesses = data.get("businesses", [])
                
                if businesses:
                    # Return the first match
                    business = businesses[0]
                    return {
                        "success": True,
                        "source": "yelp",
                        "data": {
                            "name": business.get("name"),
                            "id": business.get("id"),
                            "alias": business.get("alias"),
                            "rating": business.get("rating"),
                            "review_count": business.get("review_count"),
                            "price": business.get("price"),
                            "phone": business.get("phone"),
                            "display_phone": business.get("display_phone"),
                            "location": business.get("location", {}),
                            "coordinates": business.get("coordinates", {}),
                            "categories": business.get("categories", []),
                            "url": business.get("url"),
                            "image_url": business.get("image_url"),
                            "is_closed": business.get("is_closed")
                        },
                        "match_count": len(businesses),
                        "collected_at": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": "No businesses found",
                        "source": "yelp"
                    }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Yelp search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "yelp"
            }
    
    def search_all_directories(
        self,
        company_name: str,
        jurisdiction: Optional[str] = None,
        registration_number: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search all available business directories and aggregate results
        
        Args:
            company_name: Company name to search
            jurisdiction: Jurisdiction code (for OpenCorporates)
            registration_number: Registration number (for OpenCorporates)
            location: Location hint (for Google Business and Yelp)
        
        Returns:
            Dictionary with aggregated results from all directories
        """
        results = []
        
        # OpenCorporates (free, no API key required)
        opencorp_result = self.search_opencorporates(
            company_name=company_name,
            jurisdiction=jurisdiction,
            registration_number=registration_number
        )
        results.append(opencorp_result)
        
        # Crunchbase (requires API key)
        if hasattr(settings, 'CRUNCHBASE_API_KEY') and settings.CRUNCHBASE_API_KEY:
            crunchbase_result = self.search_crunchbase(company_name=company_name)
            results.append(crunchbase_result)
        
        # Google Business (requires API key)
        if hasattr(settings, 'GOOGLE_PLACES_API_KEY') and settings.GOOGLE_PLACES_API_KEY:
            google_result = self.search_google_business(
                company_name=company_name,
                location=location
            )
            results.append(google_result)
        
        # Yelp (requires API key)
        if hasattr(settings, 'YELP_API_KEY') and settings.YELP_API_KEY:
            yelp_result = self.search_yelp(
                company_name=company_name,
                location=location
            )
            results.append(yelp_result)
        
        # Aggregate results
        successful_results = [r for r in results if r.get("success")]
        failed_results = [r for r in results if not r.get("success")]
        
        # Merge data from all successful sources
        aggregated_data = {}
        for result in successful_results:
            source = result.get("source")
            data = result.get("data", {})
            aggregated_data[source] = data
        
        return {
            "success": len(successful_results) > 0,
            "results": results,
            "aggregated_data": aggregated_data,
            "successful_sources": [r["source"] for r in successful_results],
            "failed_sources": [r["source"] for r in failed_results],
            "total_sources": len(results),
            "collected_at": datetime.utcnow().isoformat()
        }

