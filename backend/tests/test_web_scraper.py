"""Tests for web scraper service"""

import pytest
from app.services.web_scraper import WebScraper


class TestWebScraper:
    """Test WebScraper"""
    
    def test_check_robots_txt(self):
        """Test checking robots.txt"""
        scraper = WebScraper()
        result = scraper.check_robots_txt("https://example.com")
        
        # Should return boolean or None
        assert result is None or isinstance(result, bool)
    
    def test_scrape_page(self):
        """Test scraping a page"""
        scraper = WebScraper()
        result = scraper.scrape_page("https://example.com", check_robots=False)
        
        assert isinstance(result, dict)
        # May fail if website not accessible, but should return dict
    
    def test_extract_company_data(self):
        """Test extracting company data from HTML"""
        scraper = WebScraper()
        
        html = """
        <html>
            <head>
                <title>Test Company</title>
                <script type="application/ld+json">
                {"@type": "Organization", "name": "Test Company"}
                </script>
            </head>
            <body>
                <h1>Test Company</h1>
                <p>Contact: test@example.com</p>
            </body>
        </html>
        """
        
        data = scraper.extract_company_data(html, "https://example.com")
        assert isinstance(data, dict)

