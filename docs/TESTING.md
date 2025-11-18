# Testing Documentation

## Overview

The ECVI project includes comprehensive test coverage for both backend and frontend components. Tests are organized to ensure code quality, reliability, and maintainability.

## Backend Testing

### Test Framework
- **Framework:** pytest
- **Coverage Tool:** pytest-cov
- **Database:** In-memory SQLite for test isolation

### Test Structure
```
backend/tests/
├── conftest.py                    # Pytest configuration and fixtures
├── test_risk_calculator.py        # Risk calculation service tests
├── test_contact_verification.py  # Contact verification service tests
├── test_data_correction.py        # Data correction service tests
├── test_dns_verification.py      # DNS verification service tests
├── test_verification_service.py   # Main verification service tests
├── test_report_generator.py       # Report generation service tests
├── test_discrepancy_detection.py # Discrepancy detection service tests
├── test_confidence_scoring.py    # Confidence scoring service tests
├── test_registration_verification.py # Registration verification tests
├── test_risk_history.py           # Risk history service tests
├── test_report_sharing.py         # Report sharing service tests
├── test_validators.py             # Validation utility tests
├── test_api_auth.py               # Authentication API tests
├── test_api_companies.py          # Companies API tests
├── test_api_contact_verification.py # Contact verification API tests
└── test_api_data_corrections.py   # Data corrections API tests
```

### Running Backend Tests

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_risk_calculator.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_risk_calculator.py::TestRiskCalculator::test_calculate_overall_risk_low_risk
```

### Test Fixtures

Common fixtures available in `conftest.py`:
- `db_session` - Database session for testing
- `test_user` - Test user fixture (operator role)
- `test_admin_user` - Test admin user fixture
- `test_company` - Test company fixture
- `test_verification_result` - Test verification result fixture

### Test Coverage

**Services Tested:**
- ✅ Risk Calculator (comprehensive tests for all risk calculation methods)
- ✅ Contact Verification (email, phone, name verification)
- ✅ Data Correction (create, approve, reject, versioning)
- ✅ DNS Verification (domain validation, SSL checks)
- ✅ Verification Service (end-to-end verification flow)
- ✅ Report Generator (report generation and formatting)
- ✅ Discrepancy Detection (name, address, registration discrepancies)
- ✅ Confidence Scoring (source and field confidence)
- ✅ Registration Verification (format validation, cross-referencing)
- ✅ Risk History (storing and retrieving historical scores)
- ✅ Report Sharing (shareable links, access tracking)
- ✅ Validators (email, phone, domain, registration number validation)

**API Endpoints Tested:**
- ✅ Authentication (register, login, get current user)
- ✅ Companies (CRUD operations, filtering, pagination)
- ✅ Contact Verification (verify email/phone/name, get verifications)
- ✅ Data Corrections (create, approve, reject, get history)
- ✅ Reports (generate report, export formats, shareable links)
- ✅ Reviews (create, update, get, bulk operations)
- ✅ Risk Scoring (get risk score, history, trends)

## Frontend Testing

### Test Framework
- **Framework:** Vitest
- **Testing Library:** @testing-library/react
- **Environment:** jsdom

### Test Structure
```
frontend/src/
├── test/
│   ├── setup.ts                  # Vitest configuration
│   ├── utils/
│   │   └── test-utils.tsx         # Custom render function with providers
│   └── README.md                  # Frontend testing documentation
├── components/
│   └── __tests__/
│       ├── RiskScoreBadge.test.tsx
│       └── VerificationIndicator.test.tsx
├── store/
│   └── __tests__/
│       ├── authStore.test.ts
│       └── notificationStore.test.ts
└── utils/
    └── __tests__/
        └── validators.test.ts
```

### Running Frontend Tests

```bash
# Run all tests
cd frontend
npm test

