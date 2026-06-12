"""brand-creative 契约冻结 + 知识就绪测试 — Batch B1.0。

覆盖 B1.0 第六节 10 条要求:
1. 13 个子技能全部拥有唯一契约。
2. public_outputs 全部属于现有 OutputType。
3. 不修改 Kernel OutputType(枚举集合与冻结基线一致)。
4. 所有 output_schema_refs 文件存在且是合法 JSON Schema 基线。
5. workflow 的运行时依赖与 contracts 完全一致。
6. 所有 active knowledge ID 均真实存在于全局 manifest。
7. planned asset 不得被 contract_status=ready_for_parallel 的子技能消费。
8. contract_status=ready_for_parallel 的子技能必须 P0 knowledge gap = 0。
9. 品牌创意质量资产不得继续直接使用完整 IP Design rubric 冒充。
10. 文档中不存在"最终商标可注册""版权清洁""可直接商用"等过度承诺。
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

_REPO_ROOT: Path = Path(__file__).resolve().parents[3]
_BC: Path = _REPO_ROOT / "skills" / "brand-creative"
_CONTRACTS: Path = _BC / "contracts" / "sub-skill-contracts.yaml"
_SCHEMAS_DIR: Path = _BC / "contracts" / "schemas"
_READINESS: Path = _BC / "contracts" / "knowledge-readiness-matrix.yaml"
_KM: Path = _BC / "knowledge-manifest.yaml"
_GROUP_MD: Path = _BC / "GROUP.md"
_GLOBAL_MANIFEST: Path = _REPO_ROOT / "knowledge" / "manifest.yaml"

_EXPECTED_SUB_SKILLS = {
    "brand-strategy", "competitive-analysis",
    "logo-design", "color-system", "typography-system", "visual-identity",
    "brand-voice", "content-strategy", "campaign-creative",
    "brand-collateral", "digital-assets", "brand-guidelines", "brand-audit",
}

# 现有 OutputType 枚举的冻结快照(若 kernel 改了枚举,本测试会失败 → 证明动了 kernel)
_FROZEN_OUTPUT_TYPES = {
    "analysis_report", "design_strategy", "comparison_matrix", "user_persona",
    "user_journey", "task_checklist", "issue_report", "html_report",
    "prototype_code", "design_tokens", "information_architecture",
    "component_spec", "style_guide", "brand_brief", "brand_persona",
    "visual_spec", "content_plan", "heuristic_checklist", "evidence_pack",
    "delivery_audit_bundle", "evaluation_script", "automated_eval_trace",
    "visual_diff_report", "acceptance_report", "page_mapping", "frontend_code",
    "design_token_spec", "worldview", "persona_profile", "image_prompt_pack",
    "brand_material_spec", "professional_gap_report",
}

_OVERPROMISE_TERMS = (
    "最终商标可注册", "商标可注册", "版权清洁", "可直接商用", "版权可用",
    "trademark registrable", "copyright clean", "ready for commercial use",
)


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _contracts() -> list[dict]:
    return _load(_CONTRACTS)["sub_skills"]


def test_thirteen_sub_skills_have_unique_contracts() -> None:
    """1. 13 个子技能全部拥有唯一契约。"""
    subs = _contracts()
    ids = [s["id"] for s in subs]
    assert len(ids) == 13, f"应有 13 个契约,实际 {len(ids)}"
    assert len(set(ids)) == 13, f"契约 id 不唯一: {ids}"
    assert set(ids) == _EXPECTED_SUB_SKILLS, (
        f"契约 id 与 13 子技能不符:多 {set(ids)-_EXPECTED_SUB_SKILLS}, "
        f"少 {_EXPECTED_SUB_SKILLS-set(ids)}"
    )
    # 每个契约 18 必填字段齐全
    required_fields = [
        "id", "purpose", "trigger_examples", "required_inputs", "optional_inputs",
        "upstream_contracts", "public_outputs", "internal_outputs",
        "output_schema_refs", "downstream_consumers", "runtime_dependencies",
        "knowledge_ids", "quality_gate", "fallback_behavior", "do_not_claim",
        "contract_status", "owner",
    ]
    for s in subs:
        for f in required_fields:
            assert f in s, f"契约 {s.get('id')} 缺字段: {f}"


def test_public_outputs_are_existing_output_types() -> None:
    """2. public_outputs 全部属于现有 OutputType。"""
    from kernel.contracts.enums import OutputType
    valid = {e.value for e in OutputType}
    for s in _contracts():
        for o in s.get("public_outputs", []) or []:
            assert o["type"] in valid, (
                f"{s['id']} 的 public_output '{o['type']}' 不是现有 OutputType"
            )


def test_visual_system_contract_outputs_match_runtime_state_keys() -> None:
    """B1.3: visual-system 子技能契约字段必须匹配 pipeline 实际 state key。"""
    contracts = {s["id"]: s for s in _contracts()}
    expected_outputs = {
        "logo-design": {"visual_spec", "image_prompt_pack"},
        "color-system": {"color_palette"},
        "typography-system": {"typography_spec"},
        "visual-identity": {"vi_manual"},
    }
    expected_inputs = {
        "visual-identity": {"visual_spec", "color_palette", "typography_spec"},
    }

    for sub_id, outputs in expected_outputs.items():
        pipeline = _load(_BC / "sub-skills" / sub_id / "pipeline.yaml")
        runtime_outputs = set(pipeline.get("outputs", []) or [])
        contract_outputs = {
            o["name"]
            for o in (contracts[sub_id].get("public_outputs", []) or [])
        }
        contract_outputs |= {
            o["name"]
            for o in (contracts[sub_id].get("internal_outputs", []) or [])
        }
        assert runtime_outputs == outputs, f"{sub_id} pipeline outputs drifted"
        assert contract_outputs == runtime_outputs, (
            f"{sub_id} contract outputs {contract_outputs} != runtime {runtime_outputs}"
        )

    for sub_id, inputs in expected_inputs.items():
        pipeline = _load(_BC / "sub-skills" / sub_id / "pipeline.yaml")
        runtime_inputs = set(pipeline.get("inputs", []) or [])
        contract_inputs = {
            i["name"]
            for i in (contracts[sub_id].get("required_inputs", []) or [])
        }
        assert runtime_inputs == inputs, f"{sub_id} pipeline inputs drifted"
        assert contract_inputs == runtime_inputs, (
            f"{sub_id} contract inputs {contract_inputs} != runtime {runtime_inputs}"
        )


def test_kernel_output_type_not_modified() -> None:
    """3. 不修改 Kernel OutputType(枚举集合与冻结基线一致)。"""
    from kernel.contracts.enums import OutputType
    current = {e.value for e in OutputType}
    assert current == _FROZEN_OUTPUT_TYPES, (
        f"Kernel OutputType 被改动!新增: {current - _FROZEN_OUTPUT_TYPES}, "
        f"删除: {_FROZEN_OUTPUT_TYPES - current}。B1.0 禁止改 kernel。"
    )


def test_all_schema_refs_exist_and_valid() -> None:
    """4. 所有 output_schema_refs 文件存在且是合法 JSON Schema 基线。"""
    for s in _contracts():
        for ref in s.get("output_schema_refs", []) or []:
            path = _SCHEMAS_DIR / ref
            assert path.is_file(), f"{s['id']} 引用的 schema 不存在: {ref}"
            data = json.loads(path.read_text(encoding="utf-8"))
            # 合法 JSON Schema 基线:有 $schema / type / properties
            assert data.get("$schema", "").startswith("http"), f"{ref} 缺 $schema"
            assert data.get("type") == "object", f"{ref} type 应为 object"
            assert "properties" in data, f"{ref} 缺 properties"
            assert isinstance(data.get("required", []), list), f"{ref} required 应为 list"


def _parse_group_frontmatter() -> dict:
    text = _GROUP_MD.read_text(encoding="utf-8")
    _, fm_block, _ = text.split("---", 2)
    return yaml.safe_load(fm_block)


def test_workflow_runtime_deps_consistent_with_contracts() -> None:
    """5. workflow 的运行时依赖与 contracts 完全一致。

    核心契约规则:生产者与消费者不得在同一 parallel step。
    用 contracts 声明的 upstream_contracts 推导依赖,验证 workflow 不违反。
    """
    contracts = {s["id"]: s for s in _contracts()}
    # 从契约提取依赖对:consumer 依赖 upstream(只取契约内子技能)
    dep_pairs = set()
    for sid, s in contracts.items():
        for up in s.get("upstream_contracts", []) or []:
            # upstream_contracts 条目形如 "brand-strategy (...)",取首 token
            up_id = up.split()[0].strip()
            if up_id in contracts:
                dep_pairs.add((up_id, sid))  # (producer, consumer)

    fm = _parse_group_frontmatter()
    for entry in fm["workflows"]:
        wf = _load(_BC / entry["file"])
        for idx, step in enumerate(wf["steps"]):
            if step["type"] != "parallel":
                continue
            members = set(step["sub_skills"])
            # 同一 parallel step 内不得存在 (producer, consumer) 对
            for producer, consumer in dep_pairs:
                assert not (producer in members and consumer in members), (
                    f"{entry['file']} step {idx} 把生产者 {producer} 与消费者 "
                    f"{consumer} 放在同一 parallel step,违反契约依赖"
                )


def test_active_knowledge_ids_exist_in_global_manifest() -> None:
    """6. 所有 active knowledge ID 均真实存在于全局 manifest。"""
    existing = {a["id"] for a in _load(_GLOBAL_MANIFEST)["assets"]}
    km = _load(_KM)
    for ref in km.get("shared_knowledge", []) or []:
        assert ref["id"] in existing, (
            f"knowledge-manifest active id 不存在于全局 manifest: {ref['id']}"
        )
    for ref in km.get("shared_templates", []) or []:
        assert ref["id"] in existing, f"template id 不存在: {ref['id']}"
    # 契约内 active knowledge 也必须存在
    for s in _contracts():
        for kid in (s.get("knowledge_ids", {}) or {}).get("active", []) or []:
            assert kid in existing, (
                f"契约 {s['id']} 的 active knowledge {kid} 不存在于全局 manifest"
            )


def test_planned_assets_not_consumed_by_ready_sub_skills() -> None:
    """7. planned asset 不得被 contract_status=ready_for_parallel 的子技能消费。"""
    km = _load(_KM)
    planned_ids = {p["id"] for p in (km.get("planned_assets") or [])}
    if not planned_ids:
        # B1.0 已清零 planned;仍验证逻辑成立(空集天然满足)
        pass
    for s in _contracts():
        if s["contract_status"] != "ready_for_parallel":
            continue
        active = set((s.get("knowledge_ids", {}) or {}).get("active", []) or [])
        consumed_planned = active & planned_ids
        assert not consumed_planned, (
            f"ready_for_parallel 子技能 {s['id']} 消费了 planned 资产: {consumed_planned}"
        )


def test_ready_sub_skills_have_zero_p0_gap() -> None:
    """8. contract_status=ready_for_parallel 的子技能必须 P0 knowledge gap = 0。

    以 knowledge-readiness-matrix.yaml 为 P0 gap 权威来源,
    与契约 contract_status 交叉验证。
    """
    matrix = _load(_READINESS)
    matrix_by_id = {m["id"]: m for m in matrix["sub_skills"]}
    contracts_by_id = {s["id"]: s for s in _contracts()}

    for sid, c in contracts_by_id.items():
        m = matrix_by_id.get(sid)
        assert m is not None, f"知识就绪矩阵缺子技能: {sid}"
        # 契约状态与矩阵状态必须一致
        assert c["contract_status"] == m["contract_status"], (
            f"{sid} 契约状态 {c['contract_status']} 与矩阵 {m['contract_status']} 不一致"
        )
        if c["contract_status"] == "ready_for_parallel":
            assert m["p0_knowledge_gap"] == 0, (
                f"ready_for_parallel 子技能 {sid} 的 P0 gap={m['p0_knowledge_gap']} ≠ 0"
            )
            assert m.get("schema_ready") is True, f"{sid} schema 未就绪却标 ready"
            assert m.get("runtime_deps_ready") is True, (
                f"{sid} 运行时依赖未就绪却标 ready_for_parallel"
            )


def test_brand_creative_does_not_impersonate_ip_rubric() -> None:
    """9. 品牌创意质量资产不得继续直接使用完整 IP Design rubric 冒充。

    - brand-creative 必须有专用 rubric design.quality.brand-identity-quality-rubric。
    - ready_for_parallel / ready_after_upstream 子技能的 quality_gate.rubric_ref
      必须用品牌专用 rubric,不得用 ip-design-quality-rubric。
    """
    existing = {a["id"] for a in _load(_GLOBAL_MANIFEST)["assets"]}
    assert "design.quality.brand-identity-quality-rubric" in existing, (
        "缺品牌专用 rubric"
    )
    for s in _contracts():
        qg = s.get("quality_gate", {}) or {}
        rubric = qg.get("rubric_ref")
        if rubric:
            assert rubric != "design.quality.ip-design-quality-rubric", (
                f"{s['id']} 的 quality_gate 直接用 IP rubric 冒充,必须用品牌专用 rubric"
            )
    # knowledge-manifest 中 ip rubric 只能在 partial_reuse 且 used_by 为空
    km = _load(_KM)
    for ref in km.get("shared_knowledge", []) or []:
        assert ref["id"] != "design.quality.ip-design-quality-rubric", (
            "IP rubric 不得出现在 active shared_knowledge"
        )


def test_no_overpromise_in_brand_creative_docs() -> None:
    """10. 文档中不存在"最终商标可注册""版权清洁""可直接商用"等过度承诺。

    检查 brand-creative 全部文档 + 7 个新知识资产。
    允许否定语境(如"不声称可直接商用")。
    """
    targets: list[Path] = []
    targets.extend(_BC.rglob("*.md"))
    targets.extend(_BC.rglob("*.yaml"))
    # 7 个新知识资产
    for rel in [
        "knowledge/design/strategy/brand-strategy-methodology.md",
        "knowledge/design/visual/logo-design-methodology.md",
        "knowledge/design/visual/color-system-methodology.md",
        "knowledge/design/visual/typography-system-methodology.md",
        "knowledge/design/strategy/brand-audit-methodology.md",
        "knowledge/design/quality/brand-identity-quality-rubric.md",
        "knowledge/design/quality/brand-creative-failure-modes.md",
    ]:
        targets.append(_REPO_ROOT / rel)

    offenders: list[str] = []
    # 否定/反面语境标记:出现这些词说明该行是在"禁止/识别"过度承诺,而非做出承诺
    _NEGATION_MARKERS = (
        "不", "禁", "no ", "not ", "avoid", "越界", "违反", "失败信号",
        "现象:声称", "过度承诺", "声称", "do_not_claim", "返工", "没有",
    )
    for path in targets:
        if "__pycache__" in str(path):
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            for term in _OVERPROMISE_TERMS:
                if term in line:
                    # 允许否定/反面语境(规则定义、失败模式、检查清单)
                    if any(neg in line for neg in _NEGATION_MARKERS):
                        continue
                    offenders.append(f"{path.relative_to(_REPO_ROOT)}: {line.strip()}")
    assert not offenders, "出现过度承诺:\n" + "\n".join(offenders)



def test_producer_consumer_field_level_connectivity() -> None:
    """每条 producer → consumer 边必须至少存在一个同名产物字段。

    检查所有 upstream_contracts 声明的依赖,验证:
    - producer 的 public_outputs + internal_outputs 中至少有一个产物
    - consumer 的 required_inputs + optional_inputs 能匹配上 producer 产物名
    """
    contracts = {s["id"]: s for s in _contracts()}

    disconnected = []
    for cid, c in contracts.items():
        for up_raw in c.get("upstream_contracts", []) or []:
            # upstream_contracts 条目形如 "brand-strategy (可选)" 或 "brand-strategy"
            up_id = up_raw.split()[0].strip()
            if up_id not in contracts:
                continue  # 外部依赖或注释,跳过

            producer = contracts[up_id]
            consumer = c

            # producer 产出
            p_outputs = set()
            for o in (producer.get("public_outputs", []) or []) + (producer.get("internal_outputs", []) or []):
                p_outputs.add(o["name"])

            # consumer 输入
            c_inputs = set()
            for i in (consumer.get("required_inputs", []) or []) + (consumer.get("optional_inputs", []) or []):
                c_inputs.add(i["name"])

            # 检查连通性:consumer 输入能否找到 producer 产出
            matched = p_outputs & c_inputs
            if not matched and p_outputs:
                disconnected.append(
                    f"{up_id} → {cid}: producer 产出 {p_outputs}, "
                    f"consumer 输入 {c_inputs}, 无匹配字段"
                )

    assert not disconnected, "字段级断链:\n" + "\n".join(disconnected)
def test_workflow_input_contracts_static_integrity() -> None:
    """验证 workflow-input-contracts.yaml 的静态契约完整性。

    这是静态集成契约测试,不是运行时测试。检查:
    - 文件存在且可解析
    - 每个 workflow_id 对应的 required_inputs schema_ref 存在
    - 明确声明 runtime_enforced: false
    """
    import yaml
    from pathlib import Path

    wf_input_path = Path("skills/brand-creative/contracts/workflow-input-contracts.yaml")
    assert wf_input_path.is_file(), "workflow-input-contracts.yaml 不存在"

    data = yaml.safe_load(wf_input_path.read_text(encoding="utf-8"))
    assert "schema_version" in data, "缺少 schema_version"
    assert "workflows" in data, "缺少 workflows"

    schemas_dir = Path("skills/brand-creative/contracts/schemas")

    for wf in data["workflows"]:
        assert "workflow_id" in wf, f"{wf} 缺少 workflow_id"
        wf_id = wf["workflow_id"]

        for inp in wf.get("required_inputs", []):
            assert "name" in inp, f"{wf_id} required_inputs 缺少 name"
            assert "runtime_enforced" in inp, f"{wf_id}.{inp['name']} 未声明 runtime_enforced"
            assert inp["runtime_enforced"] is False, (
                f"{wf_id}.{inp['name']} runtime_enforced 必须为 false(当前 Kernel 无强制)"
            )

            schema_ref = inp.get("schema_ref")
            if schema_ref and schema_ref != "null":
                schema_path = schemas_dir / schema_ref.split("/")[-1]
                assert schema_path.is_file(), (
                    f"{wf_id}.{inp['name']} schema_ref={schema_ref} 不存在"
                )


def test_public_output_type_matches_schema_x_output_type() -> None:
    """精确断言: public_output.type == schema["x-output-type"]。

    禁止依靠文件名字符串判断(如 "prompt" in filename)。
    每个 public output 的 schema 必须声明 x-output-type,且必须与 public_output.type 精确匹配。
    internal-only schema 可以不声明 x-output-type。
    """
    import json
    from pathlib import Path

    schemas_dir = Path("skills/brand-creative/contracts/schemas")

    for s in _contracts():
        for o in s.get("public_outputs", []) or []:
            schema_ref = o.get("schema_ref", "")
            if not schema_ref:
                continue

            schema_path = schemas_dir / schema_ref
            assert schema_path.is_file(), f"{s['id']}.{o['name']} schema_ref={schema_ref} 不存在"

            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            assert "x-output-type" in schema, (
                f"{s['id']}.{o['name']} schema {schema_ref} 缺少 x-output-type"
            )

            # 精确匹配
            assert o["type"] == schema["x-output-type"], (
                f"{s['id']}.{o['name']}: public_output.type={o['type']} "
                f"但 schema x-output-type={schema['x-output-type']}(不匹配)"
            )
