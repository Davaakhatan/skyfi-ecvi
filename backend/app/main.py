"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.metrics import MetricsMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Company Verification Intelligence API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware - production-safe configuration
cors_origins = settings.cors_origins_list
if settings.is_production and not cors_origins:
    # In production, require explicit CORS configuration
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("CORS_ORIGINS not configured in production. Defaulting to empty list.")
    cors_origins = []

# Add security headers middleware (first, so it applies to all responses)
app.add_middleware(SecurityHeadersMiddleware)

# Add metrics middleware (before rate limiting to capture all requests)
app.add_middleware(MetricsMiddleware)

# Add rate limiting middleware (if enabled)
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE
    )

# CORS middleware - production-safe configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else [] if settings.is_production else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"] if settings.is_production else ["*"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"] if settings.is_production else ["*"],
    expose_headers=["X-Total-Count", "X-Page-Count"],
    max_age=3600,  # Cache preflight requests for 1 hour
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ECVI API",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity check"""
    from app.db.database import engine
    from sqlalchemy import text
    
    try:
        # Check database connectivity
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check Redis connectivity (if configured)
    redis_status = "not_configured"
    try:
        from app.core.config import settings
        import redis
        if settings.REDIS_URL:
            # Try to connect with a short timeout and handle auth errors gracefully
            redis_client = redis.from_url(
                settings.REDIS_URL, 
                socket_connect_timeout=2,
                socket_timeout=2,
                decode_responses=False,
                health_check_interval=0  # Disable health check to avoid auth issues
            )
            redis_client.ping()
            redis_status = "healthy"
    except (redis.exceptions.AuthenticationError, redis.exceptions.ConnectionError):
        # Redis connection/auth issues - mark as not configured (optional service)
        redis_status = "not_configured"
    except Exception as e:
        # Other connection errors
        redis_status = f"unhealthy: {str(e)[:50]}"
    
    overall_status = "healthy" if db_status == "healthy" else "degraded"
    
    return {
        "status": overall_status,
        "database": db_status,
        "redis": redis_status,
        "version": settings.APP_VERSION
    }


# Initialize Sentry for error tracking (if DSN is configured)
if settings.is_production:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        
        sentry_dsn = getattr(settings, 'SENTRY_DSN', None)
        if sentry_dsn:
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[
                    FastApiIntegration(),
                    SqlalchemyIntegration(),
                    RedisIntegration(),
                ],
                traces_sample_rate=0.1,  # Sample 10% of transactions
                environment=settings.ENVIRONMENT,
                release=settings.APP_VERSION,
            )
    except ImportError:
        pass  # Sentry not installed
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to initialize Sentry: {e}")

# API routers
from app.api.v1 import auth, audit, companies, risk_scoring, reports, reviews, data_corrections, contact_verification, security, metrics

app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])
app.include_router(companies.router, prefix="/api/v1/companies", tags=["companies"])
app.include_router(risk_scoring.router, prefix="/api/v1/risk", tags=["risk-scoring"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(data_corrections.router, prefix="/api/v1", tags=["data-corrections"])
app.include_router(contact_verification.router, prefix="/api/v1", tags=["contact-verification"])
app.include_router(security.router, prefix="/api/v1/security", tags=["security"])

