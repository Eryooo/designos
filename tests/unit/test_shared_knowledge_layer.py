"""共享知识层（knowledge/）结构测试 — Batch K1 retrofit lock。

K1 把已有 skill 的 reference/templates/eval 中可复用的资深决策知识反抽到
knowledge/，并让旧 skill 只通过 knowledge-manifest.yaml 引用 shared knowledge id。
这些测试锁定：
- shared manifest 存在、五个 domain 覆盖完整、stable id 唯一
- K1 指定的 23 个共享知识资产都在 manifest 中登记，且 source_of_truth 存在
- 每个共享知识文件都包含 purpose/applies_to/decision_framework/senior_heuristics/
  quality_rubric/common_failure_modes/source_assets/do_not_claim 八段
- 三个旧 skill 的 knowledge-manifest.yaml 引用的 id 都存在
- 三个旧 skill 的核心 output_type 未改变
- 通用知识正文不得夹带 skill 专属词；source_assets 段允许保留来源路径
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

_REPO_ROOT: Path = Path(__file__).resolve().parents[2]
_KNOWLEDGE: Path = _REPO_ROOT / "knowledge"
_MANIFEST: Path = _KNOWLEDGE / "manifest.yaml"
_EXPECTED_DOMAINS = {"design", "ux", "product", "frontend", "research"}
_SKILL_SPECIFIC_TERMS = ("uxeval", "prd2proto", "ai-analytics", "design-acceptance")
_REQUIRED_ASSET_FIELDS = (
    "id",
    "version",
    "domain",
    "type",
    "applicable_skills",
    "source_of_truth",
    "decision_use",
    "quality_bar",
    "do_not_claim",
    "owner",
    "status",
)
_REQUIRED_KNOWLEDGE_SECTIONS = (
    "purpose",
    "applies_to",
    "decision_framework",
    "senior_heuristics",
    "quality_rubric",
    "common_failure_modes",
    "source_assets",
    "do_not_claim",
)
_REQUIRED_K1_IDS = {
    "ux.heuristic-principles",
    "ux.journey-modeling",
    "ux.evidence-quality",
    "ux.severity-rubric",
    "ux.issue-attribution",
    "ux.ux-failure-modes",
    "product.prd-understanding",
    "product.information-architecture",
    "product.user-story-mapping",
    "product.interaction-state-coverage",
    "frontend.atomic-design",
    "frontend.design-token-rules",
    "frontend.component-state-rules",
    "frontend.code-quality-constitution",
    "research.methodology-selection",
    "research.competitor-analysis",
    "research.user-persona-quality",
    "research.data-completeness-rubric",
    "design.design-strategy",
    "design.design-template-selection",
    "design.tone-and-visual-direction",
}
_ID_PATTERN = re.compile(r"^[a-z]+(\.[a-z0-9-]+)+$")
_VALID_STATUS = {"draft", "pilot", "stable"}
_EXPECTED_OUTPUT_TYPES = {
    "uxeval": {
        "user_journey",
        "task_checklist",
        "delivery_audit_bundle",
        "issue_report",
        "html_report",
        "evidence_pack",
    },
    "prd2proto": {
        "prototype_code",
        "frontend_code",
        "design_tokens",
        "information_architecture",
        "component_spec",
    },
    "ai-analytics": {
        "analysis_report",
        "design_strategy",
        "user_persona",
        "comparison_matrix",
    },
}


def _load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path} 顶层必须是 mapping"
    return data


def _load_manifest() -> dict:
    assert _MANIFEST.is_file(), f"共享层 manifest 缺失: {_MANIFEST}"
    return _load_yaml(_MANIFEST)


def _asset_ids() -> set[str]:
    return {asset["id"] for asset in _load_manifest()["assets"]}


def _strip_source_assets_section(text: str) -> str:
    """专属词红线检查跳过 source_assets 段，因为来源路径必须保留旧 skill 名。"""
    return re.sub(
        r"(?ims)^## source_assets\s*$.*?(?=^##\s+|\Z)",
        "",
        text,
    )


def test_manifest_exists_and_parses() -> None:
    data = _load_manifest()
    assert data.get("layer") == "shared-knowledge"
    assert isinstance(data.get("assets"), list) and data["assets"], "assets 必须是非空列表"


def test_five_domains_declared_and_covered() -> None:
    data = _load_manifest()
    declared = set(data.get("domains") or [])
    assert declared == _EXPECTED_DOMAINS
    covered = {asset["domain"] for asset in data["assets"]}
    assert _EXPECTED_DOMAINS <= covered
    for domain in _EXPECTED_DOMAINS:
        assert (_KNOWLEDGE / domain).is_dir(), f"缺少 domain 目录: knowledge/{domain}"


def test_required_k1_assets_are_registered() -> None:
    missing = _REQUIRED_K1_IDS - _asset_ids()
    assert not missing, f"K1 必需 shared knowledge id 未登记: {sorted(missing)}"


def test_every_asset_has_stable_unique_id_and_required_fields() -> None:
    data = _load_manifest()
    known_skills = set(data.get("known_skills") or [])
    seen: set[str] = set()
    for asset in data["assets"]:
        for field in _REQUIRED_ASSET_FIELDS:
            assert field in asset and asset[field] not in (None, "", []), (
                f"资产 {asset.get('id')} 缺少字段或为空: {field}"
            )
        aid = asset["id"]
        assert _ID_PATTERN.match(aid), f"id 不符合 <domain>.<slug> 规范: {aid}"
        assert aid not in seen, f"id 重复，不唯一: {aid}"
        seen.add(aid)
        assert aid.split(".", 1)[0] == asset["domain"]
        assert asset["domain"] in _EXPECTED_DOMAINS
        assert asset["status"] in _VALID_STATUS
        for skill in asset["applicable_skills"]:
            assert skill in known_skills, f"资产 {aid} 引用了未登记 skill: {skill}"


def test_source_of_truth_files_exist_and_match_domain() -> None:
    for asset in _load_manifest()["assets"]:
        sot = asset["source_of_truth"]
        assert sot.startswith(f"knowledge/{asset['domain']}/"), (
            f"资产 {asset['id']} 的 source_of_truth 未落在其 domain 目录下: {sot}"
        )
        assert (_REPO_ROOT / sot).is_file(), f"source_of_truth 不存在: {sot}"


def test_k1_shared_knowledge_files_have_decision_sections() -> None:
    by_id = {asset["id"]: asset for asset in _load_manifest()["assets"]}
    for aid in _REQUIRED_K1_IDS:
        text = (_REPO_ROOT / by_id[aid]["source_of_truth"]).read_text(encoding="utf-8")
        headings = {m.group(1).strip().lower() for m in re.finditer(r"^##\s+(.+)$", text, re.M)}
        missing = set(_REQUIRED_KNOWLEDGE_SECTIONS) - headings
        assert not missing, f"{aid} 缺少知识段落: {sorted(missing)}"


def test_generic_decision_body_has_no_skill_specific_terms_outside_source_assets() -> None:
    offenders: list[str] = []
    for asset in _load_manifest()["assets"]:
        path = _REPO_ROOT / asset["source_of_truth"]
        text = _strip_source_assets_section(path.read_text(encoding="utf-8").lower())
        for term in _SKILL_SPECIFIC_TERMS:
            if term in text:
                offenders.append(f"{path.relative_to(_REPO_ROOT)} 的通用正文含专属词 '{term}'")
    assert not offenders, "通用正文出现 skill 专属词:\n" + "\n".join(offenders)


def test_skill_knowledge_manifests_reference_existing_shared_ids() -> None:
    existing = _asset_ids()
    for skill in ("uxeval", "prd2proto", "ai-analytics"):
        path = _REPO_ROOT / "skills" / skill / "knowledge-manifest.yaml"
        assert path.is_file(), f"缺少 skill adapter: {path}"
        data = _load_yaml(path)
        assert data["skill"] == skill
        refs = data.get("shared_knowledge")
        assert isinstance(refs, list) and refs, f"{skill} adapter 必须引用至少一个 shared id"
        for ref in refs:
            assert ref["id"] in existing, f"{skill} 引用了不存在的 shared id: {ref['id']}"
            assert "used_by" in ref and ref["used_by"], f"{skill}:{ref['id']} 缺 used_by"
            assert "use" in ref and ref["use"], f"{skill}:{ref['id']} 缺 use"


def test_core_output_types_of_existing_skills_are_unchanged() -> None:
    from kernel.skill_loader import parse_frontmatter

    for skill, expected in _EXPECTED_OUTPUT_TYPES.items():
        fm, _body = parse_frontmatter(_REPO_ROOT / "skills" / skill / "SKILL.md")
        actual = {entry["type"] for entry in fm["outputs"]}
        assert actual == expected, f"{skill} output_type 改变: {actual} != {expected}"
