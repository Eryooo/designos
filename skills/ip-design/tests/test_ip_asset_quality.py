"""ip-design 资产壳质量测试 — Batch I0 baseline lock。

I0 只建资产壳 + 共享设计决策库,不开发 runtime。本测试锁定:
- 六阶段全覆盖(M01–M06)有对应共享方法论资产。
- shared knowledge manifest 已登记 I0 全部 ip-design 资产。
- skills/ip-design/knowledge-manifest.yaml 引用的 shared id 都存在。
- 通用方法论文件含 10 段专家决策结构(purpose/input_contract/decision_framework/
  expert_heuristics/output_contract/quality_rubric/common_failure_modes/
  senior_review_checklist/examples_to_read/do_not_claim)。
- 6 个产出物模板齐全。
- 每阶段方法论含质量 rubric。
- 失败模式集合 ≥ 5 条(在 common-failure-modes.md 与 visual-translation 等文件中)。
- 项目专属词不入通用方法论(只允许在 cases/ 出现)。
- 不存在过度承诺(production-ready/法务保证/真实研究替代等)。

断言基于真实解析与文件读取,不是字符串拼凑。
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

_REPO_ROOT: Path = Path(__file__).resolve().parents[3]
_KNOWLEDGE: Path = _REPO_ROOT / "knowledge"
_DESIGN: Path = _KNOWLEDGE / "design"
_MANIFEST: Path = _KNOWLEDGE / "manifest.yaml"
_SKILL_ADAPTER: Path = _REPO_ROOT / "skills" / "ip-design" / "knowledge-manifest.yaml"

# 六阶段必须有对应的方法论资产 id
_STAGE_TO_ASSET = {
    "M01": "design.strategy.brand-strategy-alignment",
    "M02": "design.ip.worldview-building",
    "M03_persona": "design.persona.persona-modeling",
    "M03_voice": "design.persona.voice-and-behavior-boundary",
    "M04_visual": "design.visual.visual-translation",
    "M04_prompt": "design.visual.image-prompt-system",
    "M05": "design.ip.content-narrative",
    "M06": "design.ip.brand-material-realization",
}

# 资深决策方法论文件必须含的 10 段
_REQUIRED_DECISION_SECTIONS = (
    "purpose",
    "input_contract",
    "decision_framework",
    "expert_heuristics",
    "output_contract",
    "quality_rubric",
    "common_failure_modes",
    "senior_review_checklist",
    "examples_to_read",
    "do_not_claim",
)

# 6 个产出物模板必须存在
_REQUIRED_TEMPLATES = (
    "design.templates.brand-brief",
    "design.templates.worldview",
    "design.templates.persona-profile",
    "design.templates.visual-spec",
    "design.templates.content-plan",
    "design.templates.brand-material-spec",
)

# 项目专属词黑名单：绝不硬编码进公开仓库（否则测试代码本身成为泄露源）。
# 真实词表只存在于本地私有证据目录（.gitignore 已排除），CI/公开环境缺失时
# 相关测试自动跳过。
_PRIVATE_WORDLIST: Path = (
    _REPO_ROOT / ".designos-private-evidence" / "sensitive-words.txt"
)


def _load_project_specific_terms() -> tuple[str, ...]:
    """从私有词表加载项目专属词；文件缺失返回空（调用方据此 skip）。"""
    if not _PRIVATE_WORDLIST.exists():
        return ()
    terms: list[str] = []
    for line in _PRIVATE_WORDLIST.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        terms.append(s)
    return tuple(terms)


_PROJECT_SPECIFIC_TERMS = _load_project_specific_terms()

# 过度承诺关键词(中英),通用方法论或 SKILL 资产不应出现
_OVERPROMISE_PATTERNS = (
    "production ready",
    "production-ready",
    "可直接商用",
    "可直接发布",
    "保证版权清洁",
    "替代法务",
    "替代真实用户研究",
    "已完成自动化",
    "终稿",
)


def _load_manifest() -> dict:
    return yaml.safe_load(_MANIFEST.read_text(encoding="utf-8"))


def _asset_index() -> dict[str, dict]:
    return {a["id"]: a for a in _load_manifest()["assets"]}


def _strip_source_assets(text: str) -> str:
    return re.sub(r"(?ims)^## source_assets\s*$.*?(?=^##\s+|\Z)", "", text)


def test_six_stages_methodology_assets_registered() -> None:
    """六阶段每个阶段都有对应共享方法论资产登记并文件存在。"""
    assets = _asset_index()
    for stage, aid in _STAGE_TO_ASSET.items():
        assert aid in assets, f"阶段 {stage} 缺少共享方法论资产 id: {aid}"
        sot = _REPO_ROOT / assets[aid]["source_of_truth"]
        assert sot.is_file(), f"{aid} 的 source_of_truth 文件不存在: {sot}"


def test_decision_methodology_files_have_ten_sections() -> None:
    """每个 ip-design 方法论文件必须含 10 段专家决策结构。"""
    methodology_ids = list(_STAGE_TO_ASSET.values()) + ["design.ip.methodology"]
    assets = _asset_index()
    for aid in methodology_ids:
        text = (_REPO_ROOT / assets[aid]["source_of_truth"]).read_text(encoding="utf-8")
        headings = {m.group(1).strip().lower() for m in re.finditer(r"^##\s+(.+?)\s*$", text, re.M)}
        missing = [s for s in _REQUIRED_DECISION_SECTIONS if s not in headings]
        assert not missing, f"{aid} 缺少决策段落: {missing}"


def test_six_templates_registered_and_exist() -> None:
    """6 个产出物模板都登记且文件存在。"""
    assets = _asset_index()
    for tid in _REQUIRED_TEMPLATES:
        assert tid in assets, f"模板未登记: {tid}"
        assert (_REPO_ROOT / assets[tid]["source_of_truth"]).is_file()


def test_quality_rubric_and_failure_modes_exist() -> None:
    """质量门槛四件齐全。"""
    must_have = (
        "design.quality.ip-design-quality-rubric",
        "design.quality.stage-review-checklists",
        "design.quality.common-failure-modes",
        "design.quality.professional-gap-report",
    )
    assets = _asset_index()
    for aid in must_have:
        assert aid in assets, f"质量资产未登记: {aid}"
        assert (_REPO_ROOT / assets[aid]["source_of_truth"]).is_file()


def test_common_failure_modes_has_at_least_five_modes() -> None:
    """common-failure-modes 文件至少列 5 条 F-* 编号失败模式(实际远多于 5)。"""
    path = _REPO_ROOT / "knowledge/design/quality/common-failure-modes.md"
    text = path.read_text(encoding="utf-8")
    matches = re.findall(r"F-[A-Z]{1,3}\d+", text)
    assert len(set(matches)) >= 5, f"failure modes 应 ≥ 5,实际 {len(set(matches))}"


def test_each_stage_methodology_has_its_own_quality_rubric_section() -> None:
    """每阶段方法论自身含 quality_rubric 段(已被 ten-sections 测试覆盖,这里再加一道独立确认)。"""
    for aid in _STAGE_TO_ASSET.values():
        text = (_REPO_ROOT / _asset_index()[aid]["source_of_truth"]).read_text(encoding="utf-8")
        assert re.search(r"^##\s+quality_rubric", text, re.M | re.I), (
            f"{aid} 缺少 quality_rubric 段"
        )


def test_skill_adapter_references_existing_shared_ids() -> None:
    """ip-design adapter 引用的所有 shared id 都存在于 manifest。"""
    existing = set(_asset_index().keys())
    data = yaml.safe_load(_SKILL_ADAPTER.read_text(encoding="utf-8"))
    assert data["skill"] == "ip-design"
    refs = data["shared_knowledge"]
    assert isinstance(refs, list) and refs
    for ref in refs:
        assert ref["id"] in existing, f"adapter 引用了不存在的 shared id: {ref['id']}"
        assert ref.get("used_by"), f"{ref['id']} 缺 used_by"
        assert ref.get("use"), f"{ref['id']} 缺 use"


def test_no_project_specific_terms_in_generic_layer() -> None:
    """通用方法论 / 模板 / 质量文件正文(剔除 source_assets 段)不得含项目专属词。"""
    if not _PROJECT_SPECIFIC_TERMS:
        pytest.skip("私有词表缺失（公开/CI 环境），跳过项目专属词检查")
    offenders: list[str] = []
    target_dirs = [
        _DESIGN / "ip",
        _DESIGN / "strategy",
        _DESIGN / "persona",
        _DESIGN / "visual",
        _DESIGN / "quality",
        _DESIGN / "templates",
    ]
    for d in target_dirs:
        for md in d.glob("*.md"):
            text = _strip_source_assets(md.read_text(encoding="utf-8"))
            for term in _PROJECT_SPECIFIC_TERMS:
                if term in text:
                    offenders.append(f"{md.relative_to(_REPO_ROOT)} 含专属词 '{term}'")
    assert not offenders, "通用层出现项目专属词:\n" + "\n".join(offenders)


def test_cases_directory_has_no_private_evidence() -> None:
    """脱敏后 cases/ 不得含真实项目证据。

    历史上 cases/ 存放真实项目案例（含项目专属词），已在脱敏阶段删除。
    合成案例尚未重建。本测试锁定：要么 cases/ 不存在，要么其中任何文件
    都不含项目专属词（只允许合成案例）。"""
    cases_dir = _DESIGN / "cases"
    if not cases_dir.exists():
        return  # cases/ 已移除，待用合成案例重建
    if not _PROJECT_SPECIFIC_TERMS:
        pytest.skip("私有词表缺失（公开/CI 环境），跳过 cases 证据检查")
    offenders: list[str] = []
    for md in cases_dir.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        for term in _PROJECT_SPECIFIC_TERMS:
            if term in text:
                offenders.append(f"{md.relative_to(_REPO_ROOT)} 含项目专属词 '{term}'")
    assert not offenders, "cases/ 不得含真实证据，只能放合成案例:\n" + "\n".join(offenders)


def test_no_overpromise_in_generic_layer_or_skill_shell() -> None:
    """通用方法论与 ip-design 资产壳不应含过度承诺词。"""
    offenders: list[str] = []
    targets: list[Path] = []
    for d in (_DESIGN / "ip", _DESIGN / "strategy", _DESIGN / "persona",
              _DESIGN / "visual", _DESIGN / "quality", _DESIGN / "templates"):
        targets.extend(d.glob("*.md"))
    targets.append(_SKILL_ADAPTER)
    targets.append(_REPO_ROOT / "skills/ip-design/reference/README.md")
    for path in targets:
        text = path.read_text(encoding="utf-8")
        for pat in _OVERPROMISE_PATTERNS:
            # 只命中肯定语境;允许 "不替代法务" 这类否定形式存在
            if pat in text:
                # 简单上下文判断:如果在同一行有"不"或"do_not"前缀则放行
                for line in text.splitlines():
                    if pat in line:
                        if any(neg in line for neg in ("不", "非", "do not", "do_not", "no ")):
                            continue
                        offenders.append(f"{path.relative_to(_REPO_ROOT)} 含过度承诺片段:'{line.strip()}'")
    assert not offenders, "出现过度承诺:\n" + "\n".join(offenders)


def test_mbti_is_aux_only_in_persona_modeling() -> None:
    """persona-modeling 不能写'必须基于 MBTI'之类的唯一依赖句式。"""
    text = (_REPO_ROOT / "knowledge/design/persona/persona-modeling.md").read_text(encoding="utf-8")
    bad_phrases = ("必须基于 MBTI", "仅依赖 MBTI", "MBTI 是唯一", "唯一基于 MBTI")
    found = [p for p in bad_phrases if p in text]
    assert not found, f"persona-modeling 出现 MBTI 唯一依赖句式: {found}"
    # 同时确认存在"辅助"或"行为模式"等关键词
    assert "辅助" in text and "行为模式" in text, "persona-modeling 应明确 MBTI 仅辅助、行为模式为主"
