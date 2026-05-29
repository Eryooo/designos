"""Tests for tools.validate — skill validation against archetype specs.

Per CONTRACT §3.C:
- validate_uxeval_pass = 必过
- validate_catches_known_violations >= 6 种违规场景

Per CONTRACT §3.E:
- error_message_actionable_rate >= 90%
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest


def _add_factory_to_path() -> None:
    factory_dir = Path(__file__).resolve().parents[1]
    if str(factory_dir) not in sys.path:
        sys.path.insert(0, str(factory_dir))


def test_validate_uxeval_passes_evaluation_archetype() -> None:
    """CONTRACT §3.C: uxeval must pass validation against evaluation archetype."""
    _add_factory_to_path()
    from archetypes import load_archetype
    from tools.validate import Validator

    repo_root = Path(__file__).resolve().parents[2]
    uxeval_dir = repo_root / "skills" / "uxeval"
    assert uxeval_dir.exists(), f"uxeval not found at {uxeval_dir}"

    archetype = load_archetype("evaluation")
    validator = Validator(uxeval_dir, archetype)
    passed = validator.validate()

    if not passed:
        for v in validator.violations:
            print(f"  {v.dimension}: {v.message}")
            print(f"    fix: {v.fix}")

    assert passed, f"uxeval failed validation with {len(validator.violations)} violations"


def test_validate_kernel_loadability_check(tmp_path: Path) -> None:
    """Validator must catch skills that kernel cannot load."""
    _add_factory_to_path()
    from archetypes import load_archetype
    from tools.validate import Validator

    skill_dir = tmp_path / "broken-skill"
    skill_dir.mkdir()

    # Create invalid SKILL.md with broken YAML
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: broken
version: 1.0.0
type: pipeline
this is not valid yaml: [unclosed
---
"""
    )

    archetype = load_archetype("evaluation")
    validator = Validator(skill_dir, archetype)
    passed = validator.validate()

    assert not passed
    assert any(v.dimension == "kernel_loadability" for v in validator.violations)
    # Check actionable error message
    loadability_violations = [v for v in validator.violations if v.dimension == "kernel_loadability"]
    assert len(loadability_violations) > 0
    assert "fix" in loadability_violations[0].fix.lower() or "ensure" in loadability_violations[0].fix.lower()


def test_validate_catches_missing_skill_md(tmp_path: Path) -> None:
    """Validator must catch missing SKILL.md."""
    _add_factory_to_path()
    from archetypes import load_archetype
    from tools.validate import Validator

    skill_dir = tmp_path / "no-skill-md"
    skill_dir.mkdir()

    archetype = load_archetype("evaluation")
    validator = Validator(skill_dir, archetype)
    passed = validator.validate()

    assert not passed
    assert any(v.dimension == "frontmatter" and "SKILL.md is missing" in v.message for v in validator.violations)


def test_validate_catches_missing_pipeline_yaml(tmp_path: Path) -> None:
    """Validator must catch missing pipeline.yaml."""
    _add_factory_to_path()
    from archetypes import load_archetype
    from tools.validate import Validator

    skill_dir = tmp_path / "no-pipeline"
    skill_dir.mkdir()

    # Create valid SKILL.md but no pipeline.yaml
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        """---
name: test-skill
version: 1.0.0
type: pipeline
description: test
requires:
  kernel: ">=1.0.0,<2.0.0"
outputs:
  - id: issue_report
    type: issue_report
    format: xlsx
---
"""
    )

    archetype = load_archetype("evaluation")
    validator = Validator(skill_dir, archetype)
    passed = validator.validate()

    assert not passed
    # Should fail kernel_loadability or stage_slots check
    assert any("pipeline.yaml" in v.message for v in validator.violations)


