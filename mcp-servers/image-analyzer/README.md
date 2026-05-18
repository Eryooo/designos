# image-analyzer MCP Server (M1 Stub)

MCP stdio server that loads screenshots and description files from a directory
and returns a `ScreenshotRef` list for downstream heuristic analysis.

## M1 scope

No actual vision analysis is performed. The server enumerates files and wraps
them as `ScreenshotRef` objects. The downstream `heuristic-detection` stage
uses the LLM to inspect the files directly.

## Supported file types

| Extension | Treatment |
|-----------|-----------|
| `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.bmp` | Real screenshot |
| `.md` | Text description (virtual screenshot) |

## Tool: `load_and_analyze`

**Inputs**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `screenshots_dir` | string | yes | Absolute path to directory |
| `task_checklist_lite` | string | no | Reserved for M2, ignored in M1 |

**Output**

```json
{
  "screenshots": [
    {
      "id": "S-001",
      "path": "/abs/path/to/screen.png",
      "flow": null,
      "description": null
    },
    {
      "id": "S-002",
      "path": "/abs/path/to/screens-description.md",
      "flow": null,
      "description": "# Screen Description\n\nFirst 200 chars..."
    }
  ],
  "image_analysis": {
    "found_count": 2,
    "paths": ["/abs/path/to/screen.png", "/abs/path/to/screens-description.md"],
    "mode": "stub"
  }
}
```

## Running tests

```bash
cd mcp-servers/image-analyzer
python -m pytest tests/ -v
```

## Running the server

```bash
python server.py
```

The server reads JSON-RPC 2.0 messages from stdin and writes responses to stdout.
