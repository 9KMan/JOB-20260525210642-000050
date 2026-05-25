"""
Connector API routes
SPEC.md Section 5: API Design - Connector management
"""
import logging
from typing import List

from fastapi import APIRouter, HTTPException, status

from api.schemas import (
    ConnectorCreate,
    ConnectorResponse,
    ConnectorTestResponse,
    MessageResponse,
)
from db.models import IntegrationConnector, IntegrationType
from workers.connectors import create_connector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/connectors", tags=["connectors"])

# In-memory storage for demo
connectors_db: dict = {}


@router.post("", response_model=ConnectorResponse, status_code=status.HTTP_201_CREATED)
async def create_connector_endpoint(connector: ConnectorCreate) -> ConnectorResponse:
    """Register new integration connector"""
    try:
        conn_type = IntegrationType(connector.type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid connector type: {connector.type}"
        )

    conn = IntegrationConnector(
        name=connector.name,
        type=conn_type,
        config=connector.config,
        azure_subscription_id=connector.azure_subscription_id,
    )
    connectors_db[str(conn.id)] = conn

    logger.info(f"Created connector: {conn.name} ({conn.id})")
    return ConnectorResponse(
        id=str(conn.id),
        name=conn.name,
        type=conn.type,
        config=conn.config,
        azure_subscription_id=str(conn.azure_subscription_id) if conn.azure_subscription_id else None,
    )


@router.get("", response_model=List[ConnectorResponse])
async def list_connectors() -> List[ConnectorResponse]:
    """List all connectors"""
    return [
        ConnectorResponse(
            id=str(c.id),
            name=c.name,
            type=c.type,
            config=c.config,
            azure_subscription_id=str(c.azure_subscription_id) if c.azure_subscription_id else None,
        )
        for c in connectors_db.values()
    ]


@router.post("/{connector_id}/test", response_model=ConnectorTestResponse)
async def test_connector(connector_id: str) -> ConnectorTestResponse:
    """Test connector connectivity"""
    if connector_id not in connectors_db:
        raise HTTPException(status_code=404, detail="Connector not found")

    conn = connectors_db[connector_id]
    try:
        connector = create_connector(conn.type, conn.config)
        is_healthy = connector.health_check()
        return ConnectorTestResponse(
            success=is_healthy,
            message="Connector healthy" if is_healthy else "Connector unhealthy",
        )
    except Exception as e:
        logger.error(f"Connector test failed: {e}")
        return ConnectorTestResponse(
            success=False,
            message=f"Connector test failed: {str(e)}",
        )