# Backend Tests

This directory contains all backend test files for the ECVI project.

## Test Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_*.py` - Individual test files for each module

## Running Tests

### Run all tests
```bash
cd backend
pytest
```

### Run specific test file
```bash
pytest tests/test_risk_calculator.py
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run with verbose output
```bash
pytest -v
```

## Test Files

### Service Tests
- `test_risk_calculator.py` - Risk calculation service tests
- `test_contact_verification.py` - Contact verification service tests
- `test_data_correction.py` - Data correction service tests
- `test_dns_verification.py` - DNS verification service tests
- `test_verification_service.py` - Main verification service tests
- `test_report_generator.py` - Report generation service tests
- `test_discrepancy_detection.py` - Discrepancy detection service tests
- `test_confidence_scoring.py` - Confidence scoring service tests
- `test_registration_verification.py` - Registration verification service tests
- `test_risk_history.py` - Risk history service tests
- `test_report_sharing.py` - Report sharing service tests
- `test_validators.py` - Validation utility tests

### API Tests
- `test_api_auth.py` - Authentication API endpoint tests
- `test_api_companies.py` - Companies API endpoint tests
- `test_api_contact_verification.py` - Contact verification API endpoint tests
- `test_api_data_corrections.py` - Data corrections API endpoint tests

## Test Fixtures

Common fixtures available in `conftest.py`:
- `db_session` - Database session for testing
- `test_user` - Test user fixture
- `test_admin_user` - Test admin user fixture
- `test_company` - Test company fixture
- `test_verification_result` - Test verification result fixture

## Writing New Tests

1. Create a new test file following the naming convention `test_*.py`
2. Import necessary fixtures from `conftest.py`
3. Use descriptive test class and method names
4. Follow the existing test patterns
5. Ensure tests are isolated and don't depend on each other

## Test Database

Tests use an in-memory SQLite database that is created and destroyed for each test, ensuring test isolation.

