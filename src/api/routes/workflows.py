"""
Workflow API routes
SPEC.md Section 5: API Design
"""
import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from api.schemas import (
    WorkflowCreate,
    WorkflowResponse,
    WorkflowRunRequest,
    ExecutionResponse,
    MessageResponse,
)
from db.models import Workflow, Execution, EngineType, ExecutionStatus
from workflow.orchestrator import WorkflowOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/workflows", tags=["workflows"])

# In-memory storage for demo (use PostgreSQL in production)
workflows_db: dict = {}
executions_db: dict = {}
orchestrator = WorkflowOrchestrator()


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(workflow: WorkflowCreate) -> WorkflowResponse:
    """Register new workflow (Argo/Temporal/Airflow)"""
    try:
        engine_type = EngineType(workflow.engine)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid engine type: {workflow.engine}"
        )

    wf = Workflow(
        name=workflow.name,
        engine=engine_type,
        definition=workflow.definition,
        owner=workflow.owner,
    )
    workflows_db[str(wf.id)] = wf

    logger.info(f"Created workflow: {wf.name} ({wf.id})")
    return WorkflowResponse(
        id=str(wf.id),
        name=wf.name,
        engine=wf.engine,
        definition=wf.definition,
        created_at=wf.created_at,
        updated_at=wf.updated_at,
        owner=wf.owner,
        status=wf.status,
    )


@router.get("", response_model=List[WorkflowResponse])
async def list_workflows() -> List[WorkflowResponse]:
    """List all workflows with status"""
    return [
        WorkflowResponse(
            id=str(wf.id),
            name=wf.name,
            engine=wf.engine,
            definition=wf.definition,
            created_at=wf.created_at,
            updated_at=wf.updated_at,
            owner=wf.owner,
            status=wf.status,
        )
        for wf in workflows_db.values()
    ]


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str) -> WorkflowResponse:
    """Get workflow definition"""
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")

    wf = workflows_db[workflow_id]
    return WorkflowResponse(
        id=str(wf.id),
        name=wf.name,
        engine=wf.engine,
        definition=wf.definition,
        created_at=wf.created_at,
        updated_at=wf.updated_at,
        owner=wf.owner,
        status=wf.status,
    )


@router.post("/{workflow_id}/run", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
async def run_workflow(workflow_id: str, request: WorkflowRunRequest) -> ExecutionResponse:
    """Trigger workflow execution"""
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")

    wf = workflows_db[workflow_id]
    execution = orchestrator.trigger_workflow(wf, request.inputs)
    executions_db[str(execution.id)] = execution

    logger.info(f"Triggered workflow {wf.name}, execution: {execution.id}")
    return ExecutionResponse(
        id=str(execution.id),
        workflow_id=str(execution.workflow_id),
        run_id=execution.run_id,
        status=execution.status,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        inputs=execution.inputs,
        outputs=execution.outputs,
        error=execution.error,
    )


@router.get("/{workflow_id}/runs", response_model=List[ExecutionResponse])
async def list_workflow_runs(workflow_id: str) -> List[ExecutionResponse]:
    """List execution history"""
    return [
        ExecutionResponse(
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
        for ex in executions_db.values()
        if str(ex.workflow_id) == workflow_id
    ]


@router.post("/{workflow_id}/pause", response_model=MessageResponse)
async def pause_workflow(workflow_id: str) -> MessageResponse:
    """Pause active workflow"""
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")

    wf = workflows_db[workflow_id]
    orchestrator.pause_workflow(wf)
    logger.info(f"Paused workflow: {wf.name}")
    return MessageResponse(message=f"Workflow {wf.name} paused", success=True)


@router.post("/{workflow_id}/resume", response_model=MessageResponse)
async def resume_workflow(workflow_id: str) -> MessageResponse:
    """Resume paused workflow"""
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")

    wf = workflows_db[workflow_id]
    orchestrator.resume_workflow(wf)
    logger.info(f"Resumed workflow: {wf.name}")
    return MessageResponse(message=f"Workflow {wf.name} resumed", success=True)