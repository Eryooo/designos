"""Reference consistency tests for prd2proto skill.

Ensures:
- pipeline-referenced reference files exist
- reference files stay under size limit (avoid regressing into textbook material)
- textbook subdir (if present) only contains markdown
- 03a prompt mentions design-templates and outputs the new schema fields
"""

from __future__ import annotations

from pathlib import Path

import pytest

SKILL_DIR: Path = Path(__file__).resolve().parent.parent
REFERENCE_DIR: Path = SKILL_DIR / "reference"
PROMPTS_DIR: Path = SKILL_DIR / "prompts"
TEXTBOOK_DIR: Path = REFERENCE_DIR / "textbook"

# Conservative list — pipeline.yaml may reference any subset of these.
EXPECTED_REFERENCE_FILES = [
    "m01-prd-understanding.md",
    "m02-design-analysis.md",
    "m03a-spec-generation.md",
    "m04-token-extraction.md",
    "m05-code-generation.md",
    "m06-review-gate.md",
]

REFERENCE_LINE_LIMIT = 100


def test_all_referenced_files_exist() -> None:
    """Every reference file the pipeline may load must exist on disk."""
    missing = []
    for name in EXPECTED_REFERENCE_FILES:
        path = REFERENCE_DIR / name
        if not path.is_file():
            missing.append(str(path))
    assert not missing, f"Missing reference files: {missing}"


@pytest.mark.parametrize("name", EXPECTED_REFERENCE_FILES)
def test_reference_files_under_size_limit(name: str) -> None:
    """Each reference must stay under the line limit to avoid teaching-material bloat."""
    path = REFERENCE_DIR / name
    if not path.is_file():
        pytest.skip(f"{name} not present")
    line_count = sum(1 for _ in path.open("r", encoding="utf-8"))
    assert line_count <= REFERENCE_LINE_LIMIT, (
        f"{name} has {line_count} lines (limit {REFERENCE_LINE_LIMIT}). "
        f"Move teaching material to reference/textbook/."
    )


def test_textbook_optional_dir_does_not_break_anything() -> None:
    """If textbook/ exists, every file inside must be readable markdown."""
    if not TEXTBOOK_DIR.is_dir():
        pytest.skip("textbook/ subdirectory not present")
    md_files = list(TEXTBOOK_DIR.glob("*.md"))
    # No requirement on count, but if anything is there it should be .md
    non_md = [p for p in TEXTBOOK_DIR.iterdir() if p.is_file() and p.suffix != ".md"]
    assert not non_md, f"textbook/ contains non-markdown files: {non_md}"
    # Every md file must be readable and non-empty
    for path in md_files:
        content = path.read_text(encoding="utf-8")
        assert content.strip(), f"textbook/{path.name} is empty"


def test_03a_prompt_mentions_design_templates() -> None:
    """The new 03a prompt must mention design-templates so the template-selection logic is preserved."""
    prompt_path = PROMPTS_DIR / "03a-spec-generation.md"
    assert prompt_path.is_file(), f"Missing prompt: {prompt_path}"
    content = prompt_path.read_text(encoding="utf-8")
    assert "design-templates" in content, (
        "03a prompt must reference 'design-templates' "
        "(template-selection logic missing)."
    )


def test_03a_prompt_outputs_selected_template() -> None:
    """The 03a prompt's output schema must include the new fields."""
    prompt_path = PROMPTS_DIR / "03a-spec-generation.md"
    content = prompt_path.read_text(encoding="utf-8")
    required_fields = ["selected_template", "selection_reason", "adjustments"]
    missing = [f for f in required_fields if f not in content]
    assert not missing, (
        f"03a prompt schema missing required output fields: {missing}"
    )
