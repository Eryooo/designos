"""Unit tests for kernel.skill_loader."""

from __future__ import annotations

from pathlib import Path

import yaml

from kernel.contracts.enums import SkillType
from kernel.skill_loader import (
    SkillLoader,
    load_pipeline_skill,
    load_skill_group,
    parse_frontmatter,
)


def _make_pipeline_skill(root: Path, name: str = "uxeval") -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "version: 1.0.0\n"
        "type: pipeline\n"
        "modes:\n"
        "  - id: web\n"
        "  - id: client\n"
        "requires:\n"
        "  kernel: \">=1.0.0,<2.0.0\"\n"
        "---\n"
        "# body\n",
        encoding="utf-8",
    )
    pipeline = {
        "name": f"{name}-pipeline",
        "version": "1.0.0",
        "stages": [
            {
                "id": "stage-1",
                "type": "llm",
                "prompt": "prompts/p1.md",
                "inputs": [],
                "outputs": ["x"],
                "knowledge": [],
            }
        ],
    }
    (skill_dir / "pipeline.yaml").write_text(yaml.safe_dump(pipeline), encoding="utf-8")
    (skill_dir / "prompts").mkdir(exist_ok=True)
    (skill_dir / "prompts" / "p1.md").write_text("body", encoding="utf-8")
    return skill_dir


def test_parse_frontmatter(tmp_path: Path) -> None:
    p = tmp_path / "SKILL.md"
    p.write_text(
        "---\nname: x\nversion: 1.0.0\n---\nbody\n", encoding="utf-8"
    )
    fm, body = parse_frontmatter(p)
    assert fm["name"] == "x"
    assert body.startswith("body")


def test_load_pipeline_skill(tmp_path: Path) -> None:
    skill_dir = _make_pipeline_skill(tmp_path)
    skill = load_pipeline_skill(skill_dir)
    assert skill.name == "uxeval"
    assert skill.skill_type is SkillType.PIPELINE
    assert skill.config.supported_modes == ["web", "client"]
    stages = skill.get_stages()
    assert len(stages) == 1
    assert stages[0].id == "stage-1"
    assert stages[0].prompt is not None
    assert stages[0].prompt.exists()


def test_skill_loader_lists_and_loads(tmp_path: Path) -> None:
    _make_pipeline_skill(tmp_path, "uxeval")
    _make_pipeline_skill(tmp_path, "prd2proto")
    loader = SkillLoader([tmp_path])
    assert loader.list_available() == ["prd2proto", "uxeval"]
    skill = loader.load("uxeval")
    assert skill.name == "uxeval"


def test_load_skill_group(tmp_path: Path) -> None:
    group_dir = tmp_path / "brand-creative"
    group_dir.mkdir()
    skills_dir = group_dir / "skills"
    skills_dir.mkdir()
    _make_pipeline_skill(skills_dir, "competitor")
    workflows = group_dir / "workflows"
    workflows.mkdir()
    workflow_yaml = workflows / "wf.yaml"
    workflow_yaml.write_text(
        yaml.safe_dump(
            {
                "name": "wf",
                "description": "test",
                "steps": [
                    {"type": "sequential", "sub_skills": ["competitor"]},
                ],
            }
        ),
        encoding="utf-8",
    )
    (group_dir / "GROUP.md").write_text(
        "---\n"
        "name: brand-creative\n"
        "version: 1.0.0\n"
        "type: group\n"
        "sub_skills:\n"
        "  - id: competitor\n"
        "    path: skills/competitor/SKILL.md\n"
        "workflows:\n"
        "  - id: wf\n"
        "    file: workflows/wf.yaml\n"
        "---\n",
        encoding="utf-8",
    )
    group = load_skill_group(group_dir)
    assert group.skill_type is SkillType.GROUP
    assert group.list_sub_skills() == ["competitor"]
    wf = group.get_workflow("wf")
    assert wf is not None
    assert wf.steps[0].sub_skills == ["competitor"]
