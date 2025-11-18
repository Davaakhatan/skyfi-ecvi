"""Pytest configuration and fixtures"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import uuid4
from passlib.context import CryptContext

from app.db.database import Base, get_db
from app.models.company import Company
from app.models.user import User
from app.models.verification_result import VerificationResult
from app.models.company_data import CompanyData
from app.models.review import Review
from app.models.data_correction import DataCorrection
from app.models.contact_verification import ContactVerificationResult


# Test database URL (in-memory SQLite for testing)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
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
def test_user(db_session):
    """Create a test user"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        password_hash=pwd_context.hash("testpassword"),
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
        password_hash=pwd_context.hash("adminpassword"),
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

