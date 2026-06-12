"""MCP stdio server for frontend-codegen.

Exposes 4 tools (fetch_dsl / extract_tokens / map_components / generate_code)
to DesignOS kernel. Currently MOCK — see core.py for status.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from core import (
    extract_tokens as core_extract_tokens,
)
from core import (
    fetch_dsl as core_fetch_dsl,
)
from core import (
    generate_code as core_generate_code,
)
from core import (
    map_components as core_map_components,
)
from mcp.server import Server  # type: ignore[import-not-found]
from mcp.server.stdio import stdio_server  # type: ignore[import-not-found]
from mcp.types import TextContent, Tool  # type: ignore[import-not-found]
from pydantic import ValidationError
from schemas import (
    DSLFetchRequest,
    ExtractTokensRequest,
    GenerateCodeRequest,
    MapComponentsRequest,
)

SERVER_NAME = "designos-frontend-codegen"


_FETCH_DSL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["source", "file_id"],
    "properties": {
        "source": {"type": "string", "enum": ["figma", "mastergo"]},
        "file_id": {"type": "string"},
        "access_token": {"type": ["string", "null"]},
    },
}

_EXTRACT_TOKENS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["dsl"],
    "properties": {
        "dsl": {"type": "object"},
        "design_md_path": {"type": ["string", "null"]},
    },
}

_MAP_COMPONENTS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["dsl", "component_lib"],
    "properties": {
        "dsl": {"type": "object"},
        "component_lib": {
            "type": "string",
            "enum": ["antd-vue", "element-plus", "antd-react", "custom"],
        },
    },
}

_GENERATE_CODE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["mode", "output_dir"],
    "properties": {
        "mode": {"type": "string", "enum": ["pm", "designer-spec", "designer-dsl"]},
        "dsl": {"type": ["object", "null"]},
        "tokens": {"type": ["object", "null"]},
        "component_mapping": {"type": ["object", "null"]},
        "framework": {"type": "string", "enum": ["react", "vue"]},
        "output_dir": {"type": "string"},
    },
}


def _serialise(payload: Any) -> str:
    return json.dumps(payload.model_dump(mode="json"), ensure_ascii=False, indent=2)


def build_server() -> Server:
    """Construct the MCP server with the 4 tools registered."""

    server: Server = Server(SERVER_NAME)

    @server.list_tools()  # type: ignore[misc]
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="fetch_dsl",
                description=(
                    "Fetch standardized DSL from Figma or MasterGo. "
                    "MOCK: returns a fixed login-screen DSL."
                ),
                inputSchema=_FETCH_DSL_SCHEMA,
            ),
            Tool(
                name="extract_tokens",
                description=(
                    "Extract Design Tokens (colors / typography / spacing / radius / shadow) "
                    "from DSL + design.md. MOCK: returns fixed tokens."
                ),
                inputSchema=_EXTRACT_TOKENS_SCHEMA,
            ),
            Tool(
                name="map_components",
                description=(
                    "Map DSL nodes to a component library (antd-vue / element-plus / "
                    "antd-react / custom). MOCK: simple type-based mapping."
                ),
                inputSchema=_MAP_COMPONENTS_SCHEMA,
            ),
            Tool(
                name="generate_code",
                description=(
                    "Generate a runnable frontend project at output_dir. "
                    "Per CONTRACT, mode controls fidelity: pm = low, designer-spec = mid, "
                    "designer-dsl = high. MOCK: writes a tiny but runnable React/Vue skeleton."
                ),
                inputSchema=_GENERATE_CODE_SCHEMA,
            ),
        ]

    @server.call_tool()  # type: ignore[misc]
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        try:
            if name == "fetch_dsl":
                req = DSLFetchRequest.model_validate(arguments)
                result = core_fetch_dsl(req)
            elif name == "extract_tokens":
                req = ExtractTokensRequest.model_validate(arguments)
                result = core_extract_tokens(req)
            elif name == "map_components":
                req = MapComponentsRequest.model_validate(arguments)
                result = core_map_components(req)
            elif name == "generate_code":
                req = GenerateCodeRequest.model_validate(arguments)
                result = core_generate_code(req)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except ValidationError as exc:
            return [TextContent(type="text", text=f"VALIDATION_ERROR: {exc}")]
        return [TextContent(type="text", text=_serialise(result))]

    return server


async def _serve() -> None:
    server = build_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    asyncio.run(_serve())


if __name__ == "__main__":  # pragma: no cover
    main()
