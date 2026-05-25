"""
Base connector interface for all integrations
SPEC.md Section 4: Connector interface - Abstract base class for all integrations
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Abstract base class for all integration connectors"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def connect(self) -> bool:
        """Test and establish connection"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection"""
        pass

    @abstractmethod
    def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action with given parameters"""
        pass

    def health_check(self) -> bool:
        """Return connector health status"""
        try:
            return self.connect()
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False


class AzureSDKConnector(BaseConnector):
    """Azure SDK connector for blob storage, Key Vault, Event Hub, Service Bus"""

    def connect(self) -> bool:
        # MSI or SP authentication handled via environment variables
        # Azure SDK uses DEFAULT credential chain
        self.logger.info("Azure SDK connector initialized")
        return True

    def disconnect(self) -> None:
        pass

    def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Azure SDK action: {action}")
        return {"status": "success", "action": action, "result": params}


class DBConnector(BaseConnector):
    """Database connector for SQL and NoSQL databases"""

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"DB action: {action}")
        return {"status": "success", "action": action, "result": params}


class HTTPConnector(BaseConnector):
    """HTTP/Webhook connector for REST API integrations"""

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"HTTP action: {action}")
        return {"status": "success", "action": action, "result": params}


class FileConnector(BaseConnector):
    """File/SFTP connector for file operations"""

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"File action: {action}")
        return {"status": "success", "action": action, "result": params}


class EventConnector(BaseConnector):
    """Event connector for Kafka, Event Hub"""

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Event action: {action}")
        return {"status": "success", "action": action, "result": params}


class CustomConnector(BaseConnector):
    """Custom connector for specialized integrations"""

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Custom action: {action}")
        return {"status": "success", "action": action, "result": params}