"""
Health API route
SPEC.md Section 5: Health check endpoint
"""
import logging

from fastapi import APIRouter

from api.schemas import HealthStatus
from workflow.orchestrator import WorkflowOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])

orchestrator = WorkflowOrchestrator()


@router.get("/health", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """Health check (all engines)"""
    engine_health = orchestrator.check_health()

    return HealthStatus(
        status="healthy" if all(engine_health.values()) else "degraded",
        argo=engine_health.get("argo", False),
        temporal=engine_health.get("temporal", False),
        airflow=engine_health.get("airflow", False),
        redis=True,  # Assume healthy for demo
        postgresql=True,  # Assume healthy for demo
    )