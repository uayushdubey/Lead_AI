"""Health-check router — first endpoint every service needs."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str


@router.get("", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    """Returns service status. Used by Docker / load-balancer probes."""
    return HealthResponse(status="ok", version="0.1.0")
