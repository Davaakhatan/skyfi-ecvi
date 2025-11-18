# CI/CD Pipeline Documentation

## Overview

The ECVI project uses GitHub Actions for continuous integration and continuous deployment. The CI/CD pipeline ensures code quality, runs automated tests, and verifies builds before deployment.

## Pipeline Structure

### Workflow File

The main CI/CD workflow is defined in `.github/workflows/ci.yml` and runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### Jobs

The pipeline consists of three main jobs:

#### 1. Backend Tests (`backend-tests`)

**Services:**
- PostgreSQL 15 (test database)
- Redis 7 (for caching and Celery)

**Steps:**
1. Checkout code
2. Set up Python 3.11 with pip caching
3. Install backend dependencies (`pip install -e ".[dev]"`)
4. Run linting (ruff, black, mypy) - non-blocking
5. Run pytest with coverage reporting
6. Upload coverage reports to Codecov

**Environment Variables:**
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: Test secret key (minimum 32 characters)
- `CORS_ORIGINS`: Allowed CORS origins
- `ENVIRONMENT`: Set to `test`

**Coverage:**
- Generates XML and HTML coverage reports
- Uploads to Codecov for tracking

#### 2. Frontend Tests (`frontend-tests`)

**Steps:**
1. Checkout code
2. Set up Node.js 20 with npm caching
3. Install frontend dependencies (`npm ci`)
4. Run ESLint - non-blocking
5. Run Vitest with coverage
6. Upload coverage reports to Codecov
7. Build frontend application

**Coverage:**
- Generates coverage reports
- Uploads to Codecov for tracking

#### 3. Build Verification (`build-verification`)

**Dependencies:**
- Requires both `backend-tests` and `frontend-tests` to pass

**Steps:**
1. Checkout code
2. Set up Python 3.11 and Node.js 20
3. Install all dependencies
4. Verify backend imports
5. Build frontend application
6. Verify build artifacts exist

**Purpose:**
- Ensures the application can be built successfully
- Verifies all dependencies are correctly configured
- Confirms build artifacts are generated

## Running Tests Locally

### Backend Tests

```bash
cd backend
pip install -e ".[dev]"
pytest tests/ -v --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm install
npm run test
```

### With Coverage

```bash
# Backend
cd backend
pytest --cov=app --cov-report=html

# Frontend
cd frontend
npm run test:coverage
```

## Code Quality Checks

### Backend

- **Ruff**: Fast Python linter
- **Black**: Code formatter
- **MyPy**: Static type checker

```bash
cd backend
ruff check app/
black --check app/
mypy app/
```

### Frontend

- **ESLint**: JavaScript/TypeScript linter

```bash
cd frontend
npm run lint
```

## Coverage Goals

- **Backend**: Target 80%+ code coverage
- **Frontend**: Target 70%+ code coverage
- **Critical Paths**: 100% coverage for authentication, data processing, and security

## Continuous Integration Benefits

1. **Early Detection**: Catches bugs and issues before they reach production
2. **Code Quality**: Ensures consistent code style and quality
3. **Test Coverage**: Tracks and maintains test coverage over time
4. **Build Verification**: Confirms the application builds successfully
5. **Automated Testing**: Runs all tests on every push and pull request

## Future Enhancements

- [ ] Add deployment workflows for staging and production
- [ ] Add security scanning (SAST/DAST)
- [ ] Add dependency vulnerability scanning
- [ ] Add performance testing in CI
- [ ] Add E2E tests with Playwright/Cypress
- [ ] Add Docker image building and publishing
- [ ] Add automated database migration testing

## Troubleshooting

### Backend Tests Failing

1. Check database connection (PostgreSQL service)
2. Verify Redis is running
3. Check environment variables are set correctly
4. Ensure all dependencies are installed

### Frontend Tests Failing

1. Verify Node.js version (20+)
2. Clear `node_modules` and reinstall: `rm -rf node_modules && npm ci`
3. Check for TypeScript errors: `npm run build`

### Build Verification Failing

1. Check import errors in backend
2. Verify frontend build completes successfully
3. Check for missing dependencies

## Best Practices

1. **Run tests locally** before pushing
2. **Fix linting issues** before committing
3. **Write tests** for new features
4. **Maintain coverage** above target thresholds
5. **Review CI results** before merging PRs

