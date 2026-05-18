"""Unit tests for MCP server."""

import json
import sys
from pathlib import Path

import pytest

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from server import handle_request, handle_parse_pdf


def test_handle_parse_pdf_success(sample_prd_path: Path) -> None:
    """Test successful PDF parsing through handler."""
    params = {"path": str(sample_prd_path)}
    response = handle_parse_pdf(params)

    assert "result" in response
    assert "error" not in response

    result = response["result"]
    assert "sections" in result
    assert "metadata" in result
    assert "raw_text" in result
    assert len(result["sections"]) > 0


def test_handle_parse_pdf_missing_path() -> None:
    """Test error when path parameter is missing."""
    params = {}
    response = handle_parse_pdf(params)

    assert "error" in response
    assert response["error"]["code"] == "invalid_params"
    assert "path" in response["error"]["message"].lower()


def test_handle_parse_pdf_file_not_found() -> None:
    """Test error when file does not exist."""
    params = {"path": "/nonexistent/file.pdf"}
    response = handle_parse_pdf(params)

    assert "error" in response
    assert response["error"]["code"] == "file_not_found"


def test_handle_parse_pdf_parse_error(scanned_pdf_path: Path) -> None:
    """Test error when PDF has no text layer."""
    params = {"path": str(scanned_pdf_path)}
    response = handle_parse_pdf(params)

    assert "error" in response
    assert response["error"]["code"] == "parse_error"
    assert "no text layer" in response["error"]["message"].lower()


def test_handle_request_tools_list() -> None:
    """Test tools/list method."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {},
    }
    response = handle_request(request)

    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert "result" in response
    assert "tools" in response["result"]
    assert len(response["result"]["tools"]) == 1
    assert response["result"]["tools"][0]["name"] == "parse_pdf"


def test_handle_request_initialize() -> None:
    """Test initialize method."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {},
    }
    response = handle_request(request)

    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert "result" in response
    assert response["result"]["serverInfo"]["name"] == "designos-pdf-parser"
    assert response["result"]["serverInfo"]["version"] == "0.1.0"


def test_handle_request_tools_call(sample_prd_path: Path) -> None:
    """Test tools/call method."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "parse_pdf",
            "arguments": {"path": str(sample_prd_path)},
        },
    }
    response = handle_request(request)

    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert "result" in response


def test_handle_request_unknown_tool() -> None:
    """Test error when calling unknown tool."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "unknown_tool",
            "arguments": {},
        },
    }
    response = handle_request(request)

    assert "error" in response
    assert "unknown tool" in response["error"]["message"].lower()


def test_handle_request_unknown_method() -> None:
    """Test error when calling unknown method."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "unknown/method",
        "params": {},
    }
    response = handle_request(request)

    assert "error" in response
    assert response["error"]["code"] == -32601


def test_handle_request_notification() -> None:
    """Test that notifications return None."""
    request = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {},
    }
    response = handle_request(request)

    assert response is None
