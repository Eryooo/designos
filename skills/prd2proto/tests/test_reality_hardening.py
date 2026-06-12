"""prd2proto P1.1 Reality Hardening contracts.

These tests lock the behavioral promises that the two real run reports
(Trae + Claude Code) exposed as the most painful gaps. They turn prose claims
in SKILL.md / pipeline.yaml / constitution.md into asserted, regression-proof
contracts:

- Progress Contract is a hard execution discipline, not just documentation.
- Checkpoints default to "continue + summary" in chat mode (no deadlock wait).
- preflight is mode-driven: frontend-codegen is NOT an unconditional dependency.
- Visibility loop: stable output-path convention + liveness dev_url delivery.
- Automation honesty: no stage is described as fully-automated when it is LLM/manual.

Source reports: two real run reports (external IDE + Claude Code), kept in
private local evidence (not tracked in this public repo).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_REPO_ROOT: Path = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from kernel.contracts.schemas import (  # noqa: E402
    DesignOSConfig,
    GlobalConfig,
    SkillContext,
)
from kernel.preflight.checker import PreflightChecker  # noqa: E402
from kernel.skill_loader import load_pipeline_skill  # noqa: E402

SKILL_DIR: Path = _REPO_ROOT / "skills" / "prd2proto"


def _skill_md() -> str:
    return (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")


def _pipeline() -> dict:
    return yaml.safe_load((SKILL_DIR / "pipeline.yaml").read_text(encoding="utf-8"))


def _ctx(mode: str, tmp_path: Path) -> SkillContext:
    return SkillContext(
        workspace=tmp_path,
        skill_name="prd2proto",
        skill_version="0.2.0",
        run_id="reality",
        mode=mode,  # type: ignore[arg-type]
        config=DesignOSConfig(workspace=tmp_path, global_config=GlobalConfig()),
    )


# ---------------------------------------------------------------------------
# 1. Progress Contract is a hard execution discipline (report §1.3 / §1.1)
# ---------------------------------------------------------------------------


def test_progress_contract_is_mandatory_and_first() -> None:
    """Progress Contract must exist, be marked mandatory, and appear before the
    bulk of the doc so the LLM reads it before writing the first artifact."""
    md = _skill_md()
    assert "Progress Contract" in md
    assert "强制" in md.split("Progress Contract", 1)[1][:80], (
        "Progress Contract section must be flagged as mandatory near its header"
    )
    # Must appear in the first 40% of the document (loaded before any stage work).
    pos = md.index("Progress Contract")
    assert pos < len(md) * 0.4, "Progress Contract buried too deep in SKILL.md"


def test_progress_contract_bans_long_silence() -> None:
    """The contract must put a hard ceiling on silent time — the literal cause
    of every '你在干啥怎么卡半天不动' complaint in the run reports."""
    md = _skill_md()
    section = md.split("Progress Contract", 1)[1].split("## ", 1)[0]
    assert "60 秒" in section or "60秒" in section, (
        "Progress Contract must cap silence (≤60s between progress lines)"
    )
    # Every stage boundary must emit a marker (start ⏳ and done ✅).
    assert "⏳" in section and "✅" in section


# ---------------------------------------------------------------------------
# 2. Checkpoint behavior: continue-by-default in chat mode (report §1.2)
# ---------------------------------------------------------------------------


def test_checkpoint_policy_defaults_to_continue_in_chat_mode() -> None:
    md = _skill_md()
    assert "Checkpoint Behavior" in md
    section = md.split("Checkpoint Behavior", 1)[1].split("## ", 1)[0]
    # Chat mode must NOT deadlock-wait on C1/C2/C3.
    assert "不允许在 C1/C2/C3 死等用户输入" in section, (
        "Checkpoint policy must forbid deadlock-waiting at C1/C2/C3 in chat mode"
    )
    # Only genuine quality gates may hard-stop.
    assert "QG_REVIEW" in section
    assert "继续" in section


def test_only_review_gate_hard_stops() -> None:
    """Of all checkpoints, only the review gate may pause the run, and only when
    there are real constitution violations."""
    pipeline = _pipeline()
    gated = [s for s in pipeline["stages"] if s.get("gate")]
    assert len(gated) == 1, "exactly one hard gate expected (review-gate)"
    gate = gated[0]["gate"]
    assert gate["action"] == "pause"
    assert gate["when"] == "constitution_violations.count > 0"
    assert gate["resume_from_stage"] == "code-generation"


# ---------------------------------------------------------------------------
# 3. Preflight is mode-driven — frontend-codegen is NOT unconditional (report §2.2)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_frontend_codegen_not_checked_outside_designer_dsl(tmp_path: Path) -> None:
    """The mock frontend-codegen MCP must only be a dependency in designer-dsl.
    In pm / designer-spec it must NOT be probed — otherwise it's the report's
    'mock MCP 永远通过但没真实价值' performative check, now at the runtime layer.

    We assert via the declared requirement condition: frontend-codegen carries
    required_when == designer-dsl, so the mode-condition filter excludes it for
    the other two modes.
    """
    skill = load_pipeline_skill(SKILL_DIR)
    by_name = {s.name: s for s in skill.config.mcp_servers}
    fc = by_name["frontend-codegen"]
    assert fc.required_when == 'mode == "designer-dsl"', (
        "frontend-codegen must be conditional on designer-dsl, not unconditional"
    )
    # And preflight must not raise/charge it in pm or designer-spec.
    checker = PreflightChecker(repo_root=_REPO_ROOT)
    for mode in ("pm", "designer-spec"):
        errors = await checker.check(skill, _ctx(mode, tmp_path))
        assert all("frontend-codegen" not in e for e in errors), (
            f"frontend-codegen wrongly probed in mode={mode}: {errors}"
        )


def test_preflight_table_is_mode_driven_in_doc() -> None:
    """SKILL.md preflight section must be a per-mode table, not a flat list that
    checks pdf-parser / figma always."""
    md = _skill_md()
    section = md.split("Preflight", 1)[1].split("## ", 1)[0]
    # pdf-parser only when PRD is a .pdf; figma/mastergo only in designer-dsl.
    assert "designer-dsl" in section
    assert ".pdf" in section or "pdf-parser" in section
    assert "figma-mcp" in section or "mastergo-mcp" in section


# ---------------------------------------------------------------------------
# 4. Visibility loop — output path + liveness dev_url (report §2.5 / §2.6)
# ---------------------------------------------------------------------------


def test_output_path_convention_is_stable() -> None:
    md = _skill_md()
    assert "Output Path Convention" in md
    assert "prd2proto-out" in md
    assert "run_id" in md.lower()


def test_liveness_is_final_stage_and_delivers_url() -> None:
    pipeline = _pipeline()
    stages = pipeline["stages"]
    assert stages[-1]["id"] == "liveness-check", "liveness-check must be last"
    assert "dev_url" in stages[-1]["outputs"], (
        "liveness-check must output dev_url so the user knows which URL to open"
    )
    prompt = (SKILL_DIR / "prompts" / "07-liveness-check.md").read_text(encoding="utf-8")
    # Must tell the user which URL/files to open, and must not fake success.
    assert "localhost" in prompt
    assert "不要假装跑通" in prompt or "不要伪造" in prompt


# ---------------------------------------------------------------------------
# 5. Automation honesty — no LLM/manual stage described as fully automated
# ---------------------------------------------------------------------------


def test_skill_md_has_implementation_truth_table() -> None:
    """SKILL.md must carry a stage-by-stage 实装现状 table distinguishing real
    tool automation from LLM/manual synthesis."""
    md = _skill_md()
    assert "实装现状" in md
    section = md.split("实装现状", 1)[1].split("## ", 1)[0]
    # The LLM-driven stages must be visibly marked as LLM, not silently 'tool'.
    assert "token-extraction" in section and "code-generation" in section
    assert "LLM" in section
    # liveness must be marked not-yet-tool (mock has no launch_preview).
    assert "liveness-check" in section


def test_no_fully_automated_overclaim() -> None:
    """No prd2proto doc may claim mock paths are fully automated."""
    for path in SKILL_DIR.rglob("*.md"):
        if "__pycache__" in str(path):
            continue
        text = path.read_text(encoding="utf-8")
        for bad in ("完全自动化", "fully automated", "全自动化"):
            assert bad not in text, f"overclaim '{bad}' in {path}"


def test_pipeline_marks_mock_dependent_stage_as_tool_only_for_dsl() -> None:
    """dsl-fetch is the only real tool stage and it's designer-dsl only; the
    LLM-driven token/code stages must be type: llm, not type: tool."""
    pipeline = _pipeline()
    by_id = {s["id"]: s for s in pipeline["stages"]}
    assert by_id["dsl-fetch"]["type"] == "tool"
    assert by_id["dsl-fetch"]["only_when"] == 'mode == "designer-dsl"'
    assert by_id["token-extraction"]["type"] == "llm"
    assert by_id["code-generation"]["type"] == "llm"


