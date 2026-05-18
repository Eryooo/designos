"""MCP stdio server for Excel report generation.

Exposes the build_issue_report tool to DesignOS kernel.
"""

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from core import build_issue_report, ExcelBuilderError


app = Server("excel-builder")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="build_issue_report",
            description="Build an Excel report from a list of issues. Supports templates: uxeval, design-acceptance, competitor.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issues": {
                        "type": "array",
                        "description": "List of Issue objects serialized as dicts",
                        "items": {"type": "object"},
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Absolute path where the Excel file should be written",
                    },
                    "template": {
                        "type": "string",
                        "enum": ["uxeval", "design-acceptance", "competitor"],
                        "description": "Report template name",
                    },
                },
                "required": ["issues", "output_path", "template"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    if name != "build_issue_report":
        raise ValueError(f"Unknown tool: {name}")

    try:
        result = build_issue_report(
            issues=arguments["issues"],
            output_path=arguments["output_path"],
            template=arguments["template"],
        )
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
    except ExcelBuilderError as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=json.dumps({"error": f"Unexpected error: {str(e)}"}, ensure_ascii=False),
            )
        ]


async def main() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
