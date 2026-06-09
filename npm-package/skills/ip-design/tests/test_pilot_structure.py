"""ip-design pilot 结构测试 — Batch I1 baseline lock。

锁定 ip-design skill 的 pilot runtime 结构:
- SKILL.md / pipeline.yaml / constitution.md 存在。
- pipeline.yaml 有 6 个 stage,每个 stage 引用共享 knowledge。
- 6 个 prompt 文件存在且引用对应共享方法论 id。
- 6 个 reference adapter 存在。
- eval/ 目录含 golden / failure / promptfoo.yaml。
- constitution 至少含 8 条约束。
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

_REPO_ROOT: Path = Path(__file__).resolve().parents[3]
_SKILL_DIR: Path = _REPO_ROOT / "skills" / "ip-design"
_PIPELINE: Path = _SKILL_DIR / "pipeline.yaml"
_SKILL_MD: Path = _SKILL_DIR / "SKILL.md"
_CONSTITUTION: Path = _SKILL_DIR / "constitution.md"

_EXPECTED_STAGES = (
    "strategy-alignment",
    "worldview-building",
    "persona-modeling",
    "visual-translation",
    "narrative-planning",
    "landing-spec",
)

_EXPECTED_PROMPTS = tuple(f"prompts/{i:02d}-{s}.md" for i, s in enumerate(_EXPECTED_STAGES, 1))
_EXPECTED_ADAPTERS = tuple(f"reference/adapter-{s}.md" for s in _EXPECTED_STAGES)


def test_skill_core_files_exist() -> None:
    """SKILL.md / pipeline.yaml / constitution.md 存在。"""
    assert _SKILL_MD.is_file(), "SKILL.md 缺失"
    assert _PIPELINE.is_file(), "pipeline.yaml 缺失"
    assert _CONSTITUTION.is_file(), "constitution.md 缺失"


def test_pipeline_has_six_stages() -> None:
    """pipeline.yaml 含 6 个 stage,id 对应预期。"""
    data = yaml.safe_load(_PIPELINE.read_text(encoding="utf-8"))
    stages = data.get("stages") or []
    assert len(stages) == 6, f"应有 6 个 stage,实际 {len(stages)}"
    actual_ids = [s["id"] for s in stages]
    assert tuple(actual_ids) == _EXPECTED_STAGES, f"stage id 不匹配:{actual_ids}"


def test_each_stage_references_shared_knowledge() -> None:
    """每个 stage 的 knowledge 字段引用共享方法论 id。"""
    data = yaml.safe_load(_PIPELINE.read_text(encoding="utf-8"))
    for stage in data["stages"]:
        knowledge = stage.get("knowledge") or []
        assert knowledge, f"stage {stage['id']} 的 knowledge 为空"
        # 至少含 1 个 design.* id(字典形式 {id: ...})
        has_shared_id = any(
            isinstance(k, dict) and k.get("id", "").startswith("design.")
            for k in knowledge
        )
        assert has_shared_id, f"stage {stage['id']} 未引用 design.* 共享 id"


def test_six_prompts_exist_and_reference_shared_methods() -> None:
    """6 个 prompt 文件存在且引用对应共享方法论 id。"""
    for prompt_path in _EXPECTED_PROMPTS:
        full_path = _SKILL_DIR / prompt_path
        assert full_path.is_file(), f"{prompt_path} 缺失"
        text = full_path.read_text(encoding="utf-8")
        # 每个 prompt 必须引用至少 1 个 design.* id
        assert re.search(r"`design\.\w+\.\w+(-\w+)*`", text), (
            f"{prompt_path} 未引用 design.* 共享方法论 id"
        )


def test_six_reference_adapters_exist() -> None:
    """6 个 reference adapter 存在。"""
    for adapter_path in _EXPECTED_ADAPTERS:
        full_path = _SKILL_DIR / adapter_path
        assert full_path.is_file(), f"{adapter_path} 缺失"


def test_eval_structure_exists() -> None:
    """eval/ 目录含 golden / failure / promptfoo.yaml。"""
    eval_dir = _SKILL_DIR / "eval"
    assert (eval_dir / "golden").is_dir(), "eval/golden/ 缺失"
    assert (eval_dir / "failure").is_dir(), "eval/failure/ 缺失"
    assert (eval_dir / "promptfoo.yaml").is_file(), "eval/promptfoo.yaml 缺失"
    # golden / failure 至少各 1 个 case
    golden_files = list((eval_dir / "golden").glob("*.md"))
    failure_files = list((eval_dir / "failure").glob("*.md"))
    assert len(golden_files) >= 2, f"eval/golden 应有 ≥2 个 case,实际 {len(golden_files)}"
    assert len(failure_files) >= 3, f"eval/failure 应有 ≥3 个 case,实际 {len(failure_files)}"


def test_constitution_has_at_least_eight_clauses() -> None:
    """constitution 至少含 8 条约束(标题 ## 1. 到 ## 8.)。"""
    text = _CONSTITUTION.read_text(encoding="utf-8")
    clause_headers = re.findall(r"^## \d+\.", text, re.M)
    assert len(clause_headers) >= 8, f"constitution 应有 ≥8 条约束,实际 {len(clause_headers)}"


def test_pipeline_has_two_quality_gates() -> None:
    """pipeline 有 2 个 gate(QG1 在 visual-translation,QG2 在 landing-spec)。"""
    data = yaml.safe_load(_PIPELINE.read_text(encoding="utf-8"))
    gates = [s for s in data["stages"] if "gate" in s]
    assert len(gates) == 2, f"应有 2 个 gate,实际 {len(gates)}"
    gate_stages = [s["id"] for s in gates]
    assert "visual-translation" in gate_stages, "QG1 应在 visual-translation"
    assert "landing-spec" in gate_stages, "QG2 应在 landing-spec"
    # 检查 checkpoint_id
    gate_checkpoint_ids = [s["gate"]["checkpoint_id"] for s in gates]
    assert "QG1" in gate_checkpoint_ids, "应有 checkpoint_id=QG1"
    assert "QG2" in gate_checkpoint_ids, "应有 checkpoint_id=QG2"


def test_pipeline_has_four_checkpoints() -> None:
    """pipeline 有 4 个 checkpoint(C1-C4,非 QG)。"""
    data = yaml.safe_load(_PIPELINE.read_text(encoding="utf-8"))
    checkpoints = [s for s in data["stages"] if "checkpoint" in s and "quality_gate" not in s]
    assert len(checkpoints) == 4, f"应有 4 个 checkpoint,实际 {len(checkpoints)}"
    checkpoint_ids = [s["checkpoint"]["id"] for s in checkpoints]
    assert checkpoint_ids == ["C1", "C2", "C3", "C4"], f"checkpoint id 不匹配:{checkpoint_ids}"


def test_skill_md_declares_pilot_boundary() -> None:
    """SKILL.md 声明 pilot 边界与不能做什么。"""
    text = _SKILL_MD.read_text(encoding="utf-8")
    assert "pilot" in text.lower(), "SKILL.md 未声明 pilot 定位"
    assert "不能做什么" in text or "不替代" in text or "不声明" in text, (
        "SKILL.md 未声明 pilot 边界(不能做什么)"
    )
    # 必须声明不调用图像生成 API
    assert "不调用图像生成" in text or "不调用图像" in text or "不产出最终视觉图像" in text, (
        "SKILL.md 未声明不调用图像生成 API"
    )
