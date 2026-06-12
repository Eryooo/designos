# image-analyzer MCP Server

MCP stdio server that performs honest local screenshot inventory and metadata extraction.

## Real capability boundary

This server is **not** a semantic image analyzer.

It can do:
- recursive discovery of supported screenshot and markdown description files
- stable ids plus absolute and relative paths
- image format, file size, pixel width/height, and resolution tier
- markdown description previews
- filename / markdown-text risk signals

It cannot do:
- OCR from image pixels
- UI semantic understanding
- task/module matching from visuals
- pixel-level sensitive-content detection

## Supported file types

| Extension | Treatment |
|-----------|-----------|
| `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.bmp` | Raster screenshot with metadata extraction |
| `.md` | Description file with preview extraction |

## Tool: `load_and_analyze`

**Inputs**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `screenshots_dir` | string | yes | Absolute path to directory |
| `task_checklist_lite` | string | no | Reserved for future enrichments; currently ignored |

**Output**

```json
{
  "screenshots": [
    {
      "id": "S-001",
      "path": "/abs/path/to/screen.png",
      "relative_path": "flows/login/screen.png",
      "kind": "image",
      "format": "png",
      "file_size_bytes": 204800,
      "width": 1440,
      "height": 900,
      "resolution": "1440x900",
      "quality_tier": "high",
      "description_preview": null,
      "signal_warnings": []
    },
    {
      "id": "S-002",
      "path": "/abs/path/to/screens-description.md",
      "relative_path": "screens-description.md",
      "kind": "description",
      "format": "md",
      "file_size_bytes": 512,
      "width": null,
      "height": null,
      "resolution": null,
      "quality_tier": "not_applicable",
      "description_preview": "# Screen Description\n\nFirst 200 chars...",
      "signal_warnings": []
    }
  ],
  "image_analysis": {
    "analyzer_kind": "metadata_inventory",
    "capabilities": [
      "recursive screenshot and markdown description discovery",
      "stable ids with relative and absolute paths"
    ],
    "limitations": [
      "no OCR text extraction from image pixels",
      "no UI semantic understanding or scene labeling"
    ],
    "confidence": "high",
    "semantic_analysis_available": false,
    "ocr_available": false,
    "summary": {
      "total_files": 2,
      "image_count": 1,
      "description_count": 1,
      "low_resolution_count": 0,
      "signal_warning_count": 0,
      "low_resolution_ids": [],
      "signal_warning_ids": []
    }
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
