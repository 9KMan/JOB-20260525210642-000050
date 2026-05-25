"""
Integration Engineering Platform - Data Models
Based on SPEC.md Section 4 Data Model
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field


class EngineType(str, Enum):
    ARGO = "argo"
    TEMPORAL = "temporal"
    AIRFLOW = "airflow"


class WorkflowStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ConnectorType(str, Enum):
    AZURE_SDK = "azure_sdk"
    DB = "db"
    HTTP = "http"
    FILE = "file"
    EVENT = "event"
    CUSTOM = "custom"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IntegrationType(str, Enum):
    BLOB_STORAGE = "blob_storage"
    SQL_DB = "sql_db"
    SERVICE_BUS = "service_bus"
    EVENT_HUB = "event_hub"
    KEY_VAULT = "key_vault"
    CUSTOM = "custom"


class Workflow(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    engine: EngineType
    definition: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    owner: str
    status: WorkflowStatus = WorkflowStatus.ACTIVE

    class Config:
        use_enum_values = True


class Task(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow_id: uuid.UUID
    name: str
    connector_type: ConnectorType
    config: Dict[str, Any] = Field(default_factory=dict)
    retry_policy: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = 300

    class Config:
        use_enum_values = True


class Execution(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow_id: uuid.UUID
    run_id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

    class Config:
        use_enum_values = True


class AzureSubscription(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: str
    client_id: str
    subscription_id: str
    scope: str


class IntegrationConnector(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    type: IntegrationType
    config: Dict[str, Any] = Field(default_factory=dict)
    azure_subscription_id: Optional[uuid.UUID] = None

    class Config:
        use_enum_values = True


class RetryPolicy(BaseModel):
    max_attempts: int = 3
    initial_interval_seconds: int = 1
    backoff_multiplier: float = 2.0
    max_interval_seconds: int = 60


class WorkflowDefinition(BaseModel):
    tasks: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]] = {}