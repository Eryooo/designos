"""Preflight probe for local OCR capability used by image-analyzer."""

from __future__ import annotations

import json
import sys

from ocr_runtime import probe_ocr_backend


def main() -> int:
    result = probe_ocr_backend()
    payload = {
        "available": result.available,
        "backend": result.backend,
        "error": result.error,
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if result.available else 1


if __name__ == "__main__":
    sys.exit(main())
