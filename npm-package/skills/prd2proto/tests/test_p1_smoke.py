"""prd2proto P1 smoke tests.

Verifies the prd2proto skill can be:
- Loaded by kernel from disk
- Mode-filtered correctly (pm / designer-spec / designer-dsl)
- End-to-end exercised against frontend-codegen MOCK (no real LLM, no real DSL)
- Conforms to the v0.2 SKILL.md contracts (Progress Contract / Checkpoint Behavior)

These tests do NOT exercise the LLM stages — those need real prompts and an
LLM. They guard the structural and tool-integration contracts so that when
real prompts ship, the wiring is already known-good.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Make the project importable
_REPO_ROOT: Path = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Make frontend-codegen importable for the e2e codegen smoke
_CODEGEN_DIR: Path = _REPO_ROOT / "mcp-servers" / "frontend-codegen"
if str(_CODEGEN_DIR) not in sys.path:
    sys.path.insert(0, str(_CODEGEN_DIR))

from kernel.contracts.schemas import DesignOSConfig, GlobalConfig, SkillContext  # noqa: E402
from kernel.pipeline.condition import condition_satisfied  # noqa: E402
from kernel.skill_loader import load_pipeline_skill  # noqa: E402

SKILL_DIR: Path = _REPO_ROOT / "skills" / "prd2proto"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ctx(mode: str | None, tmp_path: Path) -> SkillContext:
    return SkillContext(
        workspace=tmp_path,
        skill_name="prd2proto",
        skill_version="0.2.0",
        run_id="smoke",
        mode=mode,  # type: ignore[arg-type]
        config=DesignOSConfig(workspace=tmp_path, global_config=GlobalConfig()),
    )


def _stages_for_mode(mode: str, tmp_path: Path) -> list[str]:
    """Return the stage IDs that would actually execute in this mode."""
    skill = load_pipeline_skill(SKILL_DIR)
    ctx = _ctx(mode, tmp_path)
    return [s.id for s in skill.get_stages() if condition_satisfied(s.only_when, ctx)]


# ---------------------------------------------------------------------------
# Skill structure
# ---------------------------------------------------------------------------


def test_prd2proto_loads_with_three_modes() -> None:
    skill = load_pipeline_skill(SKILL_DIR)
    assert set(skill.config.supported_modes) == {"pm", "designer-spec", "designer-dsl"}


def test_prd2proto_declares_required_outputs() -> None:
    skill = load_pipeline_skill(SKILL_DIR)
    output_ids = {o.id for o in skill.config.outputs}
    # Generation archetype required
    assert {"prototype_code", "frontend_code"} <= output_ids
    # prd2proto specifics
    assert "design_tokens" in output_ids
    assert "information_architecture" in output_ids


def test_prd2proto_declares_external_mcps_for_designer_dsl() -> None:
    """figma-mcp and mastergo-mcp should both be declared as builtin=False
    with required_when='mode == "designer-dsl"' so preflight prompts the user."""
    skill = load_pipeline_skill(SKILL_DIR)
    by_name = {s.name: s for s in skill.config.mcp_servers}
    for name in ("figma-mcp", "mastergo-mcp"):
        assert name in by_name, f"missing external MCP declaration: {name}"
        srv = by_name[name]
        assert srv.builtin is False, f"{name} should be builtin=False"
        assert srv.required_when == 'mode == "designer-dsl"'


def test_prd2proto_pipeline_has_stages() -> None:
    """v0.2 topology: 8 stages total. component-mapping removed (only useful
    for designer-dsl with real MCP, deferred); liveness-check appended."""
    skill = load_pipeline_skill(SKILL_DIR)
    stage_ids = [s.id for s in skill.get_stages()]
    expected = [
        "prd-understanding",
        "design-analysis",
        "spec-generation",
        "dsl-fetch",
        "token-extraction",
        "code-generation",
        "review-gate",
        "liveness-check",
    ]
    assert stage_ids == expected


def test_pipeline_has_liveness_check() -> None:
    """liveness-check must be the final stage so dev server is always
    started before declaring done (closes the 'ERR_CONNECTION_REFUSED' gap)."""
    skill = load_pipeline_skill(SKILL_DIR)
    stage_ids = [s.id for s in skill.get_stages()]
    assert stage_ids[-1] == "liveness-check"


# ---------------------------------------------------------------------------
# Mode-specific stage filtering (the core thing we want to lock in P1)
# ---------------------------------------------------------------------------


def test_pm_mode_runs_active_stages(tmp_path: Path) -> None:
    """pm mode: PRD only, but spec-generation still runs (template-matched
    design-spec) so token-extraction has a source. Skips dsl-fetch only."""
    active = _stages_for_mode("pm", tmp_path)
    assert "prd-understanding" in active
    assert "design-analysis" in active
    assert "spec-generation" in active   # template-matched even in pm
    assert "token-extraction" in active  # all modes get tokens
    assert "code-generation" in active
    assert "review-gate" in active
    assert "liveness-check" in active
    # pm skips DSL fetch only
    assert "dsl-fetch" not in active
    # 7 stages active
    assert len(active) == 7


def test_designer_spec_mode_runs_spec_and_token_but_not_dsl(tmp_path: Path) -> None:
    """designer-spec = PRD + (generated or user-provided) design-spec.md.
    No DSL."""
    active = _stages_for_mode("designer-spec", tmp_path)
    assert "spec-generation" in active
    assert "token-extraction" in active
    assert "liveness-check" in active
    assert "dsl-fetch" not in active
    # 7 stages: prd / design / spec / token / code / review / liveness
    assert len(active) == 7


def test_designer_dsl_mode_skips_spec_generation(tmp_path: Path) -> None:
    """designer-dsl: skips spec-generation (user provides DSL + spec),
    but runs dsl-fetch + token-extraction."""
    active = _stages_for_mode("designer-dsl", tmp_path)
    assert "dsl-fetch" in active
    assert "token-extraction" in active
    assert "liveness-check" in active
    assert "spec-generation" not in active
    # 7 stages
    assert len(active) == 7


# ---------------------------------------------------------------------------
# SKILL.md v0.2 contract checks (Progress Contract / Checkpoint Behavior /
# anti-regression on the deleted Step 0 boilerplate)
# ---------------------------------------------------------------------------


def test_skill_md_has_progress_contract() -> None:
    """v0.2 SKILL.md must contain the Progress Contract section that
    governs LLM behavior in chat mode."""
    skill_md = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "Progress Contract" in skill_md, (
        "SKILL.md missing 'Progress Contract' section — re-add it (see "
        "REPORT-skill-iteration.md §1.3)"
    )


def test_skill_md_has_checkpoint_policy() -> None:
    """v0.2 SKILL.md must contain the Checkpoint Behavior section that
    explicitly tells the LLM not to deadlock-wait at C1/C2/C3 in chat mode."""
    skill_md = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "Checkpoint Behavior" in skill_md, (
        "SKILL.md missing 'Checkpoint Behavior' section — re-add it (see "
        "REPORT-skill-iteration.md §1.2)"
    )


def test_no_step0_boilerplate() -> None:
    """v0.2 SKILL.md must NOT contain the verbose Step 0 reply template
    that duplicates command-message content. The new style is concise:
    'mode + PRD path → preflight; otherwise ask what's missing'."""
    skill_md = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    # The hallmark phrase from the deleted Step 0 boilerplate
    assert "请确认：1. 哪种保真度" not in skill_md, (
        "SKILL.md still contains the legacy Step 0 boilerplate — delete it "
        "and replace with the concise mode-detection paragraph"
    )
    assert "我将用 prd2proto 把 PRD 转成前端代码" not in skill_md, (
        "SKILL.md still contains the legacy 'reply user' opening template"
    )


