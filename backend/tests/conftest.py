"""Pytest configuration and fixtures"""

import pytest
from sqlalchemy import create_engine, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.types import TypeDecorator
from uuid import uuid4
import uuid
from app.core.security import get_password_hash
from fastapi.testclient import TestClient

# Patch PostgreSQL UUID for SQLite compatibility BEFORE importing models
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

class GUID(TypeDecorator):
    """Platform-independent GUID type for SQLite compatibility"""
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'sqlite':
            return dialect.type_descriptor(String(36))
        else:
            return dialect.type_descriptor(PG_UUID(as_uuid=True))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'sqlite':
            return str(value) if isinstance(value, uuid.UUID) else value
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'sqlite':
            return uuid.UUID(value) if isinstance(value, str) else value
        return value

# Monkey-patch UUID before models are imported
import sqlalchemy.dialects.postgresql
_original_uuid = sqlalchemy.dialects.postgresql.UUID

def _patched_uuid(*args, **kwargs):
    # Check if we're in a test environment with SQLite
    import sys
    if 'sqlite' in str(sys.modules.get('app.db.database', '')):
        return GUID()
    return _original_uuid(*args, **kwargs)

# Temporarily replace UUID
sqlalchemy.dialects.postgresql.UUID = _patched_uuid

# Now import models (they'll use the patched UUID)
from app.db.database import Base, get_db
from app.models.company import Company
from app.models.user import User
from app.models.verification_result import VerificationResult
from app.models.company_data import CompanyData
from app.models.review import Review
from app.models.data_correction import DataCorrection
from app.models.contact_verification import ContactVerificationResult
from app.main import app

# Restore original UUID after imports
sqlalchemy.dialects.postgresql.UUID = _original_uuid


# Test database URL - Use PostgreSQL for proper UUID support
# Fallback to SQLite if PostgreSQL is not available
import os
from urllib.parse import quote_plus

# Check if we should use PostgreSQL (from environment or default to True for tests)
USE_POSTGRES = os.getenv("USE_POSTGRES_TEST", "true").lower() == "true"

if USE_POSTGRES:
    # PostgreSQL connection for tests
    POSTGRES_USER = os.getenv("POSTGRES_TEST_USER", "test_user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_TEST_PASSWORD", "test_password")
    POSTGRES_DB = os.getenv("POSTGRES_TEST_DB", "ecvi_test")
    POSTGRES_HOST = os.getenv("POSTGRES_TEST_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_TEST_PORT", "5433")
    
    SQLALCHEMY_TEST_DATABASE_URL = (
        f"postgresql://{POSTGRES_USER}:{quote_plus(POSTGRES_PASSWORD)}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    
    # Restore original UUID for PostgreSQL
    sqlalchemy.dialects.postgresql.UUID = _original_uuid
    
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,
        max_overflow=10,
    )
else:
    # Fallback to SQLite (with UUID workaround)
    SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
    sqlalchemy.dialects.postgresql.UUID = lambda *args, **kwargs: GUID()
    
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use security module for password hashing to ensure compatibility
# Import lazily to avoid initialization issues
def hash_password(password: str) -> str:
    """Hash password using security module (passlib)"""
    from app.core.security import get_password_hash
    return get_password_hash(password)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Drop all tables and recreate for clean state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
        session.rollback()  # Rollback any uncommitted changes
    finally:
        session.close()
        # Clean up: drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """Override get_db dependency for testing"""
    def _get_db():
        try:
            yield db_session
        finally:
            pass
    return _get_db


@pytest.fixture(scope="function")
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        password_hash=hash_password("TestPass123!"),
        role="operator",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_admin_user(db_session):
    """Create a test admin user"""
    user = User(
        id=uuid4(),
        email="admin@example.com",
        username="admin",
        password_hash=hash_password("AdminPass123!"),
        role="admin",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_company(db_session):
    """Create a test company"""
    company = Company(
        id=uuid4(),
        legal_name="Test Company Inc",
        registration_number="12345678",
        jurisdiction="US",
        domain="testcompany.com"
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture(scope="function")
def test_verification_result(db_session, test_company):
    """Create a test verification result"""
    from app.models.verification_result import VerificationStatus, RiskCategory
    
    verification = VerificationResult(
        id=uuid4(),
        company_id=test_company.id,
        risk_score=50,
        risk_category=RiskCategory.MEDIUM,
        verification_status=VerificationStatus.COMPLETED
    )
    db_session.add(verification)
    db_session.commit()
    db_session.refresh(verification)
    return verification