# Run in watch mode
npm test -- --watch

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage
```

### Test Coverage

**Components Tested:**
- ✅ RiskScoreBadge (low, medium, high risk display)
- ✅ VerificationIndicator (verified, partial, discrepancy status)
- ✅ CreateCompanyModal (form validation, submission)
- ✅ ReviewModal (create/update reviews)
- ✅ NotificationCenter (display, mark as read, remove notifications)

**Stores Tested:**
- ✅ AuthStore (login, logout, authentication state)
- ✅ NotificationStore (add, mark as read, remove notifications)

**Utilities Tested:**
- ✅ Validators (email, phone validation)

## Test Statistics

### Backend
- **Total Test Files:** 25
- **Service Tests:** 18 files (RiskCalculator, ContactVerification, DataCorrection, DNSVerification, VerificationService, ReportGenerator, DiscrepancyDetection, ConfidenceScoring, RegistrationVerification, RiskHistory, ReportSharing, Validators, BusinessDirectory, DataCollection, TaskQueue, WebScraper, Exporters, Security)
- **API Integration Tests:** 7 files (Auth, Companies, ContactVerification, DataCorrections, Reports, Reviews, RiskScoring)
- **Test Fixtures:** 4 (test_user, test_admin_user, test_company, test_verification_result)

### Frontend
- **Total Test Files:** 8
- **Component Tests:** 5 files (RiskScoreBadge, VerificationIndicator, CreateCompanyModal, ReviewModal, NotificationCenter)
- **Store Tests:** 2 files (AuthStore, NotificationStore)
- **Utility Tests:** 1 file (Validators)

## Writing New Tests

### Backend Test Guidelines

1. **File Naming:** Use `test_*.py` convention
2. **Class Naming:** Use `Test*` convention for test classes
3. **Method Naming:** Use `test_*` convention for test methods
4. **Fixtures:** Use fixtures from `conftest.py` for common test data
5. **Isolation:** Each test should be independent and not rely on other tests
6. **Assertions:** Use descriptive assertions with clear error messages

Example:
```python
def test_create_company(db_session, test_user):
    """Test creating a company"""
    service = CompanyService(db_session)
    company = service.create_company(
        legal_name="Test Company",
        created_by=test_user.id
    )
    assert company.legal_name == "Test Company"
    assert company.id is not None
```

### Frontend Test Guidelines

1. **File Naming:** Use `*.test.tsx` or `*.test.ts` convention
2. **Location:** Place test files next to the component/module being tested
3. **Render:** Use custom `render` function from `test/utils/test-utils.tsx`
4. **Queries:** Use Testing Library queries (getByText, getByRole, etc.)
5. **User Events:** Use `@testing-library/user-event` for interactions

Example:
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '../../test/utils'
import MyComponent from '../MyComponent'

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
```

## Continuous Integration

Tests should be run automatically in CI/CD pipeline:
- On every pull request
- Before merging to main branch
- On scheduled basis (nightly builds)

## Coverage Goals

- **Backend:** Target 80%+ code coverage
- **Frontend:** Target 70%+ code coverage
- **Critical Paths:** 100% coverage for authentication, payment, and data processing

## Security Tests

Security tests are located in:
- `test_security.py` - Security utility function tests (password hashing, token creation, password strength validation)
- `test_security_audit.py` - Comprehensive security audit tests (authentication, input validation, API security, data security, CORS)

### Running Security Tests

```bash
cd backend
pytest tests/test_security.py tests/test_security_audit.py -v
```

## Performance Tests

Performance tests are located in:
- `test_performance.py` - API endpoint performance tests, database query performance, caching tests, benchmarks

### Running Performance Tests

```bash
cd backend
pytest tests/test_performance.py -v
pytest tests/test_performance.py --benchmark-only  # For benchmarks
```

## Future Test Enhancements

- [ ] E2E tests with Playwright/Cypress
- [ ] AI/ML service integration tests (with LLM mocking)
- [ ] Visual regression tests
- [ ] Accessibility tests
- [ ] Penetration testing (external security firm)
- [ ] Automated vulnerability scanning

