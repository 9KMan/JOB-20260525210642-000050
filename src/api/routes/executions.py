"""
Execution API routes
SPEC.md Section 5: API Design - Get specific execution status/outputs
"""
import logging
from fastapi import APIRouter, HTTPException, status

from api.schemas import ExecutionResponse, MessageResponse
from db.models import Execution
from workflow.orchestrator import WorkflowOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/runs", tags=["executions"])

# Shared storage (in production, use database)
executions_db: dict = {}
orchestrator = WorkflowOrchestrator()


@router.get("/{run_id}", response_model=ExecutionResponse)
async def get_execution(run_id: str) -> ExecutionResponse:
    """Get specific execution status/outputs"""
    for ex in executions_db.values():
        if ex.run_id == run_id:
            return ExecutionResponse(
                id=str(ex.id),
                workflow_id=str(ex.workflow_id),
                run_id=ex.run_id,
                status=ex.status,
                started_at=ex.started_at,
                completed_at=ex.completed_at,
                inputs=ex.inputs,
                outputs=ex.outputs,
                error=ex.error,
            )

    # In production, query the workflow engine for status
    # For demo, return not found
    raise HTTPException(status_code=404, detail=f"Execution {run_id} not found")