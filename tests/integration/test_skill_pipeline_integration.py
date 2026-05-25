"""Integration tests: Skill + Pipeline + Checkpoint flow.

Tests that a Pipeline Skill can be executed end-to-end with mock LLM/MCP,
verifying stage output propagation and checkpoint pause/resume.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest
import yaml

from kernel.contracts.enums import StageStatus, StageType
from kernel.contracts.schemas import (
    CheckpointConfig,
    LLMResponse,
    SkillContext,
    StageConfig,
    StageEvent,
    ToolResult,
)
from kernel.pipeline.engine import PipelineEngine
from kernel.checkpoint.manager import CheckpointManager


@pytest.fixture
def mock_llm_client() -> AsyncMock:
    """Mock ILLMClient that returns canned responses."""
    client = AsyncMock()
    client.call = AsyncMock(
        return_value=LLMResponse(
            text='{"analysis": "用户需要登录和注册功能"}',
            model="mock-model",
            input_tokens=100,
            output_tokens=50,
        )
    )
    return client


@pytest.fixture
def mock_mcp_client() -> AsyncMock:
    """Mock IMCPClient that returns canned tool results."""
    client = AsyncMock()
    client.call_tool = AsyncMock(
        return_value=ToolResult(
            server="mock-server",
            tool="mock-tool",
            ok=True,
            data={"sections": ["需求背景", "功能描述"]},
        )
    )
    return client


@pytest.fixture
def pipeline_yaml_fixture(tmp_path: Path) -> Path:
    """Create a fixture pipeline.yaml with 3 stages."""
    pipeline_config = {
        "stages": [
            {
                "id": "stage-1-llm",
                "type": "llm",
                "prompt": str(tmp_path / "prompt1.md"),
                "inputs": ["prd_text"],
                "outputs": ["analysis"],
            },
            {
                "id": "stage-2-tool",
                "type": "tool",
                "mcp_server": "pdf-parser",
                "mcp_tool": "parse_pdf",
                "inputs": ["prd_path"],
                "outputs": ["sections"],
            },
            {
                "id": "stage-3-composite",
                "type": "composite",
                "inputs": ["analysis", "sections"],
                "outputs": ["final_report"],
                "checkpoint": {
                    "id": "C1",
                    "message": "请确认分析结果",
                    "allow": ["continue"],
                },
            },
        ]
    }

    yaml_path = tmp_path / "pipeline.yaml"
    yaml_path.write_text(yaml.safe_dump(pipeline_config, allow_unicode=True))

    # Create mock prompt file
    (tmp_path / "prompt1.md").write_text("分析以下 PRD：{{prd_text}}")

    return yaml_path


@pytest.mark.integration
class TestSkillPipelineIntegration:
    """Test Pipeline Skill execution with mock dependencies."""

    def test_pipeline_yaml_loads_correctly(self, pipeline_yaml_fixture: Path) -> None:
        """Pipeline YAML can be parsed into StageConfig list."""
        content = yaml.safe_load(pipeline_yaml_fixture.read_text())
        stages = [StageConfig.model_validate(s) for s in content["stages"]]

        assert len(stages) == 3
        assert stages[0].type is StageType.LLM
        assert stages[1].type is StageType.TOOL
        assert stages[2].type is StageType.COMPOSITE
        assert stages[2].checkpoint is not None
        assert stages[2].checkpoint.id == "C1"

    @pytest.mark.asyncio
    async def test_pipeline_engine_executes_stages_sequentially(
        self,
        pipeline_yaml_fixture: Path,
        mock_llm_client: AsyncMock,
        mock_mcp_client: AsyncMock,
        tmp_path: Path,
    ) -> None:
        """PipelineEngine executes stages in order and propagates outputs."""
        from kernel.contracts.interfaces import IPipelineSkill
        from kernel.contracts.enums import SkillType
        from kernel.contracts.schemas import DesignOSConfig, GlobalConfig

        # Load stages from fixture
        content = yaml.safe_load(pipeline_yaml_fixture.read_text())
        stages = [StageConfig.model_validate(s) for s in content["stages"]]

        # Create a mock Pipeline Skill
        class MockPipelineSkill(IPipelineSkill):
            name = "test-skill"
            version = "1.0.0"
            skill_type = SkillType.PIPELINE

            def get_stages(self) -> list[StageConfig]:
                return stages

            async def run(self, ctx: SkillContext) -> Any:
                pass

        skill = MockPipelineSkill()

        # Create context
        ctx = SkillContext(
            workspace=tmp_path,
            skill_name="test-skill",
            skill_version="1.0.0",
            run_id="001-test",
            config=DesignOSConfig(
                workspace=tmp_path,
                global_config=GlobalConfig(),
            ),
            state={
                "prd_text": "# PRD\n## 功能\n- 登录\n- 注册",
                "prd_path": str(tmp_path / "prd.pdf"),
            },
        )

        # Create engine with mocks
        engine = PipelineEngine(llm=mock_llm_client, mcp=mock_mcp_client)

        # Execute and collect events
        events: list[StageEvent] = []
        async for event in engine.execute(skill, ctx):
            events.append(event)

        # Verify events
        assert len(events) >= 3
        assert events[0].kind == "stage_started"
        assert events[0].stage_id == "stage-1-llm"

        # Verify LLM stage completed
        llm_completed = [e for e in events if e.stage_id == "stage-1-llm" and e.kind == "stage_completed"]
        assert len(llm_completed) == 1

        # Verify tool stage completed
        tool_completed = [e for e in events if e.stage_id == "stage-2-tool" and e.kind == "stage_completed"]
        assert len(tool_completed) == 1

        # Verify checkpoint event
        checkpoint_events = [e for e in events if e.kind == "checkpoint"]
        assert len(checkpoint_events) == 1
        assert checkpoint_events[0].payload["checkpoint_id"] == "C1"

        # Verify state propagation
        assert "analysis" in ctx.state
        assert "sections" in ctx.state

    @pytest.mark.asyncio
    async def test_checkpoint_pause_and_resume(
        self,
        pipeline_yaml_fixture: Path,
        mock_llm_client: AsyncMock,
        mock_mcp_client: AsyncMock,
        tmp_path: Path,
    ) -> None:
        """Pipeline pauses at checkpoint and can resume from snapshot."""
        from kernel.contracts.interfaces import IPipelineSkill
        from kernel.contracts.enums import SkillType
        from kernel.contracts.schemas import DesignOSConfig, GlobalConfig

        # Load stages
        content = yaml.safe_load(pipeline_yaml_fixture.read_text())
        stages = [StageConfig.model_validate(s) for s in content["stages"]]

        class MockPipelineSkill(IPipelineSkill):
            name = "test-skill"
            version = "1.0.0"
            skill_type = SkillType.PIPELINE

            def get_stages(self) -> list[StageConfig]:
                return stages

            async def run(self, ctx: SkillContext) -> Any:
                pass

        skill = MockPipelineSkill()

        # Create workspace with checkpoint manager
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        checkpoint_manager = CheckpointManager(workspace)

        ctx = SkillContext(
            workspace=workspace,
            skill_name="test-skill",
            skill_version="1.0.0",
            run_id="002-checkpoint-test",
            config=DesignOSConfig(
                workspace=workspace,
                global_config=GlobalConfig(),
            ),
            state={
                "prd_text": "# PRD\n## 功能\n- 登录",
                "prd_path": str(tmp_path / "prd.pdf"),
            },
        )

        # First run: execute until checkpoint
        engine = PipelineEngine(
            llm=mock_llm_client,
            mcp=mock_mcp_client,
            checkpoint_manager=checkpoint_manager,
        )

        events: list[StageEvent] = []
        async for event in engine.execute(skill, ctx):
            events.append(event)

        # Verify checkpoint was saved
        checkpoint_events = [e for e in events if e.kind == "checkpoint"]
        assert len(checkpoint_events) == 1

        snapshot = checkpoint_manager.load("002-checkpoint-test")
        assert snapshot is not None
        assert snapshot.current_stage_index == 3
        assert len(snapshot.completed_stage_ids) == 3
        assert "analysis" in snapshot.state_snapshot

        # Second run: resume from checkpoint
        ctx2 = SkillContext(
            workspace=workspace,
            skill_name="test-skill",
            skill_version="1.0.0",
            run_id="002-checkpoint-test",
            config=DesignOSConfig(
                workspace=workspace,
                global_config=GlobalConfig(),
            ),
            state={},
        )

        engine2 = PipelineEngine(
            llm=mock_llm_client,
            mcp=mock_mcp_client,
            checkpoint_manager=checkpoint_manager,
        )

        resume_events: list[StageEvent] = []
        async for event in engine2.execute(skill, ctx2):
            resume_events.append(event)

        # Verify no stages were re-executed (resume starts from index 3, which is past all stages)
        assert len(resume_events) == 0

        # Verify state was restored
        assert "analysis" in ctx2.state

    @pytest.mark.asyncio
    async def test_stage_output_propagation(
        self,
        mock_llm_client: AsyncMock,
        tmp_path: Path,
    ) -> None:
        """Stage outputs are correctly propagated to subsequent stages."""
        from kernel.contracts.interfaces import IPipelineSkill
        from kernel.contracts.enums import SkillType
        from kernel.contracts.schemas import DesignOSConfig, GlobalConfig

        stages = [
            StageConfig(
                id="s1",
                type=StageType.LLM,
                prompt=tmp_path / "p1.md",
                inputs=["input1"],
                outputs=["output1"],
            ),
            StageConfig(
                id="s2",
                type=StageType.COMPOSITE,
                inputs=["output1"],
                outputs=["final"],
            ),
        ]

        (tmp_path / "p1.md").write_text("Process: {{input1}}")

        class MockSkill(IPipelineSkill):
            name = "test"
            version = "1.0.0"
            skill_type = SkillType.PIPELINE

            def get_stages(self) -> list[StageConfig]:
                return stages

            async def run(self, ctx: SkillContext) -> Any:
                pass

        ctx = SkillContext(
            workspace=tmp_path,
            skill_name="test",
            skill_version="1.0.0",
            run_id="003-propagation",
            config=DesignOSConfig(workspace=tmp_path, global_config=GlobalConfig()),
            state={"input1": "test data"},
        )

        engine = PipelineEngine(llm=mock_llm_client)

        events: list[StageEvent] = []
        async for event in engine.execute(MockSkill(), ctx):
            events.append(event)

        # Verify output1 was produced by s1 and consumed by s2
        assert "output1" in ctx.state
        assert ctx.state["output1"] == '{"analysis": "用户需要登录和注册功能"}'

        # Verify final output
        assert "final" in ctx.state