def test_validate_catches_missing_constitution(tmp_path: Path) -> None:
    """Validator must catch missing constitution.md when required."""
    _add_factory_to_path()
    from archetypes import load_archetype
    from tools.validate import Validator

    repo_root = Path(__file__).resolve().parents[2]
    uxeval_dir = repo_root / "skills" / "uxeval"

    # Copy uxeval to tmp_path
    skill_dir = tmp_path / "no-constitution"
    shutil.copytree(uxeval_dir, skill_dir)

    # Remove constitution.md
    constitution = skill_dir / "constitution.md"
    if constitution.exists():
        constitution.unlink()

    archetype = load_archetype("evaluation")
    validator = Validator(skill_dir, archetype)
    passed = validator.validate()

    assert not passed
    assert any(
        v.dimension == "constitution" and "constitution.md is missing" in v.message
        for v in validator.violations
    )


def test_validate_catches_missing_required_outputs(tmp_path: Path) -> None:
    """Validator must catch missing required OutputTypes."""
    _add_factory_to_path()
    from archetypes import load_archetype
    from tools.validate import Validator

    repo_root = Path(__file__).resolve().parents[2]
    uxeval_dir = repo_root / "skills" / "uxeval"

    skill_dir = tmp_path / "missing-outputs"
    shutil.copytree(uxeval_dir, skill_dir)

    # Modify SKILL.md to remove issue_report output
    skill_md = skill_dir / "SKILL.md"
    content = skill_md.read_text()
    # Remove the issue_report output entry
    lines = content.split("\n")
    filtered = []
    skip_next = 0
    for line in lines:
        if skip_next > 0:
            skip_next -= 1
            continue
        if "id: issue_report" in line:
            skip_next = 2  # Skip this line and next 2 lines
            continue
        filtered.append(line)
    skill_md.write_text("\n".join(filtered))

    archetype = load_archetype("evaluation")
    validator = Validator(skill_dir, archetype)
    passed = validator.validate()

    assert not passed
    assert any(
        v.dimension == "outputs" and "issue_report" in v.message
        for v in validator.violations
    )


def test_validate_catches_missing_checkpoints(tmp_path: Path) -> None:
    """Validator must catch missing required checkpoints (C1/C2/C3)."""
    _add_factory_to_path()
    from archetypes import load_archetype
    from tools.validate import Validator

    repo_root = Path(__file__).resolve().parents[2]
    uxeval_dir = repo_root / "skills" / "uxeval"

    skill_dir = tmp_path / "missing-checkpoints"
    shutil.copytree(uxeval_dir, skill_dir)

    # Remove C1 checkpoint from pipeline.yaml
    pipeline_yaml = skill_dir / "pipeline.yaml"
    content = pipeline_yaml.read_text()
    # Remove checkpoint C1 block
    lines = content.split("\n")
    filtered = []
    in_checkpoint = False
    for line in lines:
        if "checkpoint:" in line:
            in_checkpoint = True
        if in_checkpoint:
            if "id: C1" in line:
                # Skip this checkpoint block
                continue
            if line.strip() and not line.startswith(" "):
                in_checkpoint = False
        if not in_checkpoint or "id: C1" not in line:
            filtered.append(line)

    # Simpler approach: just replace the C1 checkpoint id
    content = content.replace("id: C1", "id: CX")
    pipeline_yaml.write_text(content)

    archetype = load_archetype("evaluation")
    validator = Validator(skill_dir, archetype)
    passed = validator.validate()

    assert not passed
    assert any(
        v.dimension == "checkpoint_slots" and "C1" in v.message
        for v in validator.violations
    )


def test_validate_catches_missing_audit_gate(tmp_path: Path) -> None:
    """Validator must catch missing QG3 delivery audit gate."""
    _add_factory_to_path()
    from archetypes import load_archetype
    from tools.validate import Validator

    repo_root = Path(__file__).resolve().parents[2]
    uxeval_dir = repo_root / "skills" / "uxeval"

    skill_dir = tmp_path / "missing-gate"
    shutil.copytree(uxeval_dir, skill_dir)

    # Remove QG3 gate from pipeline.yaml
    pipeline_yaml = skill_dir / "pipeline.yaml"
    content = pipeline_yaml.read_text()
    content = content.replace("checkpoint_id: QG3", "checkpoint_id: QGX")
    pipeline_yaml.write_text(content)

    archetype = load_archetype("evaluation")
    validator = Validator(skill_dir, archetype)
    passed = validator.validate()

    assert not passed
    assert any(
        v.dimension == "gate_slots" and "QG3" in v.message
        for v in validator.violations
    )


def test_validate_error_messages_are_actionable(tmp_path: Path) -> None:
    """CONTRACT §3.E: error messages must be actionable (>= 90%)."""
    _add_factory_to_path()
    from archetypes import load_archetype
    from tools.validate import Validator

    # Create a skill with multiple violations
    skill_dir = tmp_path / "multi-violation"
    skill_dir.mkdir()

    # Missing SKILL.md
    archetype = load_archetype("evaluation")
    validator = Validator(skill_dir, archetype)
    validator.validate()

    # Check that all violations have actionable fix messages
    actionable_count = 0
    for v in validator.violations:
        # Actionable means: contains "Create", "Add", "Set", "Remove", "Fix", or similar action verbs
        fix_lower = v.fix.lower()
        if any(
            keyword in fix_lower
            for keyword in ["create", "add", "set", "remove", "fix", "ensure", "change", "install"]
        ):
            actionable_count += 1

    total = len(validator.violations)
    if total > 0:
        actionable_rate = actionable_count / total
        assert actionable_rate >= 0.9, (
            f"Only {actionable_count}/{total} ({actionable_rate:.1%}) "
            f"error messages are actionable, expected >= 90%"
        )


def test_validate_catches_missing_eval_layout(tmp_path: Path) -> None:
    """Validator must catch missing eval/golden, eval/failure, eval/promptfoo.yaml."""
    _add_factory_to_path()
    from archetypes import load_archetype
    from tools.validate import Validator

    repo_root = Path(__file__).resolve().parents[2]
    uxeval_dir = repo_root / "skills" / "uxeval"

    skill_dir = tmp_path / "missing-eval-layout"
    shutil.copytree(uxeval_dir, skill_dir)

    # Remove eval/golden
    golden_dir = skill_dir / "eval" / "golden"
    if golden_dir.exists():
        shutil.rmtree(golden_dir)

    archetype = load_archetype("evaluation")
    validator = Validator(skill_dir, archetype)
    passed = validator.validate()

    assert not passed
    assert any(
        v.dimension == "directory" and "eval/golden" in v.message
        for v in validator.violations
    )


def test_validate_cli_exit_codes(tmp_path: Path) -> None:
    """Test CLI exit codes: 0 = pass, 1 = fail, 2 = usage error."""
    _add_factory_to_path()
    import subprocess

    repo_root = Path(__file__).resolve().parents[2]
    uxeval_dir = repo_root / "skills" / "uxeval"
    factory_dir = Path(__file__).resolve().parents[1]

    # Test 0: uxeval should pass
    result = subprocess.run(
        [
            "python3",
            "-m",
            "tools.validate",
            str(uxeval_dir),
            "--archetype",
            "evaluation",
        ],
        cwd=factory_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"uxeval should pass, got: {result.stdout}\n{result.stderr}"

    # Test 1: non-existent skill should fail with exit code 2
    result = subprocess.run(
        [
            "python3",
            "-m",
            "tools.validate",
            str(tmp_path / "does-not-exist"),
            "--archetype",
            "evaluation",
        ],
        cwd=factory_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2

    # Test 2: broken skill should fail with exit code 1
    broken_dir = tmp_path / "broken"
    broken_dir.mkdir()
    result = subprocess.run(
        [
            "python3",
            "-m",
            "tools.validate",
            str(broken_dir),
            "--archetype",
            "evaluation",
        ],
        cwd=factory_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
