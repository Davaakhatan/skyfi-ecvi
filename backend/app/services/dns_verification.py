"""DNS verification service"""

from typing import Dict, Optional, Tuple
import dns.resolver
import dns.exception
from datetime import datetime
import whois
import socket


class DNSVerificationService:
    """Service for DNS and domain verification"""
    
    @staticmethod
    def verify_dns_records(domain: str) -> Dict:
        """
        Verify DNS records for a domain
        
        Args:
            domain: Domain name to verify
        
        Returns:
            Dictionary with verification results
        """
        results = {
            "domain": domain,
            "a_record_exists": False,
            "mx_record_exists": False,
            "ns_records": [],
            "verified": False,
            "errors": []
        }
        
        try:
            # Check A record
            try:
                a_records = dns.resolver.resolve(domain, "A")
                results["a_record_exists"] = True
                results["a_records"] = [str(r) for r in a_records]
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                results["errors"].append("No A record found")
            except Exception as e:
                results["errors"].append(f"A record check failed: {str(e)}")
            
            # Check MX record
            try:
                mx_records = dns.resolver.resolve(domain, "MX")
                results["mx_record_exists"] = True
                results["mx_records"] = [str(r) for r in mx_records]
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                pass  # MX records are optional
            except Exception as e:
                results["errors"].append(f"MX record check failed: {str(e)}")
            
            # Check NS records
            try:
                ns_records = dns.resolver.resolve(domain, "NS")
                results["ns_records"] = [str(r) for r in ns_records]
            except Exception as e:
                results["errors"].append(f"NS record check failed: {str(e)}")
            
            # Overall verification: domain exists and has A record
            results["verified"] = results["a_record_exists"]
            
        except dns.resolver.NXDOMAIN:
            results["errors"].append("Domain does not exist")
        except Exception as e:
            results["errors"].append(f"DNS verification failed: {str(e)}")
        
        return results
    
    @staticmethod
    def get_domain_age(domain: str) -> Optional[int]:
        """
        Get domain age in days
        
        Args:
            domain: Domain name
        
        Returns:
            Age in days or None if unable to determine
        """
        try:
            w = whois.whois(domain)
            if w.creation_date:
                if isinstance(w.creation_date, list):
                    creation_date = w.creation_date[0]
                else:
                    creation_date = w.creation_date
                
                if isinstance(creation_date, datetime):
                    age_days = (datetime.now() - creation_date).days
                    return age_days
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def check_ssl_certificate(domain: str) -> Optional[bool]:
        """
        Check if domain has valid SSL certificate
        
        Args:
            domain: Domain name
        
        Returns:
            True if valid SSL, False if invalid, None if unable to check
        """
        try:
            import ssl
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    return True
        except Exception:
            return False
    
    @staticmethod
    def verify_domain_matches_company(domain: str, company_name: str) -> bool:
        """
        Check if domain name matches company name
        
        Args:
            domain: Domain name
            company_name: Company legal name
        
        Returns:
            True if domain appears to match company name
        """
        # Remove common TLD and www
        domain_clean = domain.replace("www.", "").split(".")[0].lower()
        
        # Clean company name
        company_clean = company_name.lower()
        # Remove common words
        for word in ["inc", "llc", "ltd", "corp", "corporation", "company", "co"]:
            company_clean = company_clean.replace(word, "").strip()
        
        # Check if domain contains company name or vice versa
        company_words = company_clean.split()
        domain_words = domain_clean.replace("-", " ").split()
        
        # Check for word matches
        matches = sum(1 for word in company_words if word in domain_clean)
        if matches >= len(company_words) * 0.5:  # At least 50% match
            return True
        
        # Check if company name contains domain
        if domain_clean in company_clean:
            return True
        
        return False

