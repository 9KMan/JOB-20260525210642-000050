"""
Tests for workflow orchestrator
"""
import pytest

from workflow.orchestrator import (
    ArgoWorkflowEngine,
    TemporalEngine,
    AirflowEngine,
    get_engine,
    WorkflowOrchestrator,
)
from db.models import Workflow, EngineType


def test_argo_engine():
    engine = ArgoWorkflowEngine()
    assert engine is not None


def test_temporal_engine():
    engine = TemporalEngine()
    assert engine is not None


def test_airflow_engine():
    engine = AirflowEngine()
    assert engine is not None


def test_get_engine():
    argo = get_engine("argo")
    assert isinstance(argo, ArgoWorkflowEngine)

    temporal = get_engine("temporal")
    assert isinstance(temporal, TemporalEngine)

    airflow = get_engine("airflow")
    assert isinstance(airflow, AirflowEngine)


def test_orchestrator_trigger():
    orchestrator = WorkflowOrchestrator()
    workflow = Workflow(
        name="Test Workflow",
        engine=EngineType.ARGO,
        definition={},
        owner="test",
    )
    execution = orchestrator.trigger_workflow(workflow, {"input": "value"})
    assert execution is not None
    assert execution.run_id.startswith("argo-")