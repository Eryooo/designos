"""prd2proto P1 smoke tests.

Verifies the prd2proto skill can be:
- Loaded by kernel from disk
- Mode-filtered correctly (pm / designer-spec / designer-dsl)
- End-to-end exercised against frontend-codegen MOCK (no real LLM, no real DSL)

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
        skill_version="0.1.0",
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


def test_prd2proto_pipeline_has_eight_stages() -> None:
    skill = load_pipeline_skill(SKILL_DIR)
    stage_ids = [s.id for s in skill.get_stages()]
    expected = [
        "prd-understanding",
        "design-analysis",
        "spec-generation",
        "dsl-fetch",
        "token-extraction",
        "component-mapping",
        "code-generation",
        "review-gate",
    ]
    assert stage_ids == expected


# ---------------------------------------------------------------------------
# Mode-specific stage filtering (the core thing we want to lock in P1)
# ---------------------------------------------------------------------------


def test_pm_mode_skips_spec_dsl_token_component_stages(tmp_path: Path) -> None:
    """pm mode = PRD only, no spec, no DSL, no tokens, no component mapping."""
    active = _stages_for_mode("pm", tmp_path)
    assert "prd-understanding" in active
    assert "design-analysis" in active
    assert "code-generation" in active
    assert "review-gate" in active
    # All these should be skipped:
    assert "spec-generation" not in active
    assert "dsl-fetch" not in active
    assert "token-extraction" not in active
    assert "component-mapping" not in active
    # pm mode runs exactly 4 stages
    assert len(active) == 4


def test_designer_spec_mode_runs_spec_and_token_but_not_dsl(tmp_path: Path) -> None:
    """designer-spec = PRD + design-spec.md. No DSL, no component mapping."""
    active = _stages_for_mode("designer-spec", tmp_path)
    assert "spec-generation" in active
    assert "token-extraction" in active
    assert "dsl-fetch" not in active
    assert "component-mapping" not in active
    # 6 stages: prd / design / spec / token / code / review
    assert len(active) == 6


def test_designer_dsl_mode_runs_all_eight_stages_except_spec_generation(
    tmp_path: Path,
) -> None:
    """designer-dsl: skips spec-generation (no need to generate spec, user provides DSL),
    but runs dsl-fetch + token + component-mapping."""
    active = _stages_for_mode("designer-dsl", tmp_path)
    assert "dsl-fetch" in active
    assert "token-extraction" in active
    assert "component-mapping" in active
    assert "spec-generation" not in active  # designer-dsl users provide spec, don't generate it
    # 7 stages
    assert len(active) == 7


# ---------------------------------------------------------------------------
# frontend-codegen mock end-to-end (no LLM, no real DSL — just the codegen path)
# ---------------------------------------------------------------------------


def test_codegen_mock_pm_mode_writes_runnable_react(tmp_path: Path) -> None:
    """Smoke: in pm mode, the code-generation stage's tool call should produce
    a runnable React skeleton at `output_dir`. The MCP itself is mocked, so we
    invoke its core directly."""
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
    """Smoke: designer-dsl mode threads DSL → tokens → mapping → codegen end-to-end
    through the mock MCP."""
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
