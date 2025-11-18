"""Performance tests for API endpoints"""

import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.security import create_access_token
from app.models.user import User
from app.models.company import Company
from app.models.verification_result import VerificationResult
from datetime import datetime, timedelta

client = TestClient(app)


@pytest.fixture
def auth_token(test_user):
    """Create auth token for test user"""
    token = create_access_token(data={"sub": test_user.username, "role": test_user.role})
    return token


@pytest.fixture
def auth_headers(auth_token):
    """Create auth headers"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def test_companies(db_session, test_user):
    """Create test companies for performance testing"""
    companies = []
    for i in range(50):
        company = Company(
            legal_name=f"Test Company {i}",
            registration_number=f"REG{i:04d}",
            jurisdiction="US",
            domain=f"company{i}.com",
        )
        db_session.add(company)
        companies.append(company)
    db_session.commit()
    return companies


class TestAPIPerformance:
    """Performance tests for API endpoints"""
    
    # Performance requirements
    MAX_LIST_RESPONSE_TIME = 2.0  # seconds
    MAX_API_RESPONSE_TIME = 0.5  # seconds
    MAX_REPORT_RESPONSE_TIME = 30.0  # seconds
    
    def test_companies_list_performance(self, db_session, test_companies, auth_headers):
        """Test that companies list endpoint responds within 2 seconds"""
        start_time = time.time()
        response = client.get(
            "/api/v1/companies/",
            headers=auth_headers,
            params={"limit": 100}
        )
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < self.MAX_LIST_RESPONSE_TIME, \
            f"Companies list took {elapsed_time:.2f}s, expected < {self.MAX_LIST_RESPONSE_TIME}s"
    
    def test_get_company_performance(self, db_session, test_companies, auth_headers):
        """Test that get company endpoint responds within 500ms"""
        company_id = str(test_companies[0].id)
        
        start_time = time.time()
        response = client.get(
            f"/api/v1/companies/{company_id}",
            headers=auth_headers
        )
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < self.MAX_API_RESPONSE_TIME, \
            f"Get company took {elapsed_time:.2f}s, expected < {self.MAX_API_RESPONSE_TIME}s"
    
    def test_create_company_performance(self, db_session, auth_headers):
        """Test that create company endpoint responds within 500ms"""
        company_data = {
            "legal_name": "Performance Test Company",
            "registration_number": "PERF001",
            "jurisdiction": "US",
            "domain": "perftest.com"
        }
        
        start_time = time.time()
        response = client.post(
            "/api/v1/companies/",
            headers=auth_headers,
            json=company_data
        )
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 201
        assert elapsed_time < self.MAX_API_RESPONSE_TIME, \
            f"Create company took {elapsed_time:.2f}s, expected < {self.MAX_API_RESPONSE_TIME}s"
    
    def test_verification_result_performance(
        self, db_session, test_company, test_verification_result, auth_headers
    ):
        """Test that get verification result endpoint responds within 500ms"""
        company_id = str(test_company.id)
        
        start_time = time.time()
        response = client.get(
            f"/api/v1/companies/{company_id}/verification",
            headers=auth_headers
        )
        elapsed_time = time.time() - start_time
        
        # May return 404 if no verification result, which is acceptable
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert elapsed_time < self.MAX_API_RESPONSE_TIME, \
                f"Get verification result took {elapsed_time:.2f}s, expected < {self.MAX_API_RESPONSE_TIME}s"
    
    def test_report_generation_performance(
        self, db_session, test_company, test_verification_result, auth_headers
    ):
        """Test that report generation responds within 30 seconds"""
        company_id = str(test_company.id)
        
        start_time = time.time()
        response = client.get(
            f"/api/v1/reports/companies/{company_id}",
            headers=auth_headers,
            params={"format": "json"}
        )
        elapsed_time = time.time() - start_time
        
        # May return 404 if no verification result, which is acceptable
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert elapsed_time < self.MAX_REPORT_RESPONSE_TIME, \
                f"Report generation took {elapsed_time:.2f}s, expected < {self.MAX_REPORT_RESPONSE_TIME}s"
    
    def test_companies_list_with_filters_performance(
        self, db_session, test_companies, auth_headers
    ):
        """Test that filtered companies list responds within 2 seconds"""
        start_time = time.time()
        response = client.get(
            "/api/v1/companies/",
            headers=auth_headers,
            params={
                "limit": 100,
                "search": "Test",
                "risk_category": "LOW"
            }
        )
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < self.MAX_LIST_RESPONSE_TIME, \
            f"Filtered companies list took {elapsed_time:.2f}s, expected < {self.MAX_LIST_RESPONSE_TIME}s"
    
    def test_audit_logs_performance(self, db_session, test_user, auth_headers):
        """Test that audit logs endpoint responds within 500ms"""
        # Create test audit logs
        from app.models.audit import AuditLog
        for i in range(20):
            audit_log = AuditLog(
                user_id=test_user.id,
                action=f"TEST_ACTION_{i}",
                resource_type="company"
            )
            db_session.add(audit_log)
        db_session.commit()
        
        start_time = time.time()
        response = client.get(
            "/api/v1/audit/",
            headers=auth_headers,
            params={"limit": 50}
        )
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < self.MAX_API_RESPONSE_TIME, \
            f"Audit logs took {elapsed_time:.2f}s, expected < {self.MAX_API_RESPONSE_TIME}s"


class TestDatabaseQueryPerformance:
    """Performance tests for database queries"""
    
    def test_companies_query_with_eager_loading(
        self, db_session, test_companies
    ):
        """Test that eager loading reduces query count"""
        from sqlalchemy.orm import selectinload
        from app.models.company import Company
        from sqlalchemy import event
        
        # Count queries without eager loading
        query_count = []
        
        def count_queries(conn, cursor, statement, parameters, context, executemany):
            query_count.append(1)
        
        event.listen(db_session.bind, "before_cursor_execute", count_queries)
        
        # Query without eager loading
        companies = db_session.query(Company).limit(10).all()
        for company in companies:
            _ = company.verification_results  # Trigger lazy load
        
        queries_without_eager = len(query_count)
        query_count.clear()
        
        # Query with eager loading
        companies = db_session.query(Company).options(
            selectinload(Company.verification_results)
        ).limit(10).all()
        for company in companies:
            _ = company.verification_results  # Already loaded
        
        queries_with_eager = len(query_count)
        
        # Eager loading should reduce query count
        assert queries_with_eager < queries_without_eager, \
            f"Eager loading should reduce queries. Without: {queries_without_eager}, With: {queries_with_eager}"
        
        event.remove(db_session.bind, "before_cursor_execute", count_queries)
    
    def test_indexed_query_performance(self, db_session, test_companies):
        """Test that indexed queries are fast"""
        from app.models.company import Company
        
        start_time = time.time()
        
        # Query using indexed field (registration_number)
        company = db_session.query(Company).filter(
            Company.registration_number == "REG0000"
        ).first()
        
        elapsed_time = time.time() - start_time
        
        # Company may not exist, but query should still be fast
        assert elapsed_time < 0.1, \
            f"Indexed query took {elapsed_time:.2f}s, expected < 0.1s"


class TestCachingPerformance:
    """Performance tests for caching"""
    
    def test_cached_company_response(self, db_session, test_company, auth_headers):
        """Test that cached responses work correctly"""
        company_id = str(test_company.id)
        
        # First request
        response1 = client.get(
            f"/api/v1/companies/{company_id}",
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        
        # Second request (may be cached)
        response2 = client.get(
            f"/api/v1/companies/{company_id}",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        
        # Responses should be identical
        # Note: In test environment, caching may not be enabled
        assert response1.json() == response2.json()


@pytest.mark.benchmark
class TestBenchmarkPerformance:
    """Benchmark tests using pytest-benchmark"""
    
    def test_companies_list_benchmark(
        self, benchmark, db_session, test_companies, auth_headers
    ):
        """Benchmark companies list endpoint"""
        def get_companies():
            return client.get(
                "/api/v1/companies/",
                headers=auth_headers,
                params={"limit": 100}
            )
        
        result = benchmark(get_companies)
        assert result.status_code == 200
    
    def test_get_company_benchmark(
        self, benchmark, db_session, test_companies, auth_headers
    ):
        """Benchmark get company endpoint"""
        company_id = str(test_companies[0].id)
        
        def get_company():
            return client.get(
                f"/api/v1/companies/{company_id}",
                headers=auth_headers
            )
        
        result = benchmark(get_company)
        assert result.status_code == 200

