# PDF Parser MCP Server

MCP Server for parsing PDF documents with section extraction, metadata, and raw text.

## Features

- Extract structured sections from PDF documents
- Heuristic-based section detection (numbered sections, Chinese chapters, etc.)
- Extract PDF metadata (page count, title, author)
- Full raw text extraction
- Error handling for scanned PDFs (no text layer)

## Installation

```bash
cd mcp-servers/pdf-parser
pip install -e .
```

## Usage

### As MCP Server

Run as stdio server:

```bash
designos-pdf-parser
```

### As Python Module

```python
from pathlib import Path
from core import parse_pdf

result = parse_pdf(Path("document.pdf"))

print(f"Pages: {result.metadata.page_count}")
print(f"Sections: {len(result.sections)}")

for section in result.sections:
    print(f"{section.title} (page {section.page})")
    print(section.content[:100])
```

## MCP Tool Interface

### `parse_pdf`

Parse a PDF file and extract structured content.

**Input:**
```json
{
  "path": "/path/to/document.pdf"
}
```

**Output:**
```json
{
  "sections": [
    {
      "title": "1. Introduction",
      "content": "Full section text...",
      "page": 1
    }
  ],
  "metadata": {
    "page_count": 10,
    "title": "Document Title",
    "author": "Author Name"
  },
  "raw_text": "Complete document text..."
}
```

**Errors:**
- `file_not_found`: File does not exist
- `parse_error`: PDF has no text layer (scanned document) or invalid format
- `invalid_params`: Missing required parameter

## Section Detection Heuristics

The parser uses multiple heuristics to identify section headings:

1. **Numbered sections**: `1.`, `1.1.`, `1.1.1.`
2. **Chinese chapters**: `第一章`, `第二节`
3. **Chinese numerals**: `一、`, `二、`
4. **All-caps short lines**: `INTRODUCTION`
5. **Font size** (when available): Larger fonts indicate headings

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Generate test fixtures
python tests/fixtures/generate.py
```

## Dependencies

- `mcp>=1.0`: MCP protocol implementation
- `pdfplumber>=0.11`: PDF text extraction
- `pydantic>=2.0`: Data validation

## Architecture

- `core.py`: Pure functions for PDF parsing (no MCP dependencies)
- `schemas.py`: Pydantic models for data structures
- `server.py`: MCP stdio server implementation
- `tests/`: Unit tests with generated fixtures

## Known Limitations

- Scanned PDFs (image-only, no text layer) will raise `PdfParseError`
- Section detection is heuristic-based and may not work for all document formats
- Complex multi-column layouts may not be parsed correctly
- Performance: ~30s for 100-page documents (depends on document complexity)

## License

Apache 2.0
