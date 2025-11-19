# Enterprise Company Verification Intelligence (ECVI)

**AI-driven company verification system for Enterprise account registration**

[![CI/CD](https://github.com/Davaakhatan/skyfi-ecvi/actions/workflows/ci.yml/badge.svg)](https://github.com/Davaakhatan/skyfi-ecvi/actions/workflows/ci.yml)

## Overview

ECVI is a cloud-agnostic, microservices-based platform that leverages AI and Agentic Systems to automatically verify business entities during Enterprise account registration. The system replaces manual review processes with AI-powered verification, reducing fraud and improving compliance.

### Key Features

- 🤖 **AI-Powered Verification** - Automated data collection and verification using LangChain and Agentic Systems
- 📊 **Risk Scoring** - Comprehensive risk assessment (0-100 scale) with detailed breakdowns
- 📄 **Verification Reports** - Detailed reports with export capabilities (JSON, CSV, PDF, HTML)
- 🔒 **Security & Compliance** - GDPR compliant with comprehensive audit logging
- ⚡ **High Performance** - Optimized for < 500ms API responses, < 2s list views
- 🎨 **Modern UI** - Minimalist, responsive frontend built with React and TypeScript

## Architecture

- **Backend:** FastAPI (Python 3.11+)
- **Frontend:** React 18 + TypeScript + Vite
- **Database:** PostgreSQL 15+
- **Cache:** Redis 7+
- **Task Queue:** Celery
- **AI Framework:** LangChain with OpenAI/Anthropic
- **Deployment:** Docker + Kubernetes (cloud-agnostic)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API documentation available at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend available at: http://localhost:5173

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test

# Performance tests
cd backend
pytest tests/test_performance.py --benchmark-only

# Load tests
cd backend
locust -f load_tests/locustfile.py --host=http://localhost:8000
```

## Project Structure

```
.
├── backend/              # FastAPI backend application
│   ├── app/
│   │   ├── api/v1/      # API endpoints
│   │   ├── core/        # Core functionality (config, auth, security)
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   ├── tasks/       # Celery tasks
│   │   └── utils/       # Utility functions
│   ├── tests/           # Backend tests
│   ├── load_tests/      # Load testing scripts
│   └── pyproject.toml   # Python dependencies
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   └── store/      # State management
│   └── package.json     # Node.js dependencies
├── docs/                # Project documentation
│   ├── PRD.md          # Product Requirements Document
│   ├── ARCHITECTURE.md # System Architecture
│   ├── TESTING.md      # Testing documentation
│   └── ...
├── memory-bank/         # Project knowledge base
│   ├── project-status.md
│   ├── decisions.md
│   └── ...
└── tasks/               # Task tracking
    └── tasks-PRD.md    # Implementation tasks
```

## Documentation

### Core Documentation

- **[Product Requirements Document (PRD)](docs/PRD.md)** - Complete product requirements
- **[System Architecture](docs/ARCHITECTURE.md)** - Technical architecture and design
- **[Testing Guide](docs/TESTING.md)** - Testing strategy and procedures
- **[Performance Optimization](docs/PERFORMANCE_OPTIMIZATION.md)** - Performance optimizations
- **[Performance Testing](docs/PERFORMANCE_TESTING.md)** - Performance testing guide
- **[Security Audit](docs/SECURITY_AUDIT.md)** - Security measures and audit results
- **[CI/CD Pipeline](docs/CI_CD.md)** - Continuous integration and deployment
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Monitoring Guide](docs/MONITORING.md)** - Monitoring and observability setup
- **[Runbooks](docs/RUNBOOKS.md)** - Operational procedures and troubleshooting
- **[Operator Training](docs/OPERATOR_TRAINING.md)** - Comprehensive operator training guide
- **[Operator Quick Reference](docs/OPERATOR_QUICK_REFERENCE.md)** - Quick reference for operators
- **[Operator Troubleshooting](docs/OPERATOR_TROUBLESHOOTING.md)** - Troubleshooting guide for operators
- **[Production Readiness Checklist](docs/PRODUCTION_READINESS_CHECKLIST.md)** - Pre-deployment checklist
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Complete project overview and status

### Memory Bank

- **[Project Status](memory-bank/project-status.md)** - Current project status and progress
- **[Decisions](memory-bank/decisions.md)** - Important architectural and product decisions
- **[Context](memory-bank/context.md)** - Project background and requirements
- **[Learnings](memory-bank/learnings.md)** - Lessons learned and best practices

## Features

### Core Functionality

- ✅ **Company Verification** - Automated verification with AI-powered data collection
- ✅ **Risk Scoring** - Comprehensive risk assessment with historical tracking
- ✅ **Verification Reports** - Detailed reports with multiple export formats
- ✅ **Manual Review** - Mark companies as reviewed with notes
- ✅ **Data Correction** - Propose and approve data corrections
- ✅ **Contact Verification** - Enhanced email and phone verification
- ✅ **Visual Indicators** - Color-coded verification status indicators
- ✅ **Notification System** - Real-time notifications for verification completion

### Security Features

- ✅ **Authentication & Authorization** - JWT-based auth with RBAC
- ✅ **Audit Logging** - Comprehensive audit trail of all actions
- ✅ **Security Headers** - HTTP security headers middleware
- ✅ **Rate Limiting** - API rate limiting to prevent abuse
- ✅ **Password Security** - Strong password requirements and hashing
- ✅ **Security Audit Service** - Automated security monitoring

### Performance Features

- ✅ **Database Optimization** - Comprehensive indexes and eager loading
- ✅ **Redis Caching** - Caching for frequently accessed data
- ✅ **Code Splitting** - Frontend code splitting and lazy loading
- ✅ **Query Optimization** - Optimized database queries with batch loading

## Development

### Code Quality

- **Linting:** Ruff (Python), ESLint (TypeScript)
- **Formatting:** Black (Python), Prettier (TypeScript)
- **Type Checking:** MyPy (Python), TypeScript
- **Testing:** pytest (Python), Vitest (TypeScript)

### CI/CD

GitHub Actions workflow runs on every push and pull request:
- Backend tests with PostgreSQL and Redis
- Frontend tests and build verification
- Code coverage reporting
- Build verification

## Testing

### Test Coverage

- **Backend:** 25+ test files covering all services and APIs
- **Frontend:** 8+ test files covering components and utilities
- **Security:** Comprehensive security test suite
- **Performance:** Performance benchmarks and load testing

### Running Tests

```bash
# All backend tests
cd backend && pytest

# With coverage
pytest --cov=app --cov-report=html

# Security tests
pytest tests/test_security.py tests/test_security_audit.py

# Performance tests
pytest tests/test_performance.py --benchmark-only
```

## Performance Targets

- **API Endpoints:** < 500ms (95th percentile)
- **List Views:** < 2 seconds
- **Report Generation:** < 30 seconds
- **AI Analysis:** < 2 hours
- **Concurrent Users:** 100+ supported

## Security & Compliance

- **GDPR Compliant** - Data protection and privacy compliance
- **WCAG 2.1 Level AA** - Accessibility standards
- **Audit Logging** - Complete audit trail
- **Role-Based Access Control** - Fine-grained permissions
- **Security Headers** - HTTP security headers
- **Rate Limiting** - DDoS and abuse protection

## Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Submit a pull request

## License

Proprietary - SkyFi

## Support

For issues and questions, please refer to the documentation or contact the development team.

---

**Status:** Phase 4 (Testing & Refinement) - 100% Complete, Phase 5 (Launch) - 89% Complete  
**Last Updated:** 2025
