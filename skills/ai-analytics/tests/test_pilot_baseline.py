"""ai-analytics A1 pilot baseline contracts.

Locks the promises that make ai-analytics a real upstream skill for prd2proto:
- the skill loads and exposes the analysis pipeline
- it declares the 4 analysis OutputTypes (design_strategy + user_persona core)
- its output_type names EXACTLY match what prd2proto upstream_refs expects
- the two core product schemas are valid JSON Schema and carry the fields
  prd2proto stage1 actually consumes
- the data-completeness gate (QG1) exists so strategy is not hard-synthesized
  on insufficient data
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

_REPO_ROOT: Path = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from kernel.skill_loader import load_pipeline_skill  # noqa: E402

SKILL_DIR: Path = _REPO_ROOT / "skills" / "ai-analytics"
PRD2PROTO_DIR: Path = _REPO_ROOT / "skills" / "prd2proto"


def _pipeline(path: Path) -> dict:
    return yaml.safe_load((path / "pipeline.yaml").read_text(encoding="utf-8"))


# --- skill load -----------------------------------------------------------


def test_skill_loads() -> None:
    skill = load_pipeline_skill(SKILL_DIR)
    assert skill.config.name == "ai-analytics"
    assert skill.get_stages(), "pipeline produced no stages"


def test_declares_core_output_types() -> None:
    skill = load_pipeline_skill(SKILL_DIR)
    types = {o.type for o in skill.config.outputs}
    assert "design_strategy" in types
    assert "user_persona" in types
    assert "analysis_report" in types
    assert "comparison_matrix" in types


# --- prd2proto upstream_refs compatibility (the whole point of A1) --------


def test_output_types_match_prd2proto_upstream_refs() -> None:
    """prd2proto declares it consumes design_strategy + user_persona from
    ai-analytics. ai-analytics MUST produce those exact output_type names,
    otherwise the kernel cannot wire the products into prd2proto stage1."""
    prd2proto = _pipeline(PRD2PROTO_DIR)
    wanted = {
        ref["output_type"]
        for ref in prd2proto.get("upstream_refs", [])
        if ref.get("skill") == "ai-analytics"
    }
    assert wanted == {"design_strategy", "user_persona"}, (
        f"prd2proto upstream_refs changed: {wanted}"
    )
    produced = {o.type for o in load_pipeline_skill(SKILL_DIR).config.outputs}
    missing = wanted - produced
    assert not missing, f"ai-analytics does not produce: {missing}"


# --- output schema validity + downstream-required fields ------------------


def test_design_strategy_schema_has_prd2proto_fields() -> None:
    schema = json.loads(
        (SKILL_DIR / "templates" / "design-strategy.schema.json").read_text("utf-8")
    )
    required = set(schema.get("required", []))
    assert {"target_audience", "business_goal"} <= required


def test_user_persona_schema_has_prd2proto_fields() -> None:
    schema = json.loads(
        (SKILL_DIR / "templates" / "user-persona.schema.json").read_text("utf-8")
    )
    assert schema["type"] == "array"
    item_required = set(schema["items"].get("required", []))
    assert {"role", "goals", "pain_points"} <= item_required


# --- data-completeness gate -----------------------------------------------


def test_strategy_synthesis_has_completeness_gate() -> None:
    pipeline = _pipeline(SKILL_DIR)
    by_id = {s["id"]: s for s in pipeline["stages"]}
    synth = by_id["strategy-synthesis"]
    assert "design_strategy" in synth["outputs"]
    assert "user_persona" in synth["outputs"]
    assert "data_completeness_assessment" in synth["outputs"]
    gate = synth.get("gate")
    assert gate and gate["action"] == "pause", "QG1 completeness gate missing"
    assert gate["checkpoint_id"] == "QG1"


def test_pipeline_stages_are_llm_synthesis() -> None:
    """pilot honesty: no stage claims to be a real data-collection tool."""
    pipeline = _pipeline(SKILL_DIR)
    for stage in pipeline["stages"]:
        assert stage["type"] == "llm", f"{stage['id']} should be llm in pilot"
