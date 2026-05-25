"""
Tests for data models
"""
import pytest
from uuid import UUID

from db.models import (
    Workflow,
    Task,
    Execution,
    EngineType,
    ExecutionStatus,
    WorkflowStatus,
    ConnectorType,
)


def test_workflow_creation():
    workflow = Workflow(
        name="Test Workflow",
        engine=EngineType.ARGO,
        definition={"tasks": []},
        owner="test_user",
    )
    assert workflow.name == "Test Workflow"
    assert workflow.engine == EngineType.ARGO
    assert isinstance(workflow.id, UUID)


def test_execution_creation():
    workflow = Workflow(
        name="Test Workflow",
        engine=EngineType.TEMPORAL,
        definition={},
        owner="test_user",
    )
    execution = Execution(
        workflow_id=workflow.id,
        run_id="run-123",
        inputs={"param": "value"},
    )
    assert execution.run_id == "run-123"
    assert execution.status == ExecutionStatus.PENDING


def test_engine_type_enum():
    assert EngineType.ARGO.value == "argo"
    assert EngineType.TEMPORAL.value == "temporal"
    assert EngineType.AIRFLOW.value == "airflow"


def test_execution_status_enum():
    assert ExecutionStatus.PENDING.value == "pending"
    assert ExecutionStatus.RUNNING.value == "running"
    assert ExecutionStatus.SUCCEEDED.value == "succeeded"
    assert ExecutionStatus.FAILED.value == "failed"