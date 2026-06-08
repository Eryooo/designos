"""MCP server entry point for playwright-driver."""

from __future__ import annotations

import json
import sys
from typing import Any

from core import BrowserManager
from schemas import EvaluationScript, ScriptStep
from script_executor import ScriptExecutor

_browser = BrowserManager()


def handle_request(method: str, params: dict[str, Any] | None) -> dict[str, Any]:
    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "playwright-driver", "version": "0.1.0"},
        }
    if method == "tools/list":
        return {"tools": _tool_definitions()}
    if method == "tools/call":
        return _dispatch_tool(params or {})
    return {"error": {"code": "method_not_found", "message": f"Unknown: {method}"}}


def _dispatch_tool(params: dict[str, Any]) -> dict[str, Any]:
    name = params.get("name", "")
    args = params.get("arguments", {})
    try:
        result = _TOOL_HANDLERS[name](args)
        return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}
    except KeyError:
        return {"error": {"code": "tool_not_found", "message": f"Unknown tool: {name}"}}
    except Exception as exc:
        return {"error": {"code": "execution_error", "message": str(exc)}}


# --- Tool Handlers ---

def _handle_browser_launch(args: dict) -> dict:
    info = _browser.launch(
        url=args["url"],
        headless=args.get("headless", False),
        user_data_dir=args.get("user_data_dir"),
    )
    return info.model_dump()


def _handle_browser_close(args: dict) -> dict:
    _browser.close()
    return {"ok": True}


def _handle_navigate(args: dict) -> dict:
    state = _browser.navigate(args["url"])
    return state.model_dump()


def _handle_click(args: dict) -> dict:
    state = _browser.click(
        selector=args["selector"],
        selector_type=args.get("selector_type", "css"),
    )
    return state.model_dump()


def _handle_fill(args: dict) -> dict:
    state = _browser.fill(selector=args["selector"], value=args["value"])
    return state.model_dump()


def _handle_screenshot(args: dict) -> dict:
    path = _browser.screenshot(
        name=args["name"],
        full_page=args.get("full_page", True),
        output_dir=args.get("output_dir"),
    )
    return {"screenshot_path": path, "url": _browser._page.url}


def _handle_get_page_state(args: dict) -> dict:
    return _browser.get_page_state().model_dump()


def _handle_execute_script(args: dict) -> dict:
    script_data = args["script"]
    steps = [ScriptStep(**s) for s in script_data["steps"]]
    script = EvaluationScript(
        task_id=script_data["task_id"],
        task_title=script_data["task_title"],
        steps=steps,
    )
    executor = ScriptExecutor(_browser, output_dir=args.get("output_dir"))
    result = executor.execute(script)
    return result.model_dump()


def _handle_switch_page(args: dict) -> dict:
    state = _browser.switch_page(args.get("page_index", "last"))
    return state.model_dump()


def _handle_switch_frame(args: dict) -> dict:
    state = _browser.switch_frame(frame_selector=args.get("frame_selector"))
    return state.model_dump()


def _handle_extract_dom(args: dict) -> dict:
    return _browser.extract_dom(args.get("selector", "body"))


def _handle_execute_batch(args: dict) -> dict:
    """Execute multiple evaluation scripts in sequence, return combined results."""
    from heuristic_adapter import build_detection_request
    from retry_planner import RetryPlanner

    # Accept both formats: direct 'scripts' list or 'evaluation_script' from pipeline
    if "scripts" in args:
        scripts_data = args["scripts"]
    elif "evaluation_script" in args:
        raw = args["evaluation_script"]
        if isinstance(raw, str):
            raw = json.loads(raw)
        scripts_data = raw.get("evaluation_scripts", [])
    else:
        raise ValueError("Missing 'scripts' or 'evaluation_script' in arguments")

    output_dir = args.get("output_dir")
    max_retries = args.get("max_retries", 2)

    planner = RetryPlanner()
    all_results = []

    for script_data in scripts_data:
        steps = [ScriptStep(**s) for s in script_data["steps"]]
        script = EvaluationScript(
            task_id=script_data["task_id"],
            task_title=script_data["task_title"],
            steps=steps,
        )
        executor = ScriptExecutor(_browser, output_dir=output_dir)
        result = executor.execute(script)
        all_results.append(result)

        retries = 0
        while planner.needs_retry(result) and retries < max_retries:
            retry_script = planner.plan_retry(script, result)
            if retry_script is None:
                break
            result = executor.execute(retry_script)
            all_results.append(result)
            retries += 1

    detection_request = build_detection_request(all_results)

    total_steps = sum(r.steps_total for r in all_results)
    total_succeeded = sum(r.steps_succeeded for r in all_results)

    screenshots = detection_request.get("screenshots", [])
    dom_data = detection_request.get("dom_data")

    return {
        "execution_summary": {
            "tasks_executed": len(scripts_data),
            "total_results": len(all_results),
            "steps_total": total_steps,
            "steps_succeeded": total_succeeded,
            "steps_failed": total_steps - total_succeeded,
            "coverage_pct": round(total_succeeded / total_steps * 100, 1) if total_steps else 0,
        },
        "screenshots": screenshots,
        "dom_data": dom_data,
        "detection_request": detection_request,
        "results": [r.model_dump() for r in all_results],
    }


