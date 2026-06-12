"""MCP stdio Server for PDF parsing."""

import json
import sys
from pathlib import Path
from typing import Any

from core import PdfParseError, parse_pdf


def handle_parse_pdf(params: dict[str, Any]) -> dict[str, Any]:
    """Handle parse_pdf tool call.

    Args:
        params: Tool parameters with 'path' key

    Returns:
        Dict with parsed PDF content or error
    """
    try:
        path_value = params.get("path")
        if not isinstance(path_value, str) or not path_value:
            return {
                "error": {
                    "code": "invalid_params",
                    "message": "Missing required parameter: path",
                }
            }

        result = parse_pdf(Path(path_value))
        return {"result": result.model_dump()}

    except FileNotFoundError as exc:
        return {
            "error": {
                "code": "file_not_found",
                "message": str(exc),
            }
        }
    except PdfParseError as exc:
        return {
            "error": {
                "code": "parse_error",
                "message": exc.message,
                "path": str(exc.path),
            }
        }
    except Exception as exc:
        return {
            "error": {
                "code": "internal_error",
                "message": f"Unexpected error: {exc}",
            }
        }


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    """Handle incoming JSON-RPC request.

    Args:
        request: JSON-RPC request object

    Returns:
        JSON-RPC response object
    """
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")

    # Handle tool calls
    if method == "tools/call":
        if not isinstance(params, dict):
            params = {}
        tool_name = params.get("name")
        tool_params = params.get("arguments", {})
        if not isinstance(tool_params, dict):
            tool_params = {}

        if tool_name == "parse_pdf":
            response_data = handle_parse_pdf(tool_params)
        else:
            response_data = {
                "error": {
                    "code": "method_not_found",
                    "message": f"Unknown tool: {tool_name}",
                }
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            **response_data,
        }

    # Handle tools/list
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "parse_pdf",
                        "description": "Parse a PDF file and extract structured content with sections, metadata, and raw text",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "Path to the PDF file to parse",
                                }
                            },
                            "required": ["path"],
                        },
                    }
                ]
            },
        }

    # Handle initialize
    elif method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                },
                "serverInfo": {
                    "name": "designos-pdf-parser",
                    "version": "0.1.0",
                },
            },
        }

    # Handle notifications/initialized
    if method == "notifications/initialized":
        return None  # No response for notifications

    # Unknown method
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32601,
            "message": f"Method not found: {method}",
        },
    }


def main() -> None:
    """Main entry point for MCP stdio server.

    Reads JSON-RPC requests from stdin and writes responses to stdout.
    """
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = handle_request(request)

            if response is not None:
                print(json.dumps(response), flush=True)

        except json.JSONDecodeError as exc:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {exc}",
                },
            }
            print(json.dumps(error_response), flush=True)
        except Exception as exc:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {exc}",
                },
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
