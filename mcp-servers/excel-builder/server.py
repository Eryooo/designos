"""MCP stdio server for Excel report generation.

Exposes the build_issue_report tool to DesignOS kernel.
"""

import asyncio
import json
from typing import Any

from core import ExcelBuilderError, audit_delivery_readiness, build_issue_report
from mcp.server import Server  # type: ignore[import-not-found]
from mcp.server.stdio import stdio_server  # type: ignore[import-not-found]
from mcp.types import TextContent, Tool  # type: ignore[import-not-found]

app = Server("excel-builder")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="build_issue_report",
            description="Build issue_report/html_report/evidence_pack artifacts from a list of issues.",
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
                        "description": "Optional absolute path where the Excel workbook should be written",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Optional output directory used to derive stable artifact paths",
                    },
                    "template": {
                        "type": "string",
                        "enum": ["uxeval", "design-acceptance", "competitor"],
                        "description": "Report template name",
                    },
                    "journey_map": {
                        "description": "Optional journey map payload included in html/evidence outputs",
                    },
                    "principles": {
                        "description": "Optional principles payload included in html/evidence outputs",
                    },
                },
                "required": ["issues"],
            },
        ),
        Tool(
            name="audit_delivery_readiness",
            description="Deterministically audit final-delivery readiness and write a bounded fallback package.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issues": {
                        "type": "array",
                        "description": "Stage 6 main issue list serialized as dicts",
                        "items": {"type": "object"},
                    },
                    "unverified_issues": {
                        "type": "array",
                        "description": "Stage 6 unverified issues bucket",
                        "items": {"type": "object"},
                    },
                    "evidence_assessment": {
                        "type": "object",
                        "description": "Runtime evidence assessment from image-analyzer",
                    },
                    "delivery_assessment": {
                        "type": "object",
                        "description": "Optional Stage 6 self-reported delivery assessment for comparison only",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Absolute run output directory used to write the audit bundle",
                    },
                },
                "required": ["issues", "unverified_issues", "evidence_assessment", "output_dir"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    if name not in {"build_issue_report", "audit_delivery_readiness"}:
        raise ValueError(f"Unknown tool: {name}")

    try:
        if name == "build_issue_report":
            result = build_issue_report(
                issues=arguments["issues"],
                output_path=arguments.get("output_path"),
                output_dir=arguments.get("output_dir"),
                template=arguments.get("template", "uxeval"),
                journey_map=arguments.get("journey_map"),
                principles=arguments.get("principles"),
            )
        else:
            result = audit_delivery_readiness(
                issues=arguments.get("issues", []),
                unverified_issues=arguments.get("unverified_issues", []),
                evidence_assessment=arguments.get("evidence_assessment", {}),
                delivery_assessment=arguments.get("delivery_assessment", {}),
                output_dir=arguments["output_dir"],
                run_id=arguments.get("run_id"),
                skill_name=arguments.get("skill_name"),
                skill_version=arguments.get("skill_version"),
                stage_id=arguments.get("stage_id"),
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