_TOOL_HANDLERS = {
    "browser_launch": _handle_browser_launch,
    "browser_close": _handle_browser_close,
    "navigate": _handle_navigate,
    "click_element": _handle_click,
    "fill_input": _handle_fill,
    "capture_screenshot": _handle_screenshot,
    "get_page_state": _handle_get_page_state,
    "execute_script": _handle_execute_script,
    "execute_batch": _handle_execute_batch,
    "switch_page": _handle_switch_page,
    "switch_frame": _handle_switch_frame,
    "extract_dom": _handle_extract_dom,
}


# --- Tool Definitions ---

def _tool_definitions() -> list[dict]:
    return [
        {
            "name": "browser_launch",
            "description": "Launch browser and navigate to URL. Uses persistent context for login state.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Initial URL"},
                    "headless": {"type": "boolean", "default": False},
                    "user_data_dir": {"type": "string", "description": "Path for persistent login state"},
                },
                "required": ["url"],
            },
        },
        {
            "name": "browser_close",
            "description": "Close the browser session.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "navigate",
            "description": "Navigate to a URL.",
            "inputSchema": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
        {
            "name": "click_element",
            "description": "Click an element by CSS selector, text, or role.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string"},
                    "selector_type": {"type": "string", "enum": ["css", "text", "role"], "default": "css"},
                },
                "required": ["selector"],
            },
        },
        {
            "name": "fill_input",
            "description": "Fill a form input.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["selector", "value"],
            },
        },
        {
            "name": "capture_screenshot",
            "description": "Take a screenshot of the current page.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Screenshot filename (without .png)"},
                    "full_page": {"type": "boolean", "default": True},
                    "output_dir": {"type": "string"},
                },
                "required": ["name"],
            },
        },
        {
            "name": "get_page_state",
            "description": "Get current page state (URL, title, visible text).",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "execute_script",
            "description": "Execute a complete JSON evaluation script and return evidence bundle.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "script": {"type": "object", "description": "EvaluationScript JSON"},
                    "output_dir": {"type": "string"},
                },
                "required": ["script"],
            },
        },
        {
            "name": "switch_page",
            "description": "Switch to a different browser tab.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "page_index": {"description": "Tab index or 'last'"},
                },
            },
        },
        {
            "name": "switch_frame",
            "description": "Switch to an iframe.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "frame_selector": {"type": "string", "description": "URL substring to match frame"},
                },
            },
        },
        {
            "name": "extract_dom",
            "description": "Extract DOM structure for heuristic analysis.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "default": "body"},
                },
            },
        },
        {
            "name": "execute_batch",
            "description": "Execute multiple evaluation scripts with auto-retry, return combined evidence + detection request.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scripts": {"type": "array", "items": {"type": "object"}, "description": "List of EvaluationScript JSON objects"},
                    "output_dir": {"type": "string"},
                    "max_retries": {"type": "integer", "default": 2},
                },
                "required": ["scripts"],
            },
        },
    ]


# --- Main Loop ---

def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = request.get("method", "")
        params = request.get("params")
        req_id = request.get("id")

        response = handle_request(method, params)

        if "error" in response:
            output = {"jsonrpc": "2.0", "id": req_id, "error": response["error"]}
        else:
            output = {"jsonrpc": "2.0", "id": req_id, "result": response}

        sys.stdout.write(json.dumps(output, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
