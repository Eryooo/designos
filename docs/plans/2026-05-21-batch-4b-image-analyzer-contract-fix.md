# Batch 4B — Image Analyzer Contract Fix

## Scope

- Replace the `image-analyzer` M1 stub with an honest production-safe evidence tool.
- Align UXEval Stage 5b / 5.5 / 6 to the real analyzer contract.
- Do not add OCR, multimodal semantic understanding, or new MCP services.

## Decision

This batch chooses **Option B: honest metadata/inventory analyzer**.

Implemented capabilities:
- recursive discovery of screenshots and markdown description files
- stable ids, relative paths, absolute paths
- file format, file size, pixel width/height, resolution tier
- markdown description preview extraction
- filename / markdown-text risk signals

Explicit non-capabilities:
- no OCR
- no semantic screenshot understanding
- no UI element extraction
- no task/module matching from image pixels
- no pixel-level sensitive-content detection

## Runtime Contract

`load_and_analyze()` now returns:

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
    }
  ],
  "image_analysis": {
    "analyzer_kind": "metadata_inventory",
    "capabilities": ["recursive screenshot and markdown description discovery"],
    "limitations": ["no OCR text extraction from image pixels"],
    "confidence": "high",
    "semantic_analysis_available": false,
    "ocr_available": false,
    "summary": {
      "total_files": 1,
      "image_count": 1,
      "description_count": 0,
      "low_resolution_count": 0,
      "signal_warning_count": 0,
      "low_resolution_ids": [],
      "signal_warning_ids": []
    }
  }
}
```

## UXEval Downstream Alignment

- Stage 5b is now documented as evidence inventory, not semantic screenshot analysis.
- Stage 5.5 conflict analysis can only rely on filenames, markdown previews, and analyzer limitations.
- Stage 6 must move unsupported client-mode inferences into `unverified_issues` / `[证据不足]` instead of fabricating page semantics.
- Constitution now reflects that sensitive-content checks are file-level hints only unless a human reviews the screenshots.

## Validation

- `mcp-servers/image-analyzer/tests/test_core.py`
- `skills/uxeval/tests/test_frontmatter_runtime.py`
- `skills/uxeval/tests/test_pipeline_integration.py`
- `tests/integration/test_kernel_mcp_integration.py`
