"""Enumerations for DesignOS kernel contracts.

These enums are the single source of truth for skill types, stage types,
output types, error codes, severity levels, checkpoint actions, run/stage
status, MCP transport modes, and the shared `Mode` literal alias.

All other modules — kernel internals, MCP servers, skills — must import
enums from here, never redefine equivalents.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal


class SkillType(str, Enum):
    """Form factor of a Skill artefact loaded by the kernel."""

    PIPELINE = "pipeline"
    GROUP = "group"


class StageType(str, Enum):
    """Execution shape of a single pipeline stage."""

    LLM = "llm"
    TOOL = "tool"
    COMPOSITE = "composite"


class OutputType(str, Enum):
    """Standard product types skills can declare and consume.

    Skills self-register their `OutputType` in their ``SKILL.md``; the kernel
    uses the type to wire upstream skill products into downstream prompts.
    Adding a new value here requires updating ``docs/schemas/output-types.md``.
    """

    ANALYSIS_REPORT = "analysis_report"
    DESIGN_STRATEGY = "design_strategy"
    COMPARISON_MATRIX = "comparison_matrix"
    USER_PERSONA = "user_persona"
    USER_JOURNEY = "user_journey"
    TASK_CHECKLIST = "task_checklist"
    ISSUE_REPORT = "issue_report"
    HTML_REPORT = "html_report"
    PROTOTYPE_CODE = "prototype_code"
    DESIGN_TOKENS = "design_tokens"
    INFORMATION_ARCHITECTURE = "information_architecture"
    COMPONENT_SPEC = "component_spec"
    STYLE_GUIDE = "style_guide"
    BRAND_BRIEF = "brand_brief"
    BRAND_PERSONA = "brand_persona"
    VISUAL_SPEC = "visual_spec"
    CONTENT_PLAN = "content_plan"
    HEURISTIC_CHECKLIST = "heuristic_checklist"
    EVIDENCE_PACK = "evidence_pack"
    DELIVERY_AUDIT_BUNDLE = "delivery_audit_bundle"
    EVALUATION_SCRIPT = "evaluation_script"
    AUTOMATED_EVAL_TRACE = "automated_eval_trace"
    VISUAL_DIFF_REPORT = "visual_diff_report"
    ACCEPTANCE_REPORT = "acceptance_report"
    PAGE_MAPPING = "page_mapping"
    FRONTEND_CODE = "frontend_code"
    DESIGN_TOKEN_SPEC = "design_token_spec"
    # Creative-generation archetype outputs (I1.1)
    WORLDVIEW = "worldview"
    PERSONA_PROFILE = "persona_profile"
    IMAGE_PROMPT_PACK = "image_prompt_pack"
    BRAND_MATERIAL_SPEC = "brand_material_spec"
    PROFESSIONAL_GAP_REPORT = "professional_gap_report"


class ErrorCode(str, Enum):
    """Canonical DesignOS error codes used by every ``DesignOSError``.

    The leading character group encodes the failure family:
    ``E1xxx`` config / preflight, ``E2xxx`` pipeline, ``E3xxx`` MCP,
    ``E4xxx`` workspace, ``E5xxx`` memory / sanitizer.
    """

    E1001 = "E1001"
    E1002 = "E1002"
    E1003 = "E1003"
    E2001 = "E2001"
    E2002 = "E2002"
    E2003 = "E2003"
    E2004 = "E2004"
    E3001 = "E3001"
    E3002 = "E3002"
    E3003 = "E3003"
    E4001 = "E4001"
    E4002 = "E4002"
    E4003 = "E4003"
    E5001 = "E5001"
    E5002 = "E5002"


class SeverityLevel(str, Enum):
    """Severity of an issue raised by uxeval / design-acceptance."""

    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    SUGGESTION = "suggestion"


class CheckpointAction(str, Enum):
    """User decision recorded at a pipeline checkpoint."""

    CONTINUE = "continue"
    MODIFY = "modify"
    SUPPLEMENT = "supplement"


class RunStatus(str, Enum):
    """Lifecycle state of a single skill run."""

    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class StageStatus(str, Enum):
    """Terminal state of a single pipeline stage."""

    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class MCPTransport(str, Enum):
    """Wire transport used to talk to an MCP server."""

    STDIO = "stdio"
    SSE = "sse"


# Skill mode literal — concrete values are skill-specific (e.g. "web", "client",
# "pm", "designer-spec", "designer-dsl"); we keep it open as a string alias so
# Pydantic can validate without enumerating every skill's modes here.
Mode = Literal[
    "web",
    "client",
    "pm",
    "designer-spec",
    "designer-dsl",
]
"""Canonical skill execution modes.

Skills declare their supported modes via ``SKILL.md``; this alias lists every
value seen across the M1 skill matrix. New modes must be appended here so
``SkillContext.mode`` keeps a precise type.
"""


__all__ = [
    "CheckpointAction",
    "ErrorCode",
    "MCPTransport",
    "Mode",
    "OutputType",
    "RunStatus",
    "SeverityLevel",
    "SkillType",
    "StageStatus",
    "StageType",
]
