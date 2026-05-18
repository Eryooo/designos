"""MCP stdio Server for PDF parsing."""

import json
import sys
from pathlib import Path

from core import PdfParseError, parse_pdf


def handle_parse_pdf(params: dict) -> dict:
    """Handle parse_pdf tool call.

    Args:
        params: Tool parameters with 'path' key

    Returns:
        Dict with parsed PDF content or error
    """
    try:
        path = params.get("path")
        if not path:
            return {
                "error": {
                    "code": "invalid_params",
                    "message": "Missing required parameter: path",
                }
            }

        result = parse_pdf(Path(path))
        return {"result": result.model_dump()}

    except FileNotFoundError as e:
        return {
            "error": {
                "code": "file_not_found",
                "message": str(e),
            }
        }
    except PdfParseError as e:
        return {
            "error": {
                "code": "parse_error",
                "message": e.message,
                "path": str(e.path),
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "internal_error",
                "message": f"Unexpected error: {e}",
            }
        }


def handle_request(request: dict) -> dict:
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
        tool_name = params.get("name")
        tool_params = params.get("arguments", {})

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
    elif method == "notifications/initialized":
        return None  # No response for notifications

    # Unknown method
    else:
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

        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {e}",
                },
            }
            print(json.dumps(error_response), flush=True)
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {e}",
                },
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
