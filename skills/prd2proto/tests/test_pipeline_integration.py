"""Pipeline-loader smoke tests for the scaffolded skill."""

from __future__ import annotations

from pathlib import Path

from kernel.skill_loader.pipeline_loader import load_pipeline_skill


def test_skill_dir_is_kernel_loadable(skill_dir: Path) -> None:
    skill = load_pipeline_skill(skill_dir)
    assert skill.config.name
    assert skill.get_stages(), "pipeline.yaml produced no stages"


def test_pipeline_yaml_exists(skill_dir: Path) -> None:
    assert (skill_dir / "pipeline.yaml").exists()
