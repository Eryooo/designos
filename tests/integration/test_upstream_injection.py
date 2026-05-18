"""Integration tests: upstream run product injection.

Simulates runs/001-ai-analytics/ having artifacts, then verifies that
runs/002-prd2proto/ receives upstream_data correctly injected.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest
import yaml

from kernel.contracts.enums import OutputType, RunStatus, SkillType, StageType
from kernel.contracts.schemas import (
    ArtifactRef,
    DesignOSConfig,
    GlobalConfig,
    LLMResponse,
    OutputManifest,
    RunManifest,
    SkillContext,
    StageConfig,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_run_manifest(
    run_id: str,
    skill: str,
    outputs: list[OutputManifest],
    depends_on: list[str] | None = None,
) -> RunManifest:
    return RunManifest(
        id=run_id,
        skill=skill,
        version="1.0.0",
        status=RunStatus.COMPLETED,
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
        model="mock-model",
        depends_on=depends_on or [],
        outputs=outputs,
    )


def _write_run_manifest(runs_dir: Path, manifest: RunManifest) -> None:
    run_dir = runs_dir / manifest.id
    run_dir.mkdir(parents=True, exist_ok=True)
    run_yaml = run_dir / "run.yaml"
    run_yaml.write_text(
        yaml.safe_dump(manifest.model_dump(mode="json"), allow_unicode=True),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def upstream_workspace(tmp_path: Path) -> Path:
    """Create a workspace with runs/001-ai-analytics/ artifacts."""
    ws = tmp_path / "project"
    ws.mkdir()

    # Create workspace marker
    (ws / "designos.project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "test-project",
                "created": datetime.now(UTC).isoformat(),
                "owner": "test-user",
            },
            allow_unicode=True,
        )
    )

    runs_dir = ws / "runs"
    runs_dir.mkdir()

    # Create upstream run 001-ai-analytics
    run_001_dir = runs_dir / "001-ai-analytics"
    run_001_dir.mkdir()

    # Write analysis report artifact
    analysis_report = run_001_dir / "analysis_report.md"
    analysis_report.write_text(
        "# AI Analytics 分析报告\n\n## 核心发现\n- 用户需要登录功能\n- 注册流程需优化",
        encoding="utf-8",
    )

    # Write run manifest for 001
    manifest_001 = _make_run_manifest(
        run_id="001-ai-analytics",
        skill="ai-analytics",
        outputs=[
            OutputManifest(
                id="analysis-report-001",
                type=OutputType.ANALYSIS_REPORT,
                path=Path("analysis_report.md"),
                format="markdown",
                summary="AI 分析报告",
            )
        ],
    )
    _write_run_manifest(runs_dir, manifest_001)

    return ws


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestUpstreamInjection:
    """Verify upstream run products are injected into downstream skill context."""

    def test_upstream_run_manifest_readable(self, upstream_workspace: Path) -> None:
        """runs/001-ai-analytics/run.yaml is readable and valid."""
        run_yaml = upstream_workspace / "runs" / "001-ai-analytics" / "run.yaml"
        assert run_yaml.exists()

        raw = yaml.safe_load(run_yaml.read_text(encoding="utf-8"))
        manifest = RunManifest.model_validate(raw)

        assert manifest.id == "001-ai-analytics"
        assert manifest.status == RunStatus.COMPLETED
        assert len(manifest.outputs) == 1
        assert manifest.outputs[0].type == OutputType.ANALYSIS_REPORT

    def test_upstream_artifact_file_exists(self, upstream_workspace: Path) -> None:
        """Artifact file referenced in run manifest physically exists."""
        run_dir = upstream_workspace / "runs" / "001-ai-analytics"
        run_yaml = run_dir / "run.yaml"
        raw = yaml.safe_load(run_yaml.read_text(encoding="utf-8"))
        manifest = RunManifest.model_validate(raw)

        for output in manifest.outputs:
            artifact_path = run_dir / output.path
            assert artifact_path.exists(), f"Artifact {output.path} not found"

    def test_upstream_data_injected_into_skill_context(
        self, upstream_workspace: Path
    ) -> None:
        """upstream_data is populated from 001-ai-analytics artifacts."""
        run_dir = upstream_workspace / "runs" / "001-ai-analytics"
        run_yaml = run_dir / "run.yaml"
        raw = yaml.safe_load(run_yaml.read_text(encoding="utf-8"))
        manifest = RunManifest.model_validate(raw)

        # Simulate upstream injection: read artifact content and inject
        upstream_data: dict[str, Any] = {}
        for output in manifest.outputs:
            artifact_path = run_dir / output.path
            if artifact_path.exists():
                upstream_data[output.id] = artifact_path.read_text(encoding="utf-8")

        # Create downstream context with injected upstream data
        ctx = SkillContext(
            workspace=upstream_workspace,
            skill_name="prd2proto",
            skill_version="1.0.0",
            run_id="002-prd2proto",
            config=DesignOSConfig(
                workspace=upstream_workspace,
                global_config=GlobalConfig(),
            ),
            upstream_data=upstream_data,
        )

        assert "analysis-report-001" in ctx.upstream_data
        assert "核心发现" in ctx.upstream_data["analysis-report-001"]

    @pytest.mark.asyncio
    async def test_pipeline_stage_consumes_upstream_data(
        self, upstream_workspace: Path
    ) -> None:
        """Pipeline stage can read upstream_data via _collect_inputs."""
        from kernel.contracts.interfaces import IPipelineSkill
        from kernel.pipeline.engine import PipelineEngine

        # Load upstream artifact
        run_dir = upstream_workspace / "runs" / "001-ai-analytics"
        analysis_content = (run_dir / "analysis_report.md").read_text(encoding="utf-8")

        # Create prompt file for downstream stage
        prompt_file = upstream_workspace / "prompt.md"
        prompt_file.write_text("基于以下分析：{{upstream_analysis}}\n生成原型方案")

        stages = [
            StageConfig(
                id="proto-gen",
                type=StageType.LLM,
                prompt=prompt_file,
                inputs=["upstream_analysis"],
                outputs=["prototype_spec"],
            )
        ]

        class MockProtoSkill(IPipelineSkill):
            name = "prd2proto"
            version = "1.0.0"
            skill_type = SkillType.PIPELINE

            def get_stages(self) -> list[StageConfig]:
                return stages

            async def run(self, ctx: SkillContext) -> Any:
                pass

        mock_llm = AsyncMock()
        mock_llm.call = AsyncMock(
            return_value=LLMResponse(
                text='{"prototype": "登录页面原型方案"}',
                model="mock-model",
                input_tokens=200,
                output_tokens=80,
            )
        )

        ctx = SkillContext(
            workspace=upstream_workspace,
            skill_name="prd2proto",
            skill_version="1.0.0",
            run_id="002-prd2proto",
            config=DesignOSConfig(
                workspace=upstream_workspace,
                global_config=GlobalConfig(),
            ),
            upstream_data={"upstream_analysis": analysis_content},
        )

        engine = PipelineEngine(llm=mock_llm)

        events = []
        async for event in engine.execute(MockProtoSkill(), ctx):
            events.append(event)

        # Verify stage completed and output was produced
        completed = [e for e in events if e.kind == "stage_completed" and e.stage_id == "proto-gen"]
        assert len(completed) == 1
        assert "prototype_spec" in ctx.state

        # Verify LLM was called with upstream data in prompt
        call_args = mock_llm.call.call_args
        rendered_prompt = call_args[0][0]
        assert "核心发现" in rendered_prompt

    def test_multiple_upstream_runs_injected(self, tmp_path: Path) -> None:
        """Multiple upstream run artifacts can be injected simultaneously."""
        ws = tmp_path / "multi-upstream"
        ws.mkdir()

        runs_dir = ws / "runs"
        runs_dir.mkdir()

        # Create two upstream runs
        for run_id, skill_name, content in [
            ("001-ai-analytics", "ai-analytics", "# 分析报告\n内容A"),
            ("002-uxeval", "uxeval", "# UX 评估\n内容B"),
        ]:
            run_dir = runs_dir / run_id
            run_dir.mkdir()
            artifact = run_dir / "output.md"
            artifact.write_text(content, encoding="utf-8")

        # Simulate injecting both
        upstream_data: dict[str, Any] = {}
        for run_id in ["001-ai-analytics", "002-uxeval"]:
            run_dir = runs_dir / run_id
            artifact = run_dir / "output.md"
            upstream_data[f"{run_id}-output"] = artifact.read_text(encoding="utf-8")

        ctx = SkillContext(
            workspace=ws,
            skill_name="prd2proto",
            skill_version="1.0.0",
            run_id="003-prd2proto",
            config=DesignOSConfig(workspace=ws, global_config=GlobalConfig()),
            upstream_data=upstream_data,
        )

        assert len(ctx.upstream_data) == 2
        assert "内容A" in ctx.upstream_data["001-ai-analytics-output"]
        assert "内容B" in ctx.upstream_data["002-uxeval-output"]
