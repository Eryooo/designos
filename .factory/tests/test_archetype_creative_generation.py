"""creative-generation archetype 测试 — Batch I1.1 baseline lock。

锁定 creative-generation archetype 的 pilot 结构(从 ip-design I1 提取):
- version == 0.1.0-pilot
- required outputs: brand_brief / visual_spec / image_prompt_pack
- required stage_slots: strategy_alignment / visual_translation / landing_spec
- optional stage_slots: worldview_building / persona_modeling / narrative_planning
- quality gates: QG1(visual_translation) / QG2(landing_spec)
- checkpoints: C1 required, C2/C3/C4 optional
- mode_semantics.semantic_type: none (单模式)
- evidence_contract.required_fields: professional_gap_report
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

_FACTORY_ROOT: Path = Path(__file__).resolve().parents[1]
_ARCHETYPE_PATH: Path = _FACTORY_ROOT / "archetypes" / "creative-generation.yaml"


def test_creative_generation_archetype_exists() -> None:
    """creative-generation.yaml 存在。"""
    assert _ARCHETYPE_PATH.is_file(), "creative-generation.yaml 缺失"


def test_version_is_pilot() -> None:
    """version == 0.1.0-pilot。"""
    data = yaml.safe_load(_ARCHETYPE_PATH.read_text(encoding="utf-8"))
    assert data["version"] == "0.1.0-pilot", f"version 应为 0.1.0-pilot,实际 {data['version']}"


def test_required_outputs_are_creative_assets() -> None:
    """required outputs: brand_brief / visual_spec / image_prompt_pack。"""
    data = yaml.safe_load(_ARCHETYPE_PATH.read_text(encoding="utf-8"))
    required = data["outputs"]["required"]
    assert required == ["brand_brief", "visual_spec", "image_prompt_pack"], (
        f"required outputs 不匹配:{required}"
    )


def test_optional_outputs_include_creative_assets() -> None:
    """optional outputs 含 worldview / persona_profile / content_plan / brand_material_spec。"""
    data = yaml.safe_load(_ARCHETYPE_PATH.read_text(encoding="utf-8"))
    optional = data["outputs"]["optional"]
    expected = {"worldview", "persona_profile", "content_plan", "brand_material_spec"}
    assert expected.issubset(set(optional)), f"optional outputs 缺失 {expected - set(optional)}"


def test_required_stage_slots_are_creative_generation() -> None:
    """required stage_slots: strategy_alignment / visual_translation / landing_spec。"""
    data = yaml.safe_load(_ARCHETYPE_PATH.read_text(encoding="utf-8"))
    required_slots = [s["slot_id"] for s in data["stage_slots"] if s.get("required")]
    assert set(required_slots) == {"strategy_alignment", "visual_translation", "landing_spec"}, (
        f"required stage_slots 不匹配:{required_slots}"
    )


def test_optional_stage_slots_include_worldview_persona_narrative() -> None:
    """optional stage_slots 含 worldview_building / persona_modeling / narrative_planning。"""
    data = yaml.safe_load(_ARCHETYPE_PATH.read_text(encoding="utf-8"))
    optional_slots = [s["slot_id"] for s in data["stage_slots"] if not s.get("required")]
    expected = {"worldview_building", "persona_modeling", "narrative_planning"}
    assert expected.issubset(set(optional_slots)), f"optional stage_slots 缺失 {expected - set(optional_slots)}"


def test_all_creative_generation_stages_are_llm() -> None:
    """所有 creative-generation stage_slots 的 stage_type 都是 llm。"""
    data = yaml.safe_load(_ARCHETYPE_PATH.read_text(encoding="utf-8"))
    for slot in data["stage_slots"]:
        assert slot["stage_type"] == "llm", (
            f"stage_slot {slot['slot_id']} stage_type 应为 llm,实际 {slot['stage_type']}"
        )


def test_quality_gates_are_qg1_qg2() -> None:
    """quality gates: QG1(visual_translation) / QG2(landing_spec)。"""
    data = yaml.safe_load(_ARCHETYPE_PATH.read_text(encoding="utf-8"))
    gates = data["gate_slots"]
    assert len(gates) == 2, f"应有 2 个 gate,实际 {len(gates)}"
    gate_ids = [g["gate_id"] for g in gates]
    assert gate_ids == ["QG1", "QG2"], f"gate_ids 应为 ['QG1', 'QG2'],实际 {gate_ids}"
    gate_slots = [g["on_slot"] for g in gates]
    assert gate_slots == ["visual_translation", "landing_spec"], (
        f"gate on_slot 应为 ['visual_translation', 'landing_spec'],实际 {gate_slots}"
    )


def test_checkpoint_c1_required_others_optional() -> None:
    """checkpoint C1 required,C2/C3/C4 optional。"""
    data = yaml.safe_load(_ARCHETYPE_PATH.read_text(encoding="utf-8"))
    checkpoints = data["checkpoint_slots"]
    c1 = next(c for c in checkpoints if c["checkpoint_id"] == "C1")
    assert c1["required"] is True, "C1 应为 required"
    for c in checkpoints:
        if c["checkpoint_id"] in ("C2", "C3", "C4"):
            assert c["required"] is False, f"{c['checkpoint_id']} 应为 optional"


def test_mode_semantics_is_none() -> None:
    """mode_semantics.semantic_type: none (单模式)。"""
    data = yaml.safe_load(_ARCHETYPE_PATH.read_text(encoding="utf-8"))
    mode_semantics = data["mode_semantics"]
    assert mode_semantics["semantic_type"] == "none", (
        f"mode_semantics.semantic_type 应为 none,实际 {mode_semantics['semantic_type']}"
    )
    assert mode_semantics["allowed_modes"] == [], "allowed_modes 应为空列表"
    assert mode_semantics["must_be_single_mode"] is True, "must_be_single_mode 应为 true"


def test_evidence_contract_requires_professional_gap_report() -> None:
    """evidence_contract.required_fields: professional_gap_report。"""
    data = yaml.safe_load(_ARCHETYPE_PATH.read_text(encoding="utf-8"))
    evidence = data["evidence_contract"]
    assert evidence["required_fields"] == ["professional_gap_report"], (
        f"evidence required_fields 应为 ['professional_gap_report'],实际 {evidence['required_fields']}"
    )


def test_representative_skill_is_ip_design() -> None:
    """representative_skill == ip-design。"""
    data = yaml.safe_load(_ARCHETYPE_PATH.read_text(encoding="utf-8"))
    assert data["representative_skill"] == "ip-design", (
        f"representative_skill 应为 ip-design,实际 {data['representative_skill']}"
    )