# ---------------------------------------------------------------------------
# frontend-codegen mock end-to-end (no LLM, no real DSL — just the codegen path)
#
# These tests cover the underlying mock infrastructure. The pipeline itself
# no longer calls these tools (stages 4/5 are LLM-driven in v0.2), but the
# mocks remain available for designer-dsl mode and for future real MCP work.
# ---------------------------------------------------------------------------


def test_codegen_mock_pm_mode_writes_runnable_react(tmp_path: Path) -> None:
    """Smoke: frontend-codegen mock can still produce a runnable React
    skeleton on demand. v0.2 pipeline doesn't call this directly, but
    keeping the contract green so future MCP work stays compatible."""
    from core import generate_code as codegen_generate
    from schemas import GenerateCodeRequest

    out = tmp_path / "pm-mode-output"
    resp = codegen_generate(
        GenerateCodeRequest(
            mode="pm",
            framework="react",
            output_dir=str(out),
        )
    )
    assert resp.is_mock is True
    assert "package.json" in resp.files_written
    pkg = json.loads((out / "package.json").read_text())
    assert "react" in pkg["dependencies"]


def test_codegen_mock_designer_dsl_mode_uses_dsl_inputs(tmp_path: Path) -> None:
    """Smoke: designer-dsl mock chain (dsl → tokens → mapping → codegen)
    still wires through. v0.2 pipeline no longer chains these stages
    directly (component-mapping was removed), but the mock contract is
    preserved for future real-MCP work."""
    from core import (
        extract_tokens,
        fetch_dsl,
        generate_code as codegen_generate,
        map_components,
    )
    from schemas import (
        DSLFetchRequest,
        ExtractTokensRequest,
        GenerateCodeRequest,
        MapComponentsRequest,
    )

    out = tmp_path / "dsl-mode-output"

    dsl = fetch_dsl(DSLFetchRequest(source="figma", file_id="smoke"))
    tokens = extract_tokens(ExtractTokensRequest(dsl=dsl)).tokens
    mapping = map_components(MapComponentsRequest(dsl=dsl, component_lib="antd-react")).mapping

    assert mapping.coverage_rate == 1.0  # mock has full mapping
    assert "color.brand.primary" in tokens.colors

    resp = codegen_generate(
        GenerateCodeRequest(
            mode="designer-dsl",
            framework="react",
            output_dir=str(out),
            dsl=dsl,
            tokens=tokens,
            component_mapping=mapping,
        )
    )
    assert resp.is_mock is True
    assert (out / "src" / "App.jsx").exists()


# ---------------------------------------------------------------------------
# Validate against the factory archetype
# ---------------------------------------------------------------------------


def test_prd2proto_passes_factory_validate() -> None:
    """Calling validate.py against this skill must exit 0 — the contract
    between scaffold + validate + this skill must hold even after our
    hand-rewrites of SKILL.md and pipeline.yaml."""
    import subprocess

    factory_dir = _REPO_ROOT / ".factory"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.validate",
            str(SKILL_DIR),
            "--archetype",
            "generation",
        ],
        cwd=str(factory_dir),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"validate failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "All checks passed" in result.stdout
