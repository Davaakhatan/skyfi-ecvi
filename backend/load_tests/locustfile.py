"""
Load testing with Locust

Run with:
    locust -f load_tests/locustfile.py --host=http://localhost:8000

Access Locust web UI at: http://localhost:8089
"""

from locust import HttpUser, task, between
import random
import string


class ECVIUser(HttpUser):
    """Simulated user for load testing"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Login and get auth token"""
        # Register/login (simplified - in real scenario, use actual auth)
        self.token = None
        # For load testing, we'll use a pre-created token or skip auth
        # In production, create test users and authenticate properly
        self.headers = {}
        if self.token:
            self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def get_companies_list(self):
        """Get list of companies (most common operation)"""
        self.client.get(
            "/api/v1/companies/",
            headers=self.headers,
            params={"limit": 50, "skip": 0}
        )
    
    @task(2)
    def get_company_detail(self):
        """Get company details"""
        # Use a random company ID (in real scenario, fetch from list first)
        company_id = "00000000-0000-0000-0000-000000000001"
        self.client.get(
            f"/api/v1/companies/{company_id}",
            headers=self.headers
        )
    
    @task(1)
    def get_verification_result(self):
        """Get verification result for a company"""
        company_id = "00000000-0000-0000-0000-000000000001"
        self.client.get(
            f"/api/v1/companies/{company_id}/verification",
            headers=self.headers
        )
    
    @task(1)
    def get_report(self):
        """Get verification report"""
        company_id = "00000000-0000-0000-0000-000000000001"
        self.client.get(
            f"/api/v1/reports/companies/{company_id}",
            headers=self.headers,
            params={"format": "json"}
        )
    
    @task(1)
    def search_companies(self):
        """Search companies"""
        search_terms = ["test", "company", "inc", "ltd", "corp"]
        search_term = random.choice(search_terms)
        self.client.get(
            "/api/v1/companies/",
            headers=self.headers,
            params={"search": search_term, "limit": 20}
        )
    
    @task(1)
    def get_audit_logs(self):
        """Get audit logs (admin only)"""
        self.client.get(
            "/api/v1/audit/",
            headers=self.headers,
            params={"limit": 50}
        )


class HighLoadUser(HttpUser):
    """High-load user for stress testing"""
    
    wait_time = between(0.1, 0.5)  # Very short wait time
    
    @task
    def rapid_requests(self):
        """Rapid fire requests"""
        self.client.get(
            "/api/v1/companies/",
            params={"limit": 10}
        )

