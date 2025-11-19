"""Metrics API endpoint"""

from fastapi import APIRouter, Response
from app.middleware.metrics import get_metrics

router = APIRouter()


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    metrics_data = get_metrics()
    return Response(
        content=metrics_data,
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )

