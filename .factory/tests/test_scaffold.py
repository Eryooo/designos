"""Tests for tools.scaffold — assemble kernel-loadable skill skeletons.

Per CONTRACT §3.A, the scaffold must hit three 100% rates on its output:

- ``scaffold_success_rate``       — passes :class:`Validator` straight away.
- ``scaffold_kernel_load_rate``   — kernel ``load_pipeline_skill`` accepts it.
- ``scaffold_preflight_pass_rate`` — ``PreflightChecker.check`` returns no errors.

Per CONTRACT §4 Gate 2, the scaffold also has to:

- create the archetype's required directories and files,
- pre-wire required checkpoints (C1/C2/C3) and audit gates (QG2/QG3),
- support ``--dry-run`` (no filesystem mutation), and
- refuse to overwrite an existing target unless ``--force`` is passed.

These tests exercise each of those guarantees against the evaluation archetype.
``conftest.py`` already adds ``.factory/`` and the repo root to ``sys.path``.
"""

from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from archetypes import load_archetype
from tools.scaffold import ScaffoldPlan, main, scaffold_skill

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
FACTORY_DIR: Path = Path(__file__).resolve().parents[1]


def _scaffold(tmp_path: Path, *, name: str = "demo-skill", **kwargs: object) -> ScaffoldPlan:
    """Materialise a scaffold skeleton in ``tmp_path`` and return the plan."""
    return scaffold_skill(
        archetype_name="evaluation",
        skill_name=name,
        output_dir=tmp_path,
        **kwargs,  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# 1. Directory + file structure conforms to archetype.directory.required_*
# ---------------------------------------------------------------------------


def test_scaffold_evaluation_creates_complete_directory(tmp_path: Path) -> None:
    plan = _scaffold(tmp_path)
    archetype = load_archetype("evaluation")

    assert plan.skill_dir.exists() and plan.skill_dir.is_dir()
    for rel_dir in archetype.directory.required_directories:
        target = plan.skill_dir / rel_dir
        assert target.is_dir(), f"missing required directory: {rel_dir}"
    for rel_file in archetype.directory.required_files:
        target = plan.skill_dir / rel_file
        assert target.is_file(), f"missing required file: {rel_file}"


# ---------------------------------------------------------------------------
# 2. Skeleton is kernel-loadable (CONTRACT §3.A scaffold_kernel_load_rate=100%)
# ---------------------------------------------------------------------------


def test_scaffold_evaluation_skill_md_is_kernel_loadable(tmp_path: Path) -> None:
    from kernel.skill_loader import load_pipeline_skill

    plan = _scaffold(tmp_path)
    skill = load_pipeline_skill(plan.skill_dir)

    assert skill.config.name == "demo-skill"
    assert skill.config.version
    assert skill.get_stages(), "scaffold produced an empty pipeline"


# ---------------------------------------------------------------------------
# 3. Required slot count is satisfied (>= number of required archetype slots)
# ---------------------------------------------------------------------------


def test_scaffold_evaluation_stages_match_archetype_slots(tmp_path: Path) -> None:
    plan = _scaffold(tmp_path)
    archetype = load_archetype("evaluation")
    pipeline = yaml.safe_load((plan.skill_dir / "pipeline.yaml").read_text(encoding="utf-8"))

    required_slots = [s for s in archetype.stage_slots if s.required]
    assert len(pipeline.get("stages", [])) >= len(required_slots), (
        f"pipeline has {len(pipeline.get('stages', []))} stages, "
        f"expected at least {len(required_slots)} required slots"
    )

    stage_ids = {s["id"] for s in pipeline["stages"]}
    for slot in required_slots:
        assert slot.slot_id in stage_ids, (
            f"required slot {slot.slot_id} missing from scaffold pipeline.yaml"
        )


# ---------------------------------------------------------------------------
# 4. Required checkpoints (C1/C2/C3) are pre-wired in pipeline.yaml
# ---------------------------------------------------------------------------


def test_scaffold_evaluation_checkpoints_present(tmp_path: Path) -> None:
    plan = _scaffold(tmp_path)
    archetype = load_archetype("evaluation")
    pipeline = yaml.safe_load((plan.skill_dir / "pipeline.yaml").read_text(encoding="utf-8"))

    found_checkpoints: set[str] = set()
    for stage in pipeline.get("stages", []):
        cp = stage.get("checkpoint")
        if isinstance(cp, dict) and cp.get("id"):
            found_checkpoints.add(str(cp["id"]))

    required_ids = {cp.checkpoint_id for cp in archetype.checkpoint_slots if cp.required}
    missing = required_ids - found_checkpoints
    assert not missing, f"scaffold missing required checkpoints: {sorted(missing)}"


# ---------------------------------------------------------------------------
# 5. Required quality gates (QG2/QG3) are pre-wired in pipeline.yaml
# ---------------------------------------------------------------------------


def test_scaffold_evaluation_gates_present(tmp_path: Path) -> None:
    plan = _scaffold(tmp_path)
    archetype = load_archetype("evaluation")
    pipeline = yaml.safe_load((plan.skill_dir / "pipeline.yaml").read_text(encoding="utf-8"))

    found_gates: set[str] = set()
    for stage in pipeline.get("stages", []):
        gate = stage.get("gate")
        if isinstance(gate, dict) and gate.get("checkpoint_id"):
            found_gates.add(str(gate["checkpoint_id"]))

    required_ids = {g.gate_id for g in archetype.gate_slots if g.required}
    missing = required_ids - found_gates
    assert not missing, f"scaffold missing required gates: {sorted(missing)}"


# ---------------------------------------------------------------------------
# 6. Required OutputType members surface in SKILL.md frontmatter
# ---------------------------------------------------------------------------


def test_scaffold_evaluation_required_outputs_in_frontmatter(tmp_path: Path) -> None:
    from kernel.skill_loader import parse_frontmatter

    plan = _scaffold(tmp_path)
    archetype = load_archetype("evaluation")
    fm, _body = parse_frontmatter(plan.skill_dir / "SKILL.md")

    declared_types: set[str] = set()
    for entry in fm.get("outputs") or []:
        if isinstance(entry, dict) and entry.get("type"):
            declared_types.add(str(entry["type"]))

    expected = {ot.value for ot in archetype.outputs.required}
    missing = expected - declared_types
    assert not missing, f"SKILL.md missing required output types: {sorted(missing)}"


# ---------------------------------------------------------------------------
# 7. --dry-run must not touch the filesystem
# ---------------------------------------------------------------------------


def test_scaffold_dry_run_creates_no_files(tmp_path: Path) -> None:
    plan = scaffold_skill(
        archetype_name="evaluation",
        skill_name="ghost-skill",
        output_dir=tmp_path,
        dry_run=True,
    )

    # The plan still describes what *would* have been written.
    assert plan.skill_dir == (tmp_path / "ghost-skill").resolve()
    assert plan.files, "dry-run plan should still enumerate files"

    # But nothing was created.
    assert not plan.skill_dir.exists(), (
        "dry-run materialised files; expected no filesystem changes"
    )
    assert not any(tmp_path.iterdir()), (
        f"dry-run polluted output_dir: {sorted(p.name for p in tmp_path.iterdir())}"
    )


# ---------------------------------------------------------------------------
# 8. Existing target dir without --force must raise + non-zero exit
# ---------------------------------------------------------------------------


def test_scaffold_refuses_to_overwrite_without_force(tmp_path: Path) -> None:
    # Pre-create the target so scaffold sees a collision.
    target = tmp_path / "demo-skill"
    target.mkdir()
    (target / "leftover.txt").write_text("keep me", encoding="utf-8")

    with pytest.raises(FileExistsError) as exc_info:
        scaffold_skill(
            archetype_name="evaluation",
            skill_name="demo-skill",
            output_dir=tmp_path,
        )
    # Error message must be actionable per CONTRACT §3.E.
    assert "--force" in str(exc_info.value)

    # File must still be untouched.
    assert (target / "leftover.txt").read_text(encoding="utf-8") == "keep me"

    # CLI surface mirrors the API: non-zero exit when target exists.
    rc = main(
        [
            "--archetype",
            "evaluation",
            "--name",
            "demo-skill",
            "--output-dir",
            str(tmp_path),
        ]
    )
    assert rc != 0, "CLI should exit non-zero when target exists without --force"


# ---------------------------------------------------------------------------
# 9. --force replaces an existing target dir
# ---------------------------------------------------------------------------


def test_scaffold_force_overwrites(tmp_path: Path) -> None:
    target = tmp_path / "demo-skill"
    target.mkdir()
    leftover = target / "leftover.txt"
    leftover.write_text("stale", encoding="utf-8")

    plan = scaffold_skill(
        archetype_name="evaluation",
        skill_name="demo-skill",
        output_dir=tmp_path,
        force=True,
    )

    assert plan.skill_dir.exists()
    assert not leftover.exists(), "--force did not clear stale files"
    assert (plan.skill_dir / "SKILL.md").is_file()
    assert (plan.skill_dir / "pipeline.yaml").is_file()


# ---------------------------------------------------------------------------
# 10. Preflight passes (CONTRACT §3.A scaffold_preflight_pass_rate=100%)
# ---------------------------------------------------------------------------


def test_scaffold_preflight_passes(tmp_path: Path) -> None:
    from kernel.contracts.schemas import DesignOSConfig, GlobalConfig, SkillContext
    from kernel.preflight.checker import PreflightChecker
    from kernel.skill_loader import load_pipeline_skill

    plan = _scaffold(tmp_path, name="preflight-demo")
    skill = load_pipeline_skill(plan.skill_dir)

    workspace = tmp_path / "ws"
    workspace.mkdir()

    ctx = SkillContext(
        workspace=workspace,
        skill_name=skill.config.name,
        skill_version=skill.config.version,
        run_id="scaffold-preflight-test",
        mode=None,
        config=DesignOSConfig(workspace=workspace, global_config=GlobalConfig()),
    )

    checker = PreflightChecker(repo_root=REPO_ROOT)
    errors = asyncio.run(checker.check(skill, ctx))
    assert errors == [], f"preflight returned errors for fresh scaffold: {errors}"


# ---------------------------------------------------------------------------
# 11. Scaffold output passes the factory Validator (validate.py integration)
# ---------------------------------------------------------------------------


def test_scaffold_validates_against_archetype(tmp_path: Path) -> None:
    from tools.validate import Validator

    plan = _scaffold(tmp_path, name="validate-demo")
    archetype = load_archetype("evaluation")
    validator = Validator(plan.skill_dir, archetype)

    passed = validator.validate()
    if not passed:
        # Surface diagnostic detail on failure so the report is actionable.
        rendered = "\n".join(
            f"  {v.dimension}: {v.message}\n    fix: {v.fix}"
            for v in validator.violations
        )
        pytest.fail(f"scaffold output failed validation:\n{rendered}")


# ---------------------------------------------------------------------------
# 12. CLI --help (CONTRACT §5 Gate 5: every CLI must support --help)
# ---------------------------------------------------------------------------


def test_scaffold_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.scaffold", "--help"],
        cwd=FACTORY_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"--help exited {result.returncode}: {result.stderr}"
    out = result.stdout
    # Help must mention every public flag the contract relies on.
    for token in ("--archetype", "--name", "--output-dir", "--dry-run", "--force"):
        assert token in out, f"--help missing flag: {token}"


# ---------------------------------------------------------------------------
# Bonus: end-to-end CLI run + frontmatter sanity (lightweight smoke)
# ---------------------------------------------------------------------------


def test_scaffold_cli_writes_skill(tmp_path: Path) -> None:
    """CLI invocation produces a kernel-loadable skill end to end."""
    from kernel.skill_loader import load_pipeline_skill

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.scaffold",
            "--archetype",
            "evaluation",
            "--name",
            "cli-demo",
            "--output-dir",
            str(tmp_path),
        ],
        cwd=FACTORY_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"scaffold CLI failed (rc={result.returncode}):\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    skill_dir = tmp_path / "cli-demo"
    assert skill_dir.is_dir()
    skill = load_pipeline_skill(skill_dir)
    assert skill.config.name == "cli-demo"
    assert skill.get_stages()


def test_scaffold_rejects_invalid_skill_name(tmp_path: Path) -> None:
    """Skill names with spaces or special chars must be rejected with a fix hint."""
    with pytest.raises(ValueError) as exc_info:
        scaffold_skill(
            archetype_name="evaluation",
            skill_name="bad name!",
            output_dir=tmp_path,
        )
    msg = str(exc_info.value)
    assert "fix:" in msg, "invalid-name error must carry an actionable hint"
