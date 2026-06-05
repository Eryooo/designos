"""brand-creative Skill Group 架构基线测试 — Batch B0 baseline lock。

锁定 brand-creative Skill Group 的架构契约:
- GROUP.md 存在,frontmatter type=group,声明 13 子技能 + 4 workflows
- 13 个子技能目录存在且有占位 README
- 4 个 workflow yaml 存在且结构合法(steps 含 sequential/parallel)
- workflow 引用的 sub_skills 都在 GROUP.md 声明的子技能内
- knowledge-manifest.yaml 引用的 shared id 都存在于全局 manifest
- kernel 能加载这个 Skill Group(load_skill_group 不报错)
- 并行 workflow 的 sub_skills 互不依赖(架构契约:并行组内无依赖)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

_REPO_ROOT: Path = Path(__file__).resolve().parents[3]
_GROUP_DIR: Path = _REPO_ROOT / "skills" / "brand-creative"
_GROUP_MD: Path = _GROUP_DIR / "GROUP.md"
_KNOWLEDGE_MANIFEST: Path = _GROUP_DIR / "knowledge-manifest.yaml"
_SHARED_MANIFEST: Path = _REPO_ROOT / "knowledge" / "manifest.yaml"

_EXPECTED_SUB_SKILLS = {
    "brand-strategy", "competitive-analysis",
    "logo-design", "color-system", "typography-system", "visual-identity",
    "brand-voice", "content-strategy", "campaign-creative",
    "brand-collateral", "digital-assets", "brand-guidelines", "brand-audit",
}
_EXPECTED_WORKFLOWS = {
    "full-brand-identity", "logo-vi-fast-track", "brand-refresh", "campaign-sprint",
}


def _parse_group_frontmatter() -> dict:
    """解析 GROUP.md 的 YAML frontmatter。"""
    text = _GROUP_MD.read_text(encoding="utf-8")
    assert text.startswith("---"), "GROUP.md 必须以 frontmatter 开头"
    _, fm_block, _ = text.split("---", 2)
    return yaml.safe_load(fm_block)


def test_group_md_exists_and_is_group_type() -> None:
    """GROUP.md 存在且 type=group。"""
    assert _GROUP_MD.is_file(), "GROUP.md 缺失"
    fm = _parse_group_frontmatter()
    assert fm.get("type") == "group", f"type 应为 group,实际 {fm.get('type')}"
    assert fm.get("name") == "brand-creative"


def test_group_declares_thirteen_sub_skills() -> None:
    """GROUP.md 声明 13 个子技能,id 与预期一致。"""
    fm = _parse_group_frontmatter()
    sub_skills = fm.get("sub_skills") or []
    assert len(sub_skills) == 13, f"应有 13 个子技能,实际 {len(sub_skills)}"
    declared_ids = {s["id"] for s in sub_skills}
    assert declared_ids == _EXPECTED_SUB_SKILLS, (
        f"子技能 id 不匹配:多 {declared_ids - _EXPECTED_SUB_SKILLS},"
        f"少 {_EXPECTED_SUB_SKILLS - declared_ids}"
    )


def test_group_declares_four_workflows() -> None:
    """GROUP.md 声明 4 个 workflow。"""
    fm = _parse_group_frontmatter()
    workflows = fm.get("workflows") or []
    assert len(workflows) == 4, f"应有 4 个 workflow,实际 {len(workflows)}"
    declared = {w["id"] for w in workflows}
    assert declared == _EXPECTED_WORKFLOWS, f"workflow id 不匹配:{declared}"


def test_all_sub_skill_dirs_exist_with_readme() -> None:
    """13 个子技能目录存在且有占位 README。"""
    for sub_id in _EXPECTED_SUB_SKILLS:
        sub_dir = _GROUP_DIR / "sub-skills" / sub_id
        assert sub_dir.is_dir(), f"子技能目录缺失: {sub_id}"
        assert (sub_dir / "README.md").is_file(), f"{sub_id} 缺占位 README"


def test_sub_skill_paths_in_group_md_resolve() -> None:
    """GROUP.md 声明的子技能 path 都真实存在。

    B1.1 起 path 指向 sub-skills/<id>/SKILL.md(file),Kernel 从此解析 pipeline skill。
    兼容三种状态:
    - path 指向 SKILL.md 文件且文件存在(已实现子技能):assert path.is_file()
    - path 指向 SKILL.md 文件但子技能仅占位:父目录必须存在且有 README.md
    - path 指向目录(legacy 格式):assert path.is_dir() 且目录下有 SKILL.md
    """
    fm = _parse_group_frontmatter()
    for entry in fm["sub_skills"]:
        sub_id = entry["id"]
        path = _GROUP_DIR / entry["path"]
        if path.suffix == ".md":
            assert path.name == "SKILL.md", f"path 必须指向 SKILL.md: {entry['path']}"
            parent = path.parent
            assert parent.is_dir(), f"子技能目录缺失: {sub_id}"
            if path.is_file():
                # 已实现子技能:SKILL.md 必须可加载为 PipelineSkill
                continue
            # 占位子技能:父目录必须有 README.md
            assert (parent / "README.md").is_file(), (
                f"占位子技能 {sub_id} 必须有 README.md: {parent}"
            )
        else:
            assert path.is_dir(), f"子技能目录不存在: {entry['path']}"
            assert (path / "SKILL.md").is_file() or (path / "README.md").is_file(), (
                f"子技能 {sub_id} 目录下缺 SKILL.md 或 README.md"
            )


def test_implemented_sub_skills_loadable_via_skill_loader() -> None:
    """B1.1.2: SkillLoader.load("brand-creative:<sub-id>") 真实加载已实现的子技能。

    本批仅 brand-strategy 和 competitive-analysis 已实现;其余子技能仅占位 README,
    不要求 loadable。
    """
    from kernel.skill_loader import SkillLoader

    loader = SkillLoader([_REPO_ROOT / "skills"])

    for sub_id in ("brand-strategy", "competitive-analysis"):
        skill = loader.load(f"brand-creative:{sub_id}")
        assert skill is not None, f"SkillLoader 无法加载 brand-creative:{sub_id}"
        # 真实加载产生 PipelineSkill,有 stages
        assert hasattr(skill, "get_stages"), f"{sub_id} 加载结果不是 PipelineSkill"
        assert len(skill.get_stages()) > 0, f"{sub_id} 没有 stages"


def test_workflow_files_exist_and_valid() -> None:
    """4 个 workflow yaml 存在且结构合法(name/description/steps)。"""
    fm = _parse_group_frontmatter()
    for entry in fm["workflows"]:
        wf_path = _GROUP_DIR / entry["file"]
        assert wf_path.is_file(), f"workflow 文件缺失: {entry['file']}"
        data = yaml.safe_load(wf_path.read_text(encoding="utf-8"))
        assert data.get("name"), f"{entry['file']} 缺 name"
        assert data.get("description"), f"{entry['file']} 缺 description"
        steps = data.get("steps") or []
        assert steps, f"{entry['file']} 缺 steps"
        for step in steps:
            assert step["type"] in ("sequential", "parallel"), (
                f"{entry['file']} step type 非法: {step['type']}"
            )
            assert step.get("sub_skills"), f"{entry['file']} step 缺 sub_skills"


def test_workflow_sub_skills_are_declared_in_group() -> None:
    """workflow 引用的 sub_skills 都在 GROUP.md 声明的子技能内。"""
    fm = _parse_group_frontmatter()
    for entry in fm["workflows"]:
        wf_path = _GROUP_DIR / entry["file"]
        data = yaml.safe_load(wf_path.read_text(encoding="utf-8"))
        for step in data["steps"]:
            for sub in step["sub_skills"]:
                assert sub in _EXPECTED_SUB_SKILLS, (
                    f"{entry['file']} 引用了未声明的子技能: {sub}"
                )


def test_knowledge_manifest_references_existing_shared_ids() -> None:
    """knowledge-manifest 的 active shared_knowledge 引用的 id 都存在于全局 manifest。

    planned_assets 中的 id 可以暂不存在(status: planned)。
    active 与 planned 不得重叠。
    """
    shared = yaml.safe_load(_SHARED_MANIFEST.read_text(encoding="utf-8"))
    existing_ids = {a["id"] for a in shared["assets"]}
    km = yaml.safe_load(_KNOWLEDGE_MANIFEST.read_text(encoding="utf-8"))
    assert km["skill"] == "brand-creative"

    # active shared_knowledge 的 id 必须全部存在
    active_ids = set()
    for ref in km.get("shared_knowledge", []):
        assert ref["id"] in existing_ids, f"引用了不存在的 shared id: {ref['id']}"
        assert ref.get("used_by"), f"{ref['id']} 缺 used_by"
        active_ids.add(ref["id"])
    for ref in km.get("shared_templates", []):
        assert ref["id"] in existing_ids, f"引用了不存在的 template id: {ref['id']}"
        active_ids.add(ref["id"])

    # planned_assets 的 id 可以暂不存在,且必须标 status: planned
    planned_ids = set()
    for ref in km.get("planned_assets", []):
        assert ref.get("status") == "planned", (
            f"planned_assets 中的 {ref['id']} 必须标 status: planned"
        )
        assert ref.get("needed_by"), f"planned asset {ref['id']} 缺 needed_by"
        planned_ids.add(ref["id"])

    # active 与 planned 不得重叠
    overlap = active_ids & planned_ids
    assert not overlap, f"active 与 planned 重叠: {overlap}"


def test_kernel_can_load_skill_group() -> None:
    """kernel 能加载这个 Skill Group(load_skill_group 不报错)。"""
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    from kernel.skill_loader.group_loader import load_skill_group

    group = load_skill_group(_GROUP_DIR)
    assert group.name == "brand-creative"
    assert group.skill_type.value == "group"
    # 13 子技能都被解析
    assert len(group.list_sub_skills()) == 13
    assert set(group.list_sub_skills()) == _EXPECTED_SUB_SKILLS
    # 4 workflow 都被解析
    for wf_id in _EXPECTED_WORKFLOWS:
        assert group.get_workflow(wf_id) is not None, f"workflow {wf_id} 未加载"


def test_parallel_steps_have_no_known_dependencies() -> None:
    """并行 workflow step 内的子技能互不依赖(架构契约)。

    依赖关系硬约束:visual-identity 依赖 logo/color/typography;
    brand-guidelines 依赖几乎所有;campaign-creative 依赖 visual-identity。
    这些"汇总型"子技能绝不能与其依赖项放在同一个 parallel step。

    生产者/消费者约束:competitive-analysis 产出 competitor_matrix,
    brand-strategy 消费之。生产者与消费者绝不能放在同一 parallel step。
    """
    # 汇总型子技能 → 其依赖项(不能与依赖项同 parallel step)
    aggregators = {
        "visual-identity": {"logo-design", "color-system", "typography-system"},
        "campaign-creative": {"visual-identity", "brand-voice"},
        "brand-guidelines": {
            "brand-strategy", "visual-identity", "brand-voice",
            "content-strategy", "brand-collateral", "digital-assets",
        },
    }
    # 生产者 → 消费者(不能与消费者同 parallel step)
    producer_consumer = {
        "competitive-analysis": {"brand-strategy"},  # competitive-analysis 产出被 brand-strategy 消费
    }

    fm = _parse_group_frontmatter()
    for entry in fm["workflows"]:
        wf_path = _GROUP_DIR / entry["file"]
        data = yaml.safe_load(wf_path.read_text(encoding="utf-8"))
        for step_idx, step in enumerate(data["steps"]):
            if step["type"] != "parallel":
                continue
            members = set(step["sub_skills"])

            # 检查汇总型不与依赖项同 parallel
            for agg, deps in aggregators.items():
                if agg in members:
                    conflict = members & deps
                    assert not conflict, (
                        f"{entry['file']} step {step_idx} 把汇总型 {agg} "
                        f"与其依赖 {conflict} 放在同一并行组,违反依赖契约"
                    )

            # 检查生产者不与消费者同 parallel
            for producer, consumers in producer_consumer.items():
                if producer in members:
                    conflict = members & consumers
                    assert not conflict, (
                        f"{entry['file']} step {step_idx} 把生产者 {producer} "
                        f"与消费者 {conflict} 放在同一并行组,违反生产者/消费者契约"
                    )


def test_competitive_analysis_before_brand_strategy_when_enabled() -> None:
    """competitive-analysis 启用时,必须位于 brand-strategy 之前(运行时依赖顺序)。

    检查 full-brand-identity / campaign-sprint workflow:
    - competitive-analysis 若出现,必须在 brand-strategy 之前的 step。
    - 或 competitive-analysis 在 brand-strategy 之前的 sequential step。
    """
    fm = _parse_group_frontmatter()
    target_workflows = {"full-brand-identity", "campaign-sprint"}

    for entry in fm["workflows"]:
        if entry["id"] not in target_workflows:
            continue

        wf_path = _GROUP_DIR / entry["file"]
        data = yaml.safe_load(wf_path.read_text(encoding="utf-8"))

        comp_idx = None
        brand_idx = None
        for idx, step in enumerate(data["steps"]):
            if "competitive-analysis" in step["sub_skills"]:
                comp_idx = idx
            if "brand-strategy" in step["sub_skills"]:
                brand_idx = idx

        # full-brand-identity / campaign-sprint 中两者都必须出现
        assert comp_idx is not None, f"{entry['file']} 缺 competitive-analysis"
        assert brand_idx is not None, f"{entry['file']} 缺 brand-strategy"

        # competitive-analysis 必须在 brand-strategy 之前
        assert comp_idx < brand_idx, (
            f"{entry['file']} 中 competitive-analysis(step {comp_idx}) "
            f"必须在 brand-strategy(step {brand_idx}) 之前"
        )


def test_visual_identity_after_all_three_upstream_present() -> None:
    """visual-identity 出现时,必须确认 logo-design / color-system / typography-system
    三者全部出现,且全部位于 visual-identity 前;不是只检查任意一个。
    """
    fm = _parse_group_frontmatter()
    required_upstream = {"logo-design", "color-system", "typography-system"}

    for entry in fm["workflows"]:
        wf_path = _GROUP_DIR / entry["file"]
        data = yaml.safe_load(wf_path.read_text(encoding="utf-8"))

        # 找 visual-identity 出现的 step
        vi_idx = None
        for idx, step in enumerate(data["steps"]):
            if "visual-identity" in step["sub_skills"]:
                vi_idx = idx
                break

        if vi_idx is None:
            continue   # workflow 不含 visual-identity,跳过

        # visual-identity 出现时,记录三个上游各自最后出现的 step idx
        upstream_last_idx = {up: None for up in required_upstream}
        for idx, step in enumerate(data["steps"]):
            for up in required_upstream:
                if up in step["sub_skills"]:
                    upstream_last_idx[up] = idx

        # 三者必须全部出现
        missing = [up for up, i in upstream_last_idx.items() if i is None]
        assert not missing, (
            f"{entry['file']} 含 visual-identity 但缺少上游: {missing} "
            f"(visual-identity 必须依赖 logo-design + color-system + typography-system 三者全部完成)"
        )

        # 三者必须全部位于 visual-identity 前
        late_upstream = [up for up, i in upstream_last_idx.items() if i >= vi_idx]
        assert not late_upstream, (
            f"{entry['file']} 中 {late_upstream} 出现在 visual-identity(step {vi_idx})"
            f"之后或同步,违反汇总型依赖契约"
        )


def test_workflow_yaml_has_no_unknown_fields_silently_dropped() -> None:
    """Runtime truth: YAML 中的字段不能被 WorkflowConfig 静默丢弃。

    防止 P0 复发:WorkflowStep 模型不支持的字段(如 when/condition)被 Pydantic
    静默忽略,导致 YAML 声明的语义与运行时不一致。本测试直接比对 YAML 原始
    字段集合与模型支持字段集合,任何未知字段视为不一致。
    """
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    from kernel.contracts.schemas import WorkflowConfig, WorkflowStep

    workflow_step_known_fields = set(WorkflowStep.model_fields.keys())
    workflow_known_fields = set(WorkflowConfig.model_fields.keys())

    fm = _parse_group_frontmatter()
    for entry in fm["workflows"]:
        wf_path = _GROUP_DIR / entry["file"]
        raw_yaml = yaml.safe_load(wf_path.read_text(encoding="utf-8"))

        # 检查 workflow 顶层字段
        unknown_top = set(raw_yaml.keys()) - workflow_known_fields
        assert not unknown_top, (
            f"{entry['file']} 顶层含未知字段(将被 WorkflowConfig 静默丢弃): "
            f"{unknown_top}"
        )

        # 检查每个 step 字段
        for idx, step in enumerate(raw_yaml.get("steps", [])):
            unknown_step = set(step.keys()) - workflow_step_known_fields
            assert not unknown_step, (
                f"{entry['file']} step {idx} 含未知字段(将被 WorkflowStep 静默丢弃): "
                f"{unknown_step}。WorkflowOrchestrator 不会执行这些字段的语义,"
                f"YAML 声明与运行时行为不一致"
            )

        # 进一步确认:加载后 model_dump 与 YAML 原始字段集合一致
        wf = WorkflowConfig.model_validate(raw_yaml)
        dumped = wf.model_dump()
        for idx, (raw_step, dumped_step) in enumerate(
            zip(raw_yaml["steps"], dumped["steps"])
        ):
            raw_keys = set(raw_step.keys())
            dumped_keys = set(dumped_step.keys())
            dropped = raw_keys - dumped_keys
            assert not dropped, (
                f"{entry['file']} step {idx} 字段被静默丢弃: {dropped} "
                f"(raw YAML: {raw_keys},model_dump: {dumped_keys})"
            )
