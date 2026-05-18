"""MCP stdio Server for image-analyzer.

Exposes a single tool: load_and_analyze
"""

import json
import sys
from pathlib import Path

from core import load_and_analyze


def handle_load_and_analyze(params: dict) -> dict:
    """Handle load_and_analyze tool call.

    Args:
        params: Tool arguments with 'screenshots_dir' and optional
                'task_checklist_lite' keys.

    Returns:
        Dict with 'result' key on success or 'error' key on failure.
    """
    screenshots_dir = params.get("screenshots_dir")
    if not screenshots_dir:
        return {
            "error": {
                "code": "invalid_params",
                "message": "Missing required parameter: screenshots_dir",
            }
        }

    task_checklist_lite: str | None = params.get("task_checklist_lite")

    try:
        result = load_and_analyze(
            screenshots_dir=Path(screenshots_dir),
            task_checklist_lite=task_checklist_lite,
        )
        return {"result": result.model_dump()}

    except FileNotFoundError as exc:
        return {
            "error": {
                "code": "dir_not_found",
                "message": str(exc),
            }
        }
    except NotADirectoryError as exc:
        return {
            "error": {
                "code": "not_a_directory",
                "message": str(exc),
            }
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "error": {
                "code": "internal_error",
                "message": f"Unexpected error: {exc}",
            }
        }


def handle_request(request: dict) -> dict | None:
    """Dispatch a JSON-RPC request to the appropriate handler.

    Args:
        request: Parsed JSON-RPC request object.

    Returns:
        JSON-RPC response dict, or None for notifications.
    """
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")

    if method == "tools/call":
        tool_name = params.get("name")
        tool_params = params.get("arguments", {})

        if tool_name == "load_and_analyze":
            response_data = handle_load_and_analyze(tool_params)
        else:
            response_data = {
                "error": {
                    "code": "method_not_found",
                    "message": f"Unknown tool: {tool_name}",
                }
            }

        return {"jsonrpc": "2.0", "id": request_id, **response_data}

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "load_and_analyze",
                        "description": (
                            "Load all screenshots and description files from a directory "
                            "and return ScreenshotRef list with stub analysis. "
                            "Supports .png/.jpg/.jpeg/.webp/.gif/.bmp (images) and "
                            ".md (text descriptions). M1 stub — no vision analysis."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "screenshots_dir": {
                                    "type": "string",
                                    "description": "Absolute path to directory containing screenshots",
                                },
                                "task_checklist_lite": {
                                    "type": "string",
                                    "description": "Lite task checklist (reserved for M2, ignored in M1)",
                                },
                            },
                            "required": ["screenshots_dir"],
                        },
                    }
                ]
            },
        }

    elif method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "designos-image-analyzer",
                    "version": "0.1.0",
                },
            },
        }

    elif method == "notifications/initialized":
        return None  # notifications require no response

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
    """Entry point: read JSON-RPC from stdin, write responses to stdout."""
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
            print(
                json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {exc}"},
                }),
                flush=True,
            )
        except Exception as exc:  # noqa: BLE001
            print(
                json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": f"Internal error: {exc}"},
                }),
                flush=True,
            )


if __name__ == "__main__":
    main()
