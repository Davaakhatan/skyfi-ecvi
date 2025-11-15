# ECVI Backend

Backend API for Enterprise Company Verification Intelligence system.

## Technology Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL with SQLAlchemy
- **Migrations:** Alembic
- **Task Queue:** Celery with Redis
- **Python:** 3.11+

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e ".[dev]"
```

3. Copy environment file:
```bash
cp .env.example .env
```

4. Update `.env` with your configuration

5. Run database migrations:
```bash
alembic upgrade head
```

### Running the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API documentation will be available at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
ruff check app/
```

### Type Checking

```bash
mypy app/
```

## Project Structure

```
backend/
├── app/
│   ├── api/v1/        # API endpoints
│   ├── core/          # Core functionality (config, auth, security)
│   ├── models/        # Database models
│   ├── services/      # Business logic
│   ├── tasks/         # Celery tasks
│   ├── utils/         # Utility functions
│   └── db/            # Database configuration
├── tests/             # Tests
└── pyproject.toml     # Dependencies and config
```

