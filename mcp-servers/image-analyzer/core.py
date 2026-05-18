"""Core logic for image-analyzer (pure functions, no MCP dependencies).

M1 stub implementation: enumerates screenshot and description files in a
directory and wraps them as ScreenshotRef objects. No actual vision analysis
is performed — downstream heuristic-detection uses the LLM to inspect the
files directly.
"""

from pathlib import Path
from typing import Any

from schemas import LoadAnalyzeResult, ScreenshotRef

# File extensions treated as real screenshots
_IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"})

# File extensions treated as screenshot description documents
_DESCRIPTION_EXTENSIONS = frozenset({".md"})

# Maximum characters to include in ScreenshotRef.description
_DESCRIPTION_PREVIEW_CHARS = 200


def _make_id(index: int) -> str:
    """Return a zero-padded screenshot identifier like 'S-001'."""
    return f"S-{index:03d}"


def _collect_files(screenshots_dir: Path) -> list[Path]:
    """Return all image and description files in *screenshots_dir*, sorted.

    Only the immediate directory is scanned (non-recursive) to keep the
    contract simple for M1.

    Args:
        screenshots_dir: Directory to scan.

    Returns:
        Sorted list of matching file paths.

    Raises:
        FileNotFoundError: If *screenshots_dir* does not exist.
        NotADirectoryError: If *screenshots_dir* is not a directory.
    """
    if not screenshots_dir.exists():
        raise FileNotFoundError(f"screenshots_dir not found: {screenshots_dir}")
    if not screenshots_dir.is_dir():
        raise NotADirectoryError(f"screenshots_dir is not a directory: {screenshots_dir}")

    accepted = _IMAGE_EXTENSIONS | _DESCRIPTION_EXTENSIONS
    files = [
        p for p in screenshots_dir.iterdir()
        if p.is_file() and p.suffix.lower() in accepted
    ]
    return sorted(files, key=lambda p: p.name)


def _build_ref(index: int, path: Path) -> ScreenshotRef:
    """Build a ScreenshotRef for a single file.

    For .md files the first _DESCRIPTION_PREVIEW_CHARS characters of the
    file content are stored in the description field.

    Args:
        index: 1-based position used to generate the stable id.
        path: Absolute path to the file.

    Returns:
        Populated ScreenshotRef.
    """
    description: str | None = None
    if path.suffix.lower() in _DESCRIPTION_EXTENSIONS:
        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
            description = raw[:_DESCRIPTION_PREVIEW_CHARS]
        except OSError:
            description = None

    return ScreenshotRef(
        id=_make_id(index),
        path=str(path.resolve()),
        flow=None,
        description=description,
    )


def load_and_analyze(
    screenshots_dir: Path,
    task_checklist_lite: str | None = None,  # noqa: ARG001 — reserved for M2
) -> LoadAnalyzeResult:
    """Load all screenshots/description files and return stub analysis.

    Supports:
    - .png, .jpg, .jpeg, .webp, .gif, .bmp  → real screenshot files
    - .md (e.g. screens-description.md)      → text description (virtual screenshot)

    M1 stub: no vision analysis is performed. The downstream
    heuristic-detection stage uses the LLM to inspect files directly.

    Args:
        screenshots_dir: Directory containing screenshots or description files.
        task_checklist_lite: Lite task checklist string (reserved for M2).

    Returns:
        LoadAnalyzeResult with screenshots list and stub image_analysis dict.

    Raises:
        FileNotFoundError: If screenshots_dir does not exist.
        NotADirectoryError: If screenshots_dir is not a directory.
    """
    files = _collect_files(screenshots_dir)

    refs: list[ScreenshotRef] = [
        _build_ref(i + 1, f) for i, f in enumerate(files)
    ]

    analysis: dict[str, Any] = {
        "found_count": len(refs),
        "paths": [r.path for r in refs],
        "mode": "stub",
    }

    return LoadAnalyzeResult(screenshots=refs, image_analysis=analysis)
