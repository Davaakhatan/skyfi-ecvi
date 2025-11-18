"""Application configuration"""

from pydantic_settings import BaseSettings
from pydantic import field_validator, Field
from typing import List
import json
import logging
import os

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "ECVI Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key strength"""
        if not v:
            raise ValueError("SECRET_KEY is required")
        if len(v) < 32:
            if os.getenv('ENVIRONMENT', 'production') == 'production':
                raise ValueError("SECRET_KEY must be at least 32 characters long for production")
            else:
                logger.warning("SECRET_KEY is less than 32 characters. This is not recommended for production.")
        return v
    
    # CORS - can be comma-separated string or JSON array
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS into a list"""
        if not self.CORS_ORIGINS:
            return []
        # Try JSON first
        try:
            origins = json.loads(self.CORS_ORIGINS)
            if isinstance(origins, list):
                return origins
            return [origins] if origins else []
        except (json.JSONDecodeError, TypeError):
            # Fall back to comma-separated string
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # AI/ML
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    LLM_PROVIDER: str = "openai"
    
    # External APIs
    DNS_LOOKUP_SERVICE_URL: str = ""
    COMPANY_REGISTRY_API_KEY: str = ""
    
    # Business Directory APIs
    CRUNCHBASE_API_KEY: str = ""
    GOOGLE_PLACES_API_KEY: str = ""
    YELP_API_KEY: str = ""
    
    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

