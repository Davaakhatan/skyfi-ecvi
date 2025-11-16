"""Web scraping tools with legal compliance and rate limiting"""

from typing import Dict, List, Optional, Any
import logging
import time
import json
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup

from app.core.config import settings

logger = logging.getLogger(__name__)


class WebScraper:
    """Web scraper with legal compliance, rate limiting, and respectful crawling"""
    
    def __init__(self):
        self.rate_limit_delay = 1.0  # Seconds between requests
        self.last_request_time = 0
        self.user_agent = "ECVI-Bot/1.0 (Company Verification Service)"
        self.timeout = 30.0
        self.max_redirects = 5
    
    def _check_rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _check_robots_txt(self, base_url: str) -> bool:
        """
        Check robots.txt for crawling permissions
        
        Args:
            base_url: Base URL of the website
        
        Returns:
            True if crawling is allowed, False otherwise
        """
        try:
            robots_url = urljoin(base_url, "/robots.txt")
            with httpx.Client(timeout=10.0) as client:
                response = client.get(robots_url, headers={"User-Agent": self.user_agent})
                if response.status_code == 200:
                    # TODO: Parse robots.txt properly (use robotparser library)
                    # For now, check for common disallow patterns
                    content = response.text.lower()
                    if "disallow: /" in content:
                        logger.warning(f"robots.txt disallows crawling for {base_url}")
                        return False
            return True
        except Exception as e:
            logger.warning(f"Could not check robots.txt for {base_url}: {e}")
            # Default to allowing if we can't check
            return True
    
    def scrape_page(
        self,
        url: str,
        check_robots: bool = True,
        extract_text: bool = True,
        extract_links: bool = False
    ) -> Dict[str, Any]:
        """
        Scrape a single web page with legal compliance
        
        Args:
            url: URL to scrape
            check_robots: Whether to check robots.txt first
            extract_text: Whether to extract text content
            extract_links: Whether to extract links
        
        Returns:
            Dictionary with scraped content
        """
        # Check rate limit
        self._check_rate_limit()
        
        # Check robots.txt if requested
        if check_robots:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            if not self._check_robots_txt(base_url):
                return {
                    "success": False,
                    "error": "robots.txt disallows crawling",
                    "url": url
                }
        
        try:
            with httpx.Client(
                timeout=self.timeout,
                follow_redirects=True,
                max_redirects=self.max_redirects,
                headers={"User-Agent": self.user_agent}
            ) as client:
                response = client.get(url)
                response.raise_for_status()
                
                result = {
                    "success": True,
                    "url": url,
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type", ""),
                    "scraped_at": time.time()
                }
                
                # Parse HTML if content is HTML
                if "text/html" in response.headers.get("content-type", ""):
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    if extract_text:
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Get text content
                        text = soup.get_text()
                        # Clean up whitespace
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        text = " ".join(chunk for chunk in chunks if chunk)
                        
                        result["text_content"] = text
                        result["title"] = soup.title.string if soup.title else None
                    
                    if extract_links:
                        links = []
                        for link in soup.find_all("a", href=True):
                            absolute_url = urljoin(url, link["href"])
                            links.append({
                                "url": absolute_url,
                                "text": link.get_text(strip=True)
                            })
                        result["links"] = links
                
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error scraping {url}: {e}")
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}",
                "url": url
            }
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    def search_company_info(
        self,
        company_name: str,
        domain: Optional[str] = None,
        search_engines: List[str] = None
    ) -> Dict[str, Any]:
        """
        Search for company information across multiple sources
        
        Args:
            company_name: Company name to search for
            domain: Optional company domain
            search_engines: List of search engine URLs to use
        
        Returns:
            Dictionary with search results
        """
        if search_engines is None:
            # Default to using web search APIs (not direct scraping of search engines)
            # TODO: Integrate with search APIs like SerpAPI, Google Custom Search
            logger.info(f"Searching for company: {company_name}")
            return {
                "success": False,
                "error": "Search engine integration not yet implemented. Use search APIs instead.",
                "company_name": company_name
            }
        
        results = []
        for engine in search_engines:
            # TODO: Implement search engine queries
            pass
        
        return {
            "success": True,
            "company_name": company_name,
            "results": results
        }
    
    def extract_company_data(self, html_content: str) -> Dict[str, Any]:
        """
        Extract structured company data from HTML content
        
        Args:
            html_content: HTML content to parse
        
        Returns:
            Dictionary with extracted company data
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Extract common company information patterns
            extracted_data = {
                "company_name": None,
                "address": None,
                "phone": None,
                "email": None,
                "website": None,
                "registration_number": None
            }
            
            # Look for structured data (JSON-LD, microdata, etc.)
            json_ld_scripts = soup.find_all("script", type="application/ld+json")
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get("@type") == "Organization":
                        extracted_data["company_name"] = data.get("name")
                        if "address" in data:
                            addr = data["address"]
                            if isinstance(addr, dict):
                                extracted_data["address"] = addr.get("streetAddress")
                        extracted_data["phone"] = data.get("telephone")
                        extracted_data["email"] = data.get("email")
                        extracted_data["website"] = data.get("url")
                except (json.JSONDecodeError, AttributeError):
                    pass
            
            # Extract from common HTML patterns
            # Company name (often in h1 or title)
            if not extracted_data["company_name"]:
                h1 = soup.find("h1")
                if h1:
                    extracted_data["company_name"] = h1.get_text(strip=True)
            
            # Phone numbers (common patterns)
            phone_patterns = soup.find_all(string=lambda text: text and any(
                char.isdigit() for char in text
            ))
            # TODO: Use regex to extract phone numbers properly
            
            # Email addresses
            email_links = soup.find_all("a", href=lambda x: x and x.startswith("mailto:"))
            if email_links:
                extracted_data["email"] = email_links[0]["href"].replace("mailto:", "")
            
            return {
                "success": True,
                "extracted_data": extracted_data
            }
            
        except Exception as e:
            logger.error(f"Error extracting company data: {e}")
            return {
                "success": False,
                "error": str(e)
            }

