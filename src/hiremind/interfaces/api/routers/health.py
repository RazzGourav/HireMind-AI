"""Healthcheck and readiness probes."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/health", tags=["System"])


@router.get("")
async def health_check():
    """Simple liveness probe."""
    return {"status": "healthy", "version": "1.0"}
