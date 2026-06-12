"""MCP stdio server entry point for the heuristic-engine.

Exposes a single tool ``detect`` that wraps :func:`core.detect`. The server
follows the same skeleton as ``mcp-servers/pdf-parser/server.py`` so kernel
side discovery is uniform.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from core import detect
from llm_judge import LLMJudge
from mcp.server import Server  # type: ignore[import-not-found]
from mcp.server.stdio import stdio_server  # type: ignore[import-not-found]
from mcp.types import TextContent, Tool  # type: ignore[import-not-found]
from principles_library import default_principles
from pydantic import ValidationError
from schemas import DetectionRequest, HeuristicPrinciple

SERVER_NAME = "designos-heuristic-engine"

# JSON-Schema served to MCP clients so they can validate inputs locally.
_DETECT_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["screenshots"],
    "properties": {
        "screenshots": {"type": "array", "minItems": 1},
        "principles": {"type": "array"},
        "task_checklist": {"type": "object"},
        "constitution": {"type": "string"},
        "mode": {"type": "string", "enum": ["web", "client"]},
        "dom_data": {"type": ["array", "null"]},
    },
}


def _build_request(payload: dict[str, Any]) -> DetectionRequest:
    """Coerce the raw tool payload into a :class:`DetectionRequest`.

    Falls back to the built-in principle catalogue when the caller does not
    pass any.
    """

    if "principles" not in payload or not payload["principles"]:
        payload = {**payload, "principles": [p.model_dump() for p in default_principles()]}
    elif isinstance(payload["principles"], list) and payload["principles"] and isinstance(
        payload["principles"][0], HeuristicPrinciple
    ):
        # Allow callers that already constructed Pydantic objects.
        payload = {**payload, "principles": [p.model_dump() for p in payload["principles"]]}
    return DetectionRequest.model_validate(payload)


def _serialise_result(result: Any) -> str:
    """Pretty-print the detection result as JSON for the MCP transport."""

    return json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2)


def build_server() -> Server:
    """Construct the MCP server with the ``detect`` tool registered."""

    server: Server = Server(SERVER_NAME)

    @server.list_tools()  # type: ignore[misc]
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="detect",
                description=(
                    "Run heuristic UX detection over screenshots: deterministic rules "
                    "plus an LLM vision judge constrained by the skill constitution."
                ),
                inputSchema=_DETECT_INPUT_SCHEMA,
            )
        ]

    @server.call_tool()  # type: ignore[misc]
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        if name != "detect":
            raise ValueError(f"Unknown tool: {name}")
        try:
            request = _build_request(arguments)
        except ValidationError as exc:
            return [TextContent(type="text", text=f"VALIDATION_ERROR: {exc}")]
        judge = LLMJudge()
        result = detect(request, judge=judge)
        return [TextContent(type="text", text=_serialise_result(result))]

    return server


async def _serve() -> None:
    """Start the stdio MCP server loop."""

    server = build_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    """Console-script entry point."""

    asyncio.run(_serve())


if __name__ == "__main__":  # pragma: no cover
    main()
