"""Frontmatter sanity tests for the scaffolded skill."""

from __future__ import annotations

from pathlib import Path

from kernel.skill_loader import parse_frontmatter


def test_skill_md_has_required_top_level_keys(skill_dir: Path) -> None:
    fm, _body = parse_frontmatter(skill_dir / "SKILL.md")
    for key in ("name", "version", "type", "requires", "outputs"):
        assert key in fm, f"SKILL.md missing key: {key}"


def test_skill_md_declares_kernel_range(skill_dir: Path) -> None:
    fm, _body = parse_frontmatter(skill_dir / "SKILL.md")
    requires = fm.get("requires") or {}
    assert isinstance(requires, dict)
    assert str(requires.get("kernel", "")).startswith(">=")
