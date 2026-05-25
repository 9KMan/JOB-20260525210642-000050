"""
Tests for connectors
"""
import pytest

from workers.connectors import (
    create_connector,
    AzureSDKConnector,
    DBConnector,
    HTTPConnector,
)


def test_create_azure_connector():
    connector = create_connector("azure_sdk", {"subscription": "test"})
    assert isinstance(connector, AzureSDKConnector)
    assert connector.health_check() is True


def test_create_db_connector():
    connector = create_connector("db", {"host": "localhost"})
    assert isinstance(connector, DBConnector)
    assert connector.health_check() is True


def test_create_http_connector():
    connector = create_connector("http", {"url": "https://api.example.com"})
    assert isinstance(connector, HTTPConnector)
    assert connector.health_check() is True


def test_connector_execute():
    connector = HTTPConnector({"url": "https://api.example.com"})
    result = connector.execute("GET", {"path": "/status"})
    assert result["status"] == "success"
    assert result["action"] == "GET"