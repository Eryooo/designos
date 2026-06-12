"""Test that all B1.1 sub-skill pipeline stages use only valid StageConfig fields.

Prevents silent field dropping when unknown fields are added to stage YAML.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from kernel.contracts.schemas import StageConfig


def _load_pipeline_yaml(path: Path) -> dict:
    """Load and parse a pipeline.yaml file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _get_valid_stage_fields() -> set[str]:
    """Get the set of valid StageConfig fields."""
    return set(StageConfig.model_fields.keys())


@pytest.mark.parametrize(
    "pipeline_path",
    [
        "skills/brand-creative/sub-skills/competitive-analysis/pipeline.yaml",
        "skills/brand-creative/sub-skills/brand-strategy/pipeline.yaml",
    ],
)
def test_stage_fields_are_valid(pipeline_path: str) -> None:
    """All stage fields must be in StageConfig.model_fields to avoid silent dropping."""
    repo_root = Path(__file__).parent.parent.parent
    pipeline_file = repo_root / pipeline_path
    assert pipeline_file.exists(), f"pipeline not found: {pipeline_file}"

    pipeline = _load_pipeline_yaml(pipeline_file)
    stages = pipeline.get("stages", [])
    assert stages, f"no stages in {pipeline_path}"

    valid_fields = _get_valid_stage_fields()

    for i, stage in enumerate(stages):
        stage_id = stage.get("id", f"stage-{i}")
        stage_fields = set(stage.keys())

        unknown_fields = stage_fields - valid_fields
        assert not unknown_fields, (
            f"{pipeline_path} stage '{stage_id}' has unknown fields: {unknown_fields}. "
            f"Valid fields: {valid_fields}. "
            f"Unknown fields are silently dropped by StageConfig, causing runtime confusion."
        )


def test_valid_stage_fields_list() -> None:
    """Document the expected valid StageConfig fields for reference."""
    valid = _get_valid_stage_fields()

    # As of B1.1, these are the valid fields
    expected = {
        "id", "type", "prompt", "mcp_server", "mcp_tool",
        "inputs", "outputs", "knowledge",
        "only_when", "checkpoint", "gate", "retry",
    }

    assert valid == expected, (
        f"StageConfig fields changed. Expected: {expected}, got: {valid}. "
        f"If this is intentional, update this test."
    )
