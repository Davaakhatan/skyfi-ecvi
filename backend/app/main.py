"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Company Verification Intelligence API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    """Health check endpoint"""
    return {"status": "healthy"}


# API routers
from app.api.v1 import auth, audit, companies, risk_scoring, reports

app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])
app.include_router(companies.router, prefix="/api/v1/companies", tags=["companies"])
app.include_router(risk_scoring.router, prefix="/api/v1/risk", tags=["risk-scoring"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])

