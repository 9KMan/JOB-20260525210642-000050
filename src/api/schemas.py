"""
API Schemas - Request/Response models for FastAPI
"""
from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field

from db.models import EngineType, WorkflowStatus, ConnectorType, ExecutionStatus, IntegrationType


# Workflow Schemas
class WorkflowCreate(BaseModel):
    name: str
    engine: EngineType
    definition: Dict[str, Any]
    owner: str


class WorkflowResponse(BaseModel):
    id: str
    name: str
    engine: str
    definition: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    owner: str
    status: str


class WorkflowRunRequest(BaseModel):
    inputs: Dict[str, Any] = Field(default_factory=dict)


class ExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    run_id: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    error: Optional[str]


# Connector Schemas
class ConnectorCreate(BaseModel):
    name: str
    type: IntegrationType
    config: Dict[str, Any]
    azure_subscription_id: Optional[str] = None


class ConnectorResponse(BaseModel):
    id: str
    name: str
    type: str
    config: Dict[str, Any]
    azure_subscription_id: Optional[str]


class ConnectorTestResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None


# Health Check
class HealthStatus(BaseModel):
    status: str
    argo: bool
    temporal: bool
    airflow: bool
    redis: bool
    postgresql: bool


# Generic Message Response
class MessageResponse(BaseModel):
    message: str
    success: bool = True