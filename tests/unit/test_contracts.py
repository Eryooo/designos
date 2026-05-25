"""Unit tests for ``kernel.contracts`` — schemas, enums, errors, interfaces."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from kernel.contracts import (
    ArtifactRef,
    CheckpointAction,
    CheckpointConfig,
    CheckpointDecision,
    CheckpointEvent,
    CheckpointSnapshot,
    ConfigError,
    DesignOSConfig,
    DesignOSError,
    ErrorCode,
    ErrorInfo,
    Evidence,
    GlobalConfig,
    HeuristicPrinciple,
    ICheckpointManager,
    ILLMClient,
    IMCPClient,
    IMemoryAdapter,
    IOutputRenderer,
    IPipelineEngine,
    IPipelineSkill,
    IPreflightChecker,
    ISkill,
    ISkillGroup,
    ISkillLoader,
    IWorkflowOrchestrator,
    InputUsed,
    Issue,
    JourneyStage,
    LLMResponse,
    MCPError,
    MCPServerConfig,
    MCPTransport,
    Module,
    OrgMemoryError,
    OutputManifest,
    OutputType,
    PipelineError,
    PreflightError,
    ProjectConfig,
    RetryConfig,
    RunManifest,
    RunStatus,
    SanitizerError,
    SeverityLevel,
    SkillConfig,
    SkillContext,
    SkillResult,
    SkillType,
    StageConfig,
    StageEvent,
    StageResult,
    StageStatus,
    StageType,
    Task,
    ToolResult,
    UserRole,
    WorkflowConfig,
    WorkflowEvent,
    WorkflowStep,
    WorkspaceError,
)

NOW = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Enum sanity
# ---------------------------------------------------------------------------


def test_skill_type_values() -> None:
    assert SkillType.PIPELINE.value == "pipeline"
    assert SkillType.GROUP.value == "group"


def test_stage_type_values() -> None:
    assert {s.value for s in StageType} == {"llm", "tool", "composite"}


def test_severity_level_values() -> None:
    assert {s.value for s in SeverityLevel} == {
        "critical",
        "major",
        "minor",
        "suggestion",
    }


def test_run_status_values() -> None:
    assert {s.value for s in RunStatus} == {
        "running",
        "paused",
        "completed",
        "failed",
    }


def test_stage_status_values() -> None:
    assert {s.value for s in StageStatus} == {"completed", "failed", "skipped"}


def test_checkpoint_action_values() -> None:
    assert {a.value for a in CheckpointAction} == {
        "continue",
        "modify",
        "supplement",
    }


def test_mcp_transport_values() -> None:
    assert {t.value for t in MCPTransport} == {"stdio", "sse"}


def test_output_type_includes_adr_additions() -> None:
    expected = {
        "evaluation_script",
        "automated_eval_trace",
        "visual_diff_report",
        "acceptance_report",
        "page_mapping",
        "frontend_code",
        "design_token_spec",
    }
    actual = {o.value for o in OutputType}
    assert expected.issubset(actual)


def test_error_code_families_present() -> None:
    codes = {e.value for e in ErrorCode}
    assert "E1001" in codes
    assert "E2003" in codes
    assert "E3001" in codes
    assert "E4002" in codes
    assert "E5002" in codes


# ---------------------------------------------------------------------------
# Schema instantiation (happy path)
# ---------------------------------------------------------------------------


def test_error_info_frozen_and_serialisable() -> None:
    info = ErrorInfo(code=ErrorCode.E2003, message="schema mismatch")
    assert info.code is ErrorCode.E2003
    with pytest.raises(ValidationError):
        info.code = ErrorCode.E1001  # type: ignore[misc]


def test_artifact_ref_minimal() -> None:
    ref = ArtifactRef(
        id="issue_report",
        output_type=OutputType.ISSUE_REPORT,
        path=Path("outputs/issues.xlsx"),
        format="xlsx",
    )
    assert ref.format == "xlsx"


def test_retry_config_defaults() -> None:
    cfg = RetryConfig()
    assert cfg.max_attempts == 2
    assert cfg.backoff_seconds == pytest.approx(1.0)


def test_stage_config_with_checkpoint() -> None:
    stage = StageConfig(
        id="journey-modeling",
        type=StageType.LLM,
        prompt=Path("prompts/v1.0.0/03-journey-modeling.md"),
        inputs=["modules", "roles"],
        outputs=["journey_map"],
        checkpoint=CheckpointConfig(
            id="C1",
            message="confirm journey",
            allow=[CheckpointAction.CONTINUE, CheckpointAction.MODIFY],
        ),
    )
    assert stage.checkpoint is not None
    assert stage.checkpoint.id == "C1"


def test_workflow_config_minimal() -> None:
    wf = WorkflowConfig(
        name="quick-audit",
        description="T1+T2 quick audit",
        steps=[
            WorkflowStep(
                type="parallel",
                sub_skills=["a", "b"],
                on_failure="continue",
            )
        ],
    )
    assert wf.steps[0].type == "parallel"


def test_designos_config_minimal() -> None:
    cfg = DesignOSConfig(workspace=Path("/tmp/ws"))
    assert isinstance(cfg.global_config, GlobalConfig)
    assert cfg.project_config is None


def test_skill_context_minimal() -> None:
    ctx = SkillContext(
        workspace=Path("/tmp/ws"),
        skill_name="uxeval",
        skill_version="1.0.0",
        run_id="001-uxeval",
        config=DesignOSConfig(workspace=Path("/tmp/ws")),
    )
    assert ctx.mode is None
    assert ctx.upstream_data == {}


def test_stage_result_completed() -> None:
    sr = StageResult(stage_id="prd-understanding", status=StageStatus.COMPLETED)
    assert sr.error is None


def test_skill_result_paused() -> None:
    res = SkillResult(
        skill_name="uxeval",
        skill_version="1.0.0",
        status=RunStatus.PAUSED,
        paused_at_checkpoint="C1",
        pause_kind="checkpoint",
    )
    assert res.paused_at_checkpoint == "C1"
    assert res.pause_kind == "checkpoint"


def test_stage_event() -> None:
    ev = StageEvent(kind="stage_completed", stage_id="s1", timestamp=NOW)
    assert ev.kind == "stage_completed"


def test_workflow_event() -> None:
    ev = WorkflowEvent(kind="step_started", step_index=0, timestamp=NOW)
    assert ev.step_index == 0


def test_checkpoint_event() -> None:
    ev = CheckpointEvent(
        checkpoint_id="C1",
        decision=CheckpointAction.CONTINUE,
        timestamp=NOW,
    )
    assert ev.decision is CheckpointAction.CONTINUE


def test_llm_response_token_counts() -> None:
    resp = LLMResponse(text="hello", model="claude-opus-4-7", input_tokens=10, output_tokens=5)
    assert resp.finish_reason == "stop"


def test_tool_result_ok() -> None:
    tr = ToolResult(server="pdf-parser", tool="parse_pdf", ok=True, data={"sections": []})
    assert tr.ok is True


def test_run_manifest_minimal() -> None:
    rm = RunManifest(
        id="001-uxeval",
        skill="uxeval",
        version="1.0.0",
        status=RunStatus.RUNNING,
        started_at=NOW,
        model="claude-opus-4-7",
    )
    assert rm.outputs == []
    assert rm.required_actions == []


def test_checkpoint_snapshot_round_trip() -> None:
    snap = CheckpointSnapshot(
        run_id="001-uxeval",
        skill="uxeval",
        current_stage_index=2,
        completed_stage_ids=["s1", "s2"],
        pending_stage_ids=["s3"],
        last_updated=NOW,
    )
    again = CheckpointSnapshot.model_validate(snap.model_dump())
    assert again.current_stage_index == 2


def test_mcp_server_config_defaults_stdio() -> None:
    cfg = MCPServerConfig(name="pdf-parser")
    assert cfg.transport is MCPTransport.STDIO
    assert cfg.builtin is True


def test_global_config_defaults() -> None:
    g = GlobalConfig()
    assert g.primary_model == "claude-opus-4-7"
    assert "markdown" in g.default_output_formats


def test_project_config_minimal() -> None:
    pc = ProjectConfig(name="demo", created=NOW, owner="young")
    assert pc.tags == []


def test_skill_config_minimal() -> None:
    sc = SkillConfig(name="uxeval", version="1.0.0", skill_type=SkillType.PIPELINE)
    assert sc.requires_kernel.startswith(">=")


def test_input_used_and_output_manifest() -> None:
    iu = InputUsed(path=Path("inputs/prd.pdf"), type="PRD")
    om = OutputManifest(
        id="issue_report",
        type=OutputType.ISSUE_REPORT,
        path=Path("outputs/issues.xlsx"),
        format="xlsx",
    )
    assert iu.type == "PRD"
    assert om.format == "xlsx"


def test_issue_defaults_include_delivery_metadata() -> None:
    issue = Issue(
        id="I-001",
        title="Sample",
        description="Sample description",
        severity=SeverityLevel.MINOR,
        evidence_refs=["E-001"],
        user_impact="在示例场景下，用户完成操作时遇到示例问题，导致效率下降。",
        suggestion="建议把当前示例元素改为更清晰的反馈样式，并降低理解成本。",
    )
    assert issue.confidence == "medium"
    assert issue.evidence_basis == []
    assert issue.verification_status == "verified"


def test_checkpoint_decision_record() -> None:
    cd = CheckpointDecision(
        checkpoint="C1",
        decision=CheckpointAction.MODIFY,
        timestamp=NOW,
    )
    assert cd.decision is CheckpointAction.MODIFY


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------


def test_evidence_with_bbox() -> None:
    ev = Evidence(id="E-001", kind="screenshot", path=Path("e/1.png"), bbox=(10, 20, 30, 40))
    assert ev.bbox == (10, 20, 30, 40)


def test_heuristic_principle() -> None:
    hp = HeuristicPrinciple(id="H1", name="Visibility", description="...")
    assert hp.id == "H1"


def test_journey_stage() -> None:
    js = JourneyStage(id="J1", name="onboarding", description="first contact")
    assert js.role_ids == []


def test_module() -> None:
    m = Module(id="M1", name="workbench", description="core ops")
    assert m.pages == []


def test_user_role() -> None:
    role = UserRole(id="R1", name="ops", goals=["finish job"])
    assert role.goals == ["finish job"]


def test_task() -> None:
    t = Task(id="T1", title="login", description="...", role="ops")
    assert t.success_criteria == []


def test_issue_requires_evidence_and_user_impact() -> None:
    issue = Issue(
        id="I-001",
        title="login fails silently",
        description="user gets no feedback",
        severity=SeverityLevel.MAJOR,
        evidence_refs=["E-001"],
        user_impact="user cannot proceed",
        suggestion="show inline error",
    )
    assert issue.severity is SeverityLevel.MAJOR


# ---------------------------------------------------------------------------
# Validation failures (missing required fields)
# ---------------------------------------------------------------------------


def test_issue_rejects_empty_evidence_refs() -> None:
    with pytest.raises(ValidationError):
        Issue(
            id="I-001",
            title="t",
            description="d",
            severity=SeverityLevel.MINOR,
            evidence_refs=[],  # constitution rule: must be non-empty
            user_impact="impact",
            suggestion="fix",
        )


def test_run_manifest_requires_started_at() -> None:
    with pytest.raises(ValidationError):
        RunManifest(  # type: ignore[call-arg]
            id="x",
            skill="uxeval",
            version="1.0.0",
            status=RunStatus.RUNNING,
            model="claude-opus-4-7",
        )


def test_workflow_step_requires_sub_skills() -> None:
    with pytest.raises(ValidationError):
        WorkflowStep(type="sequential", sub_skills=[])


def test_skill_context_requires_run_id() -> None:
    with pytest.raises(ValidationError):
        SkillContext(  # type: ignore[call-arg]
            workspace=Path("/tmp/ws"),
            skill_name="uxeval",
            skill_version="1.0.0",
            config=DesignOSConfig(workspace=Path("/tmp/ws")),
        )


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


def test_designos_error_carries_code() -> None:
    err = DesignOSError(ErrorCode.E1001, "missing config", context={"path": "foo"})
    assert err.error_code is ErrorCode.E1001
    assert "[E1001]" in str(err)
    assert err.context == {"path": "foo"}


@pytest.mark.parametrize(
    "exc_cls",
    [
        ConfigError,
        PipelineError,
        MCPError,
        WorkspaceError,
        OrgMemoryError,
        PreflightError,
        SanitizerError,
    ],
)
def test_error_subclasses_inherit_from_designos_error(
    exc_cls: type[DesignOSError],
) -> None:
    err = exc_cls(ErrorCode.E2001, "boom")
    assert isinstance(err, DesignOSError)


def test_org_memory_error_does_not_shadow_builtin() -> None:
    # ensure we did not redefine the builtin MemoryError name in the contracts
    from kernel import contracts as c

    assert not hasattr(c, "MemoryError")
    assert hasattr(c, "OrgMemoryError")


# ---------------------------------------------------------------------------
# Abstract interfaces cannot be instantiated
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "iface",
    [
        ISkill,
        IPipelineSkill,
        ISkillGroup,
        IPipelineEngine,
        IWorkflowOrchestrator,
        ILLMClient,
        IMCPClient,
        IMemoryAdapter,
        IPreflightChecker,
        IOutputRenderer,
        ISkillLoader,
        ICheckpointManager,
    ],
)
def test_abstract_interfaces_are_not_instantiable(iface: type) -> None:
    with pytest.raises(TypeError):
        iface()  # type: ignore[abstract]
