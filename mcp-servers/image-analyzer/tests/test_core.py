"""Unit tests for image-analyzer core logic."""

import sys
from pathlib import Path

import pytest

# Add parent directory so we can import core and schemas directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import load_and_analyze
from schemas import LoadAnalyzeResult, ScreenshotRef


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_load_two_pngs_and_one_md(fixtures_path: Path) -> None:
    """Directory with 2 PNGs + 1 .md should return 3 ScreenshotRefs."""
    result = load_and_analyze(fixtures_path)

    assert isinstance(result, LoadAnalyzeResult)
    assert len(result.screenshots) == 3

    ids = [ref.id for ref in result.screenshots]
    assert ids == ["S-001", "S-002", "S-003"]

    for ref in result.screenshots:
        assert isinstance(ref, ScreenshotRef)
        assert ref.id.startswith("S-")
        assert Path(ref.path).exists()
        assert ref.flow is None  # M1: always None


def test_image_analysis_found_count(fixtures_path: Path) -> None:
    """image_analysis.found_count must equal the number of refs returned."""
    result = load_and_analyze(fixtures_path)

    assert result.image_analysis["found_count"] == len(result.screenshots)
    assert result.image_analysis["mode"] == "stub"
    assert len(result.image_analysis["paths"]) == len(result.screenshots)


def test_empty_dir_returns_zero(empty_dir: Path) -> None:
    """Empty directory should return empty list and found_count == 0."""
    result = load_and_analyze(empty_dir)

    assert result.screenshots == []
    assert result.image_analysis["found_count"] == 0
    assert result.image_analysis["paths"] == []
    assert result.image_analysis["mode"] == "stub"


def test_md_file_description_contains_first_200_chars(fixtures_path: Path) -> None:
    """ScreenshotRef for a .md file must have description with first 200 chars."""
    result = load_and_analyze(fixtures_path)

    md_refs = [r for r in result.screenshots if r.path.endswith(".md")]
    assert len(md_refs) == 1, "Expected exactly one .md ScreenshotRef"

    ref = md_refs[0]
    assert ref.description is not None
    assert len(ref.description) <= 200

    # Verify content matches the actual file start
    actual_content = Path(ref.path).read_text(encoding="utf-8")
    assert ref.description == actual_content[:200]


def test_png_files_have_no_description(fixtures_path: Path) -> None:
    """ScreenshotRefs for image files should have description == None."""
    result = load_and_analyze(fixtures_path)

    image_refs = [r for r in result.screenshots if not r.path.endswith(".md")]
    assert len(image_refs) == 2

    for ref in image_refs:
        assert ref.description is None


def test_paths_are_absolute(fixtures_path: Path) -> None:
    """All ScreenshotRef.path values must be absolute paths."""
    result = load_and_analyze(fixtures_path)

    for ref in result.screenshots:
        assert Path(ref.path).is_absolute(), f"Expected absolute path, got: {ref.path}"


def test_task_checklist_lite_ignored(fixtures_path: Path) -> None:
    """Passing task_checklist_lite should not change the result (M1 stub)."""
    result_without = load_and_analyze(fixtures_path)
    result_with = load_and_analyze(fixtures_path, task_checklist_lite="T-001: Login flow")

    assert result_without.image_analysis["found_count"] == result_with.image_analysis["found_count"]
    assert [r.id for r in result_without.screenshots] == [r.id for r in result_with.screenshots]


# ---------------------------------------------------------------------------
# Error-path tests
# ---------------------------------------------------------------------------


def test_nonexistent_dir_raises_file_not_found() -> None:
    """Non-existent directory should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_and_analyze(Path("/nonexistent/screenshots/dir"))


def test_file_path_raises_not_a_directory(tmp_path: Path) -> None:
    """Passing a file path instead of a directory should raise NotADirectoryError."""
    f = tmp_path / "not_a_dir.txt"
    f.write_text("hello")

    with pytest.raises(NotADirectoryError):
        load_and_analyze(f)


# ---------------------------------------------------------------------------
# Ordering test
# ---------------------------------------------------------------------------


def test_refs_are_sorted_by_filename(fixtures_path: Path) -> None:
    """ScreenshotRefs should be sorted alphabetically by filename."""
    result = load_and_analyze(fixtures_path)

    names = [Path(r.path).name for r in result.screenshots]
    assert names == sorted(names), f"Expected sorted filenames, got: {names}"
