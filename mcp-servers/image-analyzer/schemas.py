"""Pydantic models for image-analyzer MCP server."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SourceChannel = Literal["ocr", "filename", "markdown", "metadata", "mixed"]
ConfidenceLevel = Literal["high", "medium", "low"]
PreRunStatus = Literal["ready", "supplement_required", "blocked"]
RequirementLevel = Literal["hard", "recommended"]
StateCategory = Literal["default", "success", "error", "loading", "empty"]


class AnalysisTrace(BaseModel):
    """Traceability metadata attached to every derived analysis result."""

    confidence: ConfidenceLevel = Field(
        default="medium",
        description="Confidence in this specific derived result.",
    )
    source_channel: SourceChannel = Field(
        default="metadata",
        description="Primary source channel used to derive this result.",
    )
    evidence_basis: list[str] = Field(
        default_factory=list,
        description="Concrete evidence snippets supporting the result.",
    )
    unsupported: list[str] = Field(
        default_factory=list,
        description="Capabilities this result cannot currently provide.",
    )
    unknown: list[str] = Field(
        default_factory=list,
        description="Fields that remain unknown after available analysis.",
    )
    verification_gaps: list[str] = Field(
        default_factory=list,
        description="Specific follow-up gaps that require more evidence or review.",
    )


class TextCue(AnalysisTrace):
    """Single text-based cue extracted from OCR, filename or markdown."""

    cue_type: Literal[
        "ocr_text",
        "page_title",
        "button_text",
        "navigation_text",
        "state_text",
        "filename_hint",
        "description_hint",
    ] = Field(description="Normalized cue category for downstream consumption.")
    value: str = Field(description="Extracted text cue value.")


class DescriptionLink(AnalysisTrace):
    """Link between an image and a markdown description file."""

    description_id: str = Field(description="Stable id of the linked markdown description file.")
    description_path: str = Field(description="Relative path of the linked description file.")


class ReadabilityAssessment(AnalysisTrace):
    """How readable or trustworthy a screenshot is for downstream analysis."""

    level: Literal["high", "medium", "low", "unreadable"] = Field(
        description="Overall screenshot readability level.",
    )
    reasons: list[str] = Field(
        default_factory=list,
        description="Concrete reasons behind the readability judgement.",
    )


class EvidenceAssessment(AnalysisTrace):
    """Top-level evidence sufficiency verdict for client-mode screenshot inputs."""

    verdict: Literal["sufficient", "supplement_needed", "blocked"] = Field(
        description="Whether current evidence is sufficient for reliable downstream evaluation.",
    )
    delivery_status: Literal[
        "final_delivery_ready",
        "fallback_safe",
        "supplement_required",
        "blocked",
    ] = Field(
        description="Whether the evidence qualifies for final delivery, limited fallback output, or only supplement/block states.",
    )
    final_delivery_ready: bool = Field(
        default=False,
        description="True only when the current evidence is strong enough for a final issue list and final report.",
    )
    fallback_safe: bool = Field(
        default=False,
        description="True when the current evidence only supports a bounded, clearly limited intermediate result.",
    )
    blocking_reasons: list[str] = Field(
        default_factory=list,
        description="Reasons that block or weaken reliable downstream use.",
    )
    required_actions: list[str] = Field(
        default_factory=list,
        description="Concrete user actions required to unblock or improve evidence quality.",
    )
    missing_coverage: list[str] = Field(
        default_factory=list,
        description="Structured gaps in screenshot, OCR, description, or key-flow coverage that prevent stronger delivery confidence.",
    )
    coverage_summary: dict[str, int | float | bool | str | list[str] | None] = Field(
        default_factory=dict,
        description="Structured coverage and quality metrics used to decide delivery readiness.",
    )
    clarification_items: list["ClarificationItem"] = Field(
        default_factory=list,
        description="Only the ambiguous screenshots that still need minimal confirmation before stronger delivery claims.",
    )
    clarification_package_path: str | None = Field(
        default=None,
        description="Optional path to a generated clarification package for only the ambiguous screenshots.",
    )


class EvidencePageRequirement(AnalysisTrace):
    """Critical page evidence expected before client-mode delivery can be trusted."""

    page_key: str = Field(description="Stable page requirement key.")
    page_name: str = Field(description="Human-readable critical page name.")
    match_tokens: list[str] = Field(
        default_factory=list,
        description="Normalized tokens used for deterministic filename/OCR/markdown matching.",
    )
    task_refs: list[str] = Field(
        default_factory=list,
        description="Task checklist entries that make this page critical.",
    )
    module_refs: list[str] = Field(
        default_factory=list,
        description="Module names that make this page critical.",
    )
    feature_refs: list[str] = Field(
        default_factory=list,
        description="Feature names that make this page critical.",
    )
    journey_stage_refs: list[str] = Field(
        default_factory=list,
        description="Journey stages that make this page critical.",
    )
    required_states: list[StateCategory] = Field(
        default_factory=list,
        description="State categories that should be evidenced for this page.",
    )
    description_required: bool = Field(
        default=False,
        description="Whether markdown description is strongly recommended or required.",
    )
    naming_hint: str = Field(
        description="Optional accelerator-style naming example for this page, not a prerequisite.",
    )
    requirement_level: RequirementLevel = Field(
        default="hard",
        description="Whether this page is a hard or recommended requirement.",
    )
    rationale: str = Field(description="Why this page matters for delivery readiness.")


class CriticalStateRequirement(AnalysisTrace):
    """Critical state evidence expected across one or more pages."""

    state: StateCategory = Field(description="Critical state category.")
    applies_to_pages: list[str] = Field(
        default_factory=list,
        description="Critical page keys this state applies to.",
    )
    requirement_level: RequirementLevel = Field(
        default="hard",
        description="Whether this state is a hard or recommended requirement.",
    )
    rationale: str = Field(description="Why this state matters for delivery readiness.")


class RequiredEvidencePlan(AnalysisTrace):
    """Deterministic client-mode plan for critical evidence inputs."""

    plan_version: str = Field(description="Plan contract version.")
    critical_page_count: int = Field(ge=0, description="Number of critical pages in the plan.")
    critical_state_count: int = Field(ge=0, description="Number of critical states in the plan.")
    critical_pages: list[EvidencePageRequirement] = Field(
        default_factory=list,
        description="Critical page requirements for this run.",
    )
    critical_states: list[CriticalStateRequirement] = Field(
        default_factory=list,
        description="Cross-page critical state requirements for this run.",
    )
    hard_requirements: list[str] = Field(
        default_factory=list,
        description="Non-negotiable inputs required to maximize final-delivery readiness.",
    )
    recommended_descriptions: list[str] = Field(
        default_factory=list,
        description="Pages that should preferably have markdown descriptions.",
    )
    preferred_mapping_files: list[str] = Field(
        default_factory=list,
        description="Low-friction markdown mapping files that can clarify screenshot-to-page/state intent without bulk renaming.",
    )
    naming_convention: str = Field(
        description="Recommended accelerator-style screenshot naming convention, not a prerequisite.",
    )
    quality_targets: dict[str, str] = Field(
        default_factory=dict,
        description="Explicit quality targets for final and fallback delivery modes.",
    )


class EvidenceInputGuidance(AnalysisTrace):
    """Structured one-shot intake guidance before heavy screenshot analysis begins."""

    pre_run_status: PreRunStatus = Field(
        description="Whether the current input bundle is ready, needs supplement, or is blocked before screenshot analysis.",
    )
    current_input_sufficient: bool = Field(
        default=False,
        description="Whether current inputs are strong enough to continue without a pre-run intake pause.",
    )
    status_reason: str = Field(
        default="",
        description="Short product-facing reason for the current pre-run status.",
    )
    required_actions: list[str] = Field(
        default_factory=list,
        description="One-shot structured actions required before or during client-mode evidence execution.",
    )
    optional_suggestions: list[str] = Field(
        default_factory=list,
        description="Nice-to-have accelerators that can improve matching speed but are not a run gate.",
    )
    missing_pages: list[str] = Field(
        default_factory=list,
        description="Critical pages still missing from the current bundle.",
    )
    missing_states: list[str] = Field(
        default_factory=list,
        description="Critical states still likely missing from the current bundle.",
    )
    missing_descriptions: list[str] = Field(
        default_factory=list,
        description="Critical pages that still lack markdown descriptions.",
    )
    naming_issues: list[str] = Field(
        default_factory=list,
        description="Screenshot naming patterns that may slow matching, treated only as a risk/suggestion signal.",
    )
    hard_requirements_missing: list[str] = Field(
        default_factory=list,
        description="Hard requirements that still block high-confidence delivery readiness.",
    )
    clarification_items: list["ClarificationItem"] = Field(
        default_factory=list,
        description="Only the low-confidence screenshot mappings that still need user confirmation.",
    )
    clarification_package_path: str | None = Field(
        default=None,
        description="Optional path to a generated clarification package for only the ambiguous screenshots.",
    )


class PlanRequiredEvidenceResult(BaseModel):
    """Result from ``plan_required_evidence`` tool call."""

    required_evidence_plan: RequiredEvidencePlan = Field(
        description="Deterministic critical evidence plan for this run.",
    )
    critical_page_requirements: list[EvidencePageRequirement] = Field(
        default_factory=list,
        description="Flattened critical page requirements for runtime convenience.",
    )
    critical_state_requirements: list[CriticalStateRequirement] = Field(
        default_factory=list,
        description="Flattened critical state requirements for runtime convenience.",
    )
    evidence_input_guidance: EvidenceInputGuidance = Field(
        description="Structured one-shot intake guidance derived from the plan and current inputs.",
    )


class ScreenshotRef(AnalysisTrace):
    """Reference to a single discovered evidence file."""

    id: str = Field(description="Stable identifier, e.g. 'S-001'")
    path: str = Field(description="Absolute file path")
    relative_path: str = Field(description="Path relative to the scanned root directory")
    kind: Literal["image", "description"] = Field(
        description="Whether the file is a raster image or a markdown description file.",
    )
    format: str = Field(description="Lowercase file format, for example png/jpg/md.")
    file_size_bytes: int = Field(ge=0, description="File size in bytes.")
    width: int | None = Field(default=None, ge=1, description="Pixel width for image files.")
    height: int | None = Field(default=None, ge=1, description="Pixel height for image files.")
    resolution: str | None = Field(
        default=None,
        description="Convenience '<width>x<height>' string for image files.",
    )
    quality_tier: Literal["high", "medium", "low", "not_applicable", "unknown"] = Field(
        description="Resolution-based quality tier for image files.",
    )
    description_preview: str | None = Field(
        default=None,
        description="First 200 characters from a markdown description file.",
    )
    signal_warnings: list[str] = Field(
        default_factory=list,
        description="Filename, markdown or OCR risk hints requiring manual review.",
    )
    readability: ReadabilityAssessment = Field(
        description="Readability assessment for downstream screenshot use.",
    )
    ocr_text_preview: str | None = Field(
        default=None,
        description="Concise OCR text preview when local OCR is available and succeeds.",
    )
    ocr_text_lines: list[TextCue] = Field(
        default_factory=list,
        description="OCR-derived text lines or phrases extracted from the screenshot.",
    )
    page_title_candidates: list[TextCue] = Field(
        default_factory=list,
        description="Best-effort page title candidates with traceability.",
    )
    button_text_candidates: list[TextCue] = Field(
        default_factory=list,
        description="Best-effort button or CTA text candidates with traceability.",
    )
    navigation_text_candidates: list[TextCue] = Field(
        default_factory=list,
        description="Best-effort navigation text candidates with traceability.",
    )
    state_text_candidates: list[TextCue] = Field(
        default_factory=list,
        description="Empty / error / loading / success state text candidates with traceability.",
    )
    description_links: list[DescriptionLink] = Field(
        default_factory=list,
        description="Best-effort links to markdown description files.",
    )
    draft_mapping: "DraftScreenshotMapping | None" = Field(
        default=None,
        description="Best-effort screenshot-to-page/state mapping used to reduce manual screens-map work.",
    )


class DraftScreenshotMapping(AnalysisTrace):
    """Best-effort screenshot mapping to a planned page/state target."""

    page_key: str | None = Field(default=None, description="Matched critical page key when available.")
    page_name: str | None = Field(default=None, description="Matched critical page name when available.")
    matched_states: list[StateCategory] = Field(
        default_factory=list,
        description="State categories inferred for this screenshot.",
    )
    candidate_pages: list[str] = Field(
        default_factory=list,
        description="Top page candidates when the mapping is ambiguous.",
    )
    clarification_needed: bool = Field(
        default=False,
        description="Whether this screenshot still needs a lightweight human confirmation.",
    )
    clarification_reason: str | None = Field(
        default=None,
        description="Short reason why the mapping still needs confirmation.",
    )
    final_delivery_eligible: bool = Field(
        default=False,
        description="Whether this mapping is strong enough to count toward final_delivery_ready coverage.",
    )
    final_delivery_reason: str | None = Field(
        default=None,
        description="Short deterministic reason explaining why this mapping can or cannot count toward final delivery.",
    )


class ClarificationItem(AnalysisTrace):
    """Minimal user-facing clarification request for an ambiguous screenshot."""

    screenshot_id: str = Field(description="Stable screenshot id that needs confirmation.")
    relative_path: str = Field(description="Relative path of the ambiguous screenshot.")
    candidate_pages: list[str] = Field(
        default_factory=list,
        description="Top candidate pages inferred for this screenshot.",
    )
    candidate_states: list[StateCategory] = Field(
        default_factory=list,
        description="State categories already inferred for this screenshot.",
    )
    clarification_reason: str = Field(
        description="Short reason explaining why this screenshot still needs confirmation.",
    )


class ImageAnalysisSummary(AnalysisTrace):
    """Concrete analyzer capabilities and high-level evidence summary."""

    analyzer_kind: Literal["text_evidence_inventory"] = Field(
        default="text_evidence_inventory",
        description="Concrete analyzer mode implemented by this server.",
    )
    capabilities: list[str] = Field(
        default_factory=list,
        description="Concrete capabilities provided by the analyzer.",
    )
    limitations: list[str] = Field(
        default_factory=list,
        description="Known limitations downstream stages must respect.",
    )
    semantic_analysis_available: bool = Field(
        default=False,
        description="Whether this analyzer can do screenshot semantic understanding.",
    )
    ocr_available: bool = Field(
        default=False,
        description="Whether this analyzer can extract text from pixels.",
    )
    ocr_backend: str | None = Field(
        default=None,
        description="Concrete OCR backend name when OCR is available.",
    )
    summary: dict[str, int | bool | str | None | list[str]] = Field(
        default_factory=dict,
        description="Inventory and evidence counts for downstream consumption.",
    )


class LoadAnalyzeResult(BaseModel):
    """Result from ``load_and_analyze`` tool call."""

    screenshots: list[ScreenshotRef] = Field(
        default_factory=list,
        description="Ordered list of recursively discovered screenshot evidence files.",
    )
    image_analysis: ImageAnalysisSummary = Field(
        description="Concrete capabilities and evidence summary for this evidence set.",
    )
    evidence_assessment: EvidenceAssessment = Field(
        description="Input sufficiency verdict and required follow-up actions.",
    )


__all__ = [
    "AnalysisTrace",
    "ClarificationItem",
    "CriticalStateRequirement",
    "DraftScreenshotMapping",
    "DescriptionLink",
    "EvidenceAssessment",
    "EvidenceInputGuidance",
    "EvidencePageRequirement",
    "ImageAnalysisSummary",
    "LoadAnalyzeResult",
    "PlanRequiredEvidenceResult",
    "PreRunStatus",
    "ReadabilityAssessment",
    "RequiredEvidencePlan",
    "ScreenshotRef",
    "StateCategory",
    "TextCue",
]
