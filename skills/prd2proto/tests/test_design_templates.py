"""Validation tests for the prd2proto design templates library.

These tests verify that all 8 design.md templates and the README index
follow the Google Labs design.md spec and the format documented in
`reference/design-templates/README.md`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable

import pytest
import yaml

TEMPLATES_DIR: Path = (
    Path(__file__).resolve().parent.parent / "reference" / "design-templates"
)

EXPECTED_TEMPLATE_NAMES: list[str] = [
    "stripe",
    "linear",
    "vercel",
    "notion",
    "coze",
    "antd-pro",
    "apple-hig",
    "arco",
]

REQUIRED_TOKEN_GROUPS: list[str] = [
    "colors",
    "typography",
    "spacing",
    "rounded",
    "components",
]

FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(?P<frontmatter>.*?)\n---\s*\n(?P<body>.*)$",
    re.DOTALL,
)


def _template_paths() -> list[Path]:
    return [TEMPLATES_DIR / f"{name}.md" for name in EXPECTED_TEMPLATE_NAMES]


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a markdown file with YAML frontmatter into (data, body).

    Raises AssertionError if the file does not contain valid frontmatter.
    """
    match = FRONTMATTER_PATTERN.match(text)
    assert match is not None, "missing YAML frontmatter delimited by '---'"
    raw = match.group("frontmatter")
    body = match.group("body")
    data = yaml.safe_load(raw)
    assert isinstance(data, dict), "frontmatter must parse to a YAML mapping"
    return data, body


def _walk_strings(value: Any) -> Iterable[str]:
    """Yield every string scalar contained in a nested dict/list."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for inner in value.values():
            yield from _walk_strings(inner)
    elif isinstance(value, list):
        for inner in value:
            yield from _walk_strings(inner)


def _resolve_token_path(data: dict[str, Any], dotted: str) -> Any:
    """Look up `colors.primary` style references inside the frontmatter.

    Returns the resolved value or raises KeyError.
    """
    cursor: Any = data
    for part in dotted.split("."):
        if not isinstance(cursor, dict) or part not in cursor:
            raise KeyError(dotted)
        cursor = cursor[part]
    return cursor


# ---------- Tests ----------


def test_all_templates_exist() -> None:
    """All 8 templates and the README index file must exist on disk."""
    assert TEMPLATES_DIR.is_dir(), f"missing templates dir: {TEMPLATES_DIR}"
    readme = TEMPLATES_DIR / "README.md"
    assert readme.exists(), "README.md index is missing"
    for path in _template_paths():
        assert path.exists(), f"template missing: {path.name}"


@pytest.mark.parametrize("template_name", EXPECTED_TEMPLATE_NAMES)
def test_each_template_has_valid_yaml_frontmatter(template_name: str) -> None:
    path = TEMPLATES_DIR / f"{template_name}.md"
    text = path.read_text(encoding="utf-8")
    data, _ = _split_frontmatter(text)
    assert data.get("version") == "alpha", "version must be 'alpha'"
    assert isinstance(data.get("name"), str) and data["name"], "name required"
    assert (
        isinstance(data.get("description"), str) and data["description"]
    ), "description required"


@pytest.mark.parametrize("template_name", EXPECTED_TEMPLATE_NAMES)
def test_each_template_declares_required_token_groups(template_name: str) -> None:
    path = TEMPLATES_DIR / f"{template_name}.md"
    data, _ = _split_frontmatter(path.read_text(encoding="utf-8"))
    for group in REQUIRED_TOKEN_GROUPS:
        assert group in data, f"{template_name}: missing token group `{group}`"
        assert isinstance(
            data[group], dict
        ), f"{template_name}: `{group}` must be a mapping"
        assert data[group], f"{template_name}: `{group}` must not be empty"


@pytest.mark.parametrize("template_name", EXPECTED_TEMPLATE_NAMES)
def test_each_template_uses_token_references_correctly(template_name: str) -> None:
    """Every `{group.key}` reference inside `components` must resolve."""
    path = TEMPLATES_DIR / f"{template_name}.md"
    data, _ = _split_frontmatter(path.read_text(encoding="utf-8"))
    components = data["components"]
    reference_re = re.compile(r"\{([a-zA-Z0-9_\-]+(?:\.[a-zA-Z0-9_\-]+)+)\}")
    seen_references = 0
    for value in _walk_strings(components):
        for ref in reference_re.findall(value):
            seen_references += 1
            try:
                _resolve_token_path(data, ref)
            except KeyError:
                pytest.fail(
                    f"{template_name}: dangling token reference `{{{ref}}}` "
                    f"inside components"
                )
    assert seen_references > 0, (
        f"{template_name}: components should reference token paths via "
        f"`{{group.key}}`"
    )


@pytest.mark.parametrize("template_name", EXPECTED_TEMPLATE_NAMES)
def test_each_template_has_design_philosophy_section(template_name: str) -> None:
    path = TEMPLATES_DIR / f"{template_name}.md"
    _, body = _split_frontmatter(path.read_text(encoding="utf-8"))
    assert "## Design Philosophy" in body, "missing top-level Design Philosophy"
    for sub in ("### Overall Vibe", "### When to Use", "### Usage Guidelines"):
        assert sub in body, f"missing required subsection `{sub}`"
    assert "**DO**" in body, "missing Do's list"
    assert "**DON'T**" in body, "missing Don'ts list"


def test_readme_lists_all_8_templates() -> None:
    readme_text = (TEMPLATES_DIR / "README.md").read_text(encoding="utf-8")
    for name in EXPECTED_TEMPLATE_NAMES:
        assert name in readme_text, f"README missing reference to `{name}`"
