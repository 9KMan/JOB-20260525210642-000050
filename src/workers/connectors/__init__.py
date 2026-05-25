"""
Connector factory - creates appropriate connector based on type
"""
from workers.connectors.base import (
    BaseConnector,
    AzureSDKConnector,
    DBConnector,
    HTTPConnector,
    FileConnector,
    EventConnector,
    CustomConnector,
)
from db.models import ConnectorType


def create_connector(connector_type: str, config: dict) -> BaseConnector:
    """Factory function to create connector based on type"""
    type_map = {
        ConnectorType.AZURE_SDK.value: AzureSDKConnector,
        ConnectorType.DB.value: DBConnector,
        ConnectorType.HTTP.value: HTTPConnector,
        ConnectorType.FILE.value: FileConnector,
        ConnectorType.EVENT.value: EventConnector,
        ConnectorType.CUSTOM.value: CustomConnector,
    }

    connector_class = type_map.get(connector_type, CustomConnector)
    return connector_class(config)


__all__ = [
    "BaseConnector",
    "AzureSDKConnector",
    "DBConnector",
    "HTTPConnector",
    "FileConnector",
    "EventConnector",
    "CustomConnector",
    "create_connector",
]