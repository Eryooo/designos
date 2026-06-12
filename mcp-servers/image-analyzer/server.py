"""MCP stdio Server for image-analyzer.

Exposes a single tool: load_and_analyze.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from core import PlanningLoopError, RemediationLoopError, load_and_analyze, plan_required_evidence


def handle_load_and_analyze(params: dict[str, Any]) -> dict[str, Any]:
    """Handle load_and_analyze tool call.

    Args:
        params: Tool arguments with 'screenshots_dir' and optional
                'task_checklist_lite' keys.

    Returns:
        Dict with 'result' key on success or 'error' key on failure.
    """
    screenshots_dir = params.get("screenshots_dir")
    if not isinstance(screenshots_dir, str) or not screenshots_dir:
        return {
            "error": {
                "code": "invalid_params",
                "message": "Missing required parameter: screenshots_dir",
            }
        }

    task_checklist_lite: str | None = params.get("task_checklist_lite")
    required_evidence_plan = params.get("required_evidence_plan")
    output_dir_raw = params.get("output_dir")
    output_dir = Path(output_dir_raw) if isinstance(output_dir_raw, str) and output_dir_raw else None
    run_id = params.get("run_id")
    stage_id = params.get("stage_id")

    try:
        result = load_and_analyze(
            screenshots_dir=Path(screenshots_dir),
            task_checklist_lite=task_checklist_lite,
            required_evidence_plan=required_evidence_plan,
            output_dir=output_dir,
            run_id=run_id if isinstance(run_id, str) else None,
            stage_id=stage_id if isinstance(stage_id, str) else None,
        )
        return {"result": result.model_dump()}

    except PlanningLoopError as exc:
        return {
            "error": {
                "code": "planning_loop",
                "message": str(exc),
            }
        }
    except RemediationLoopError as exc:
        return {
            "error": {
                "code": "remediation_loop",
                "message": str(exc),
            }
        }
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
    except Exception as exc:
        return {
            "error": {
                "code": "internal_error",
                "message": f"Unexpected error: {exc}",
            }
        }


def handle_plan_required_evidence(params: dict[str, Any]) -> dict[str, Any]:
    """Handle plan_required_evidence tool call."""
    output_dir_raw = params.get("output_dir")
    output_dir = Path(output_dir_raw) if isinstance(output_dir_raw, str) and output_dir_raw else None
    screenshots_dir = params.get("screenshots_dir")
    run_id = params.get("run_id")
    stage_id = params.get("stage_id")

    try:
        result = plan_required_evidence(
            modules=params.get("modules"),
            key_features=params.get("key_features"),
            task_checklist_lite=params.get("task_checklist_lite"),
            journey_map=params.get("journey_map"),
            journey_stages=params.get("journey_stages"),
            screenshots_dir=screenshots_dir if isinstance(screenshots_dir, str) else None,
            output_dir=output_dir,
            run_id=run_id if isinstance(run_id, str) else None,
            stage_id=stage_id if isinstance(stage_id, str) else None,
        )
        return {"result": result.model_dump()}
    except PlanningLoopError as exc:
        return {
            "error": {
                "code": "planning_loop",
                "message": str(exc),
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
    """Dispatch a JSON-RPC request to the appropriate handler.

    Args:
        request: Parsed JSON-RPC request object.

    Returns:
        JSON-RPC response dict, or None for notifications.
    """
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")
    if not isinstance(params, dict):
        params = {}

    if method == "tools/call":
        tool_name = params.get("name")
        tool_params = params.get("arguments", {})
        if not isinstance(tool_params, dict):
            tool_params = {}

        if tool_name == "load_and_analyze":
            response_data = handle_load_and_analyze(tool_params)
        elif tool_name == "plan_required_evidence":
            response_data = handle_plan_required_evidence(tool_params)
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
                        "name": "plan_required_evidence",
                        "description": (
                            "Build a deterministic client-mode evidence plan from tasks, modules, and "
                            "journey hints, then compare the current screenshot bundle against that plan "
                            "to produce a one-shot supplement checklist before full screenshot analysis."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "modules": {
                                    "description": "Structured modules from PRD understanding",
                                },
                                "key_features": {
                                    "description": "Structured key features from PRD understanding",
                                },
                                "task_checklist_lite": {
                                    "type": "string",
                                    "description": "Lite task checklist used to derive critical page coverage",
                                },
                                "journey_map": {
                                    "description": "Optional journey map text or structured data",
                                },
                                "journey_stages": {
                                    "description": "Optional structured journey stages",
                                },
                                "screenshots_dir": {
                                    "type": "string",
                                    "description": "Optional screenshot directory for pre-run intake planning",
                                },
                                "output_dir": {
                                    "type": "string",
                                    "description": "Optional run output directory for planning-state persistence",
                                },
                                "run_id": {
                                    "type": "string",
                                    "description": "Optional run id for traceability",
                                },
                                "stage_id": {
                                    "type": "string",
                                    "description": "Optional stage id for traceability",
                                },
                            },
                            "required": ["modules", "key_features", "task_checklist_lite"],
                        },
                    },
                    {
                        "name": "load_and_analyze",
                        "description": (
                            "Recursively analyze screenshots and markdown description files "
                            "with real local metadata extraction, OCR-backed text evidence when "
                            "available, screenshot-to-description linking, and input sufficiency "
                            "assessment. Supports "
                            ".png/.jpg/.jpeg/.webp/.gif/.bmp (images) and "
                            ".md (text descriptions). Does not provide full semantic image "
                            "understanding, task attribution, or intent inference."
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
                                    "description": "Optional lite task checklist used to estimate key page/task coverage",
                                },
                                "required_evidence_plan": {
                                    "description": "Optional deterministic evidence plan produced by plan_required_evidence",
                                },
                                "output_dir": {
                                    "type": "string",
                                    "description": "Optional run output directory for remediation notes and state",
                                },
                                "run_id": {
                                    "type": "string",
                                    "description": "Optional run id for traceability",
                                },
                                "stage_id": {
                                    "type": "string",
                                    "description": "Optional stage id for traceability",
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
        except Exception as exc:
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
