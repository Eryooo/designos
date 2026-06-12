"""Pydantic models for image-analyzer MCP server."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

SourceChannel = Literal["ocr", "filename", "markdown", "metadata", "mixed"]
ConfidenceLevel = Literal["high", "medium", "low"]
FusionVerdict = Literal["trusted", "provisional", "conflicting", "ambiguous"]
PreRunStatus = Literal["ready", "supplement_required", "blocked"]
RequirementLevel = Literal["hard", "recommended"]
StateCategory = Literal["default", "success", "error", "loading", "empty"]
CriticalPathPriority = Literal["P0", "P1", "P2"]
TargetedAcquisitionAction = Literal[
    "must_acquire_now",
    "clarify_existing_evidence",
    "nice_to_have_later",
]
TargetedAcquisitionInputForm = Literal[
    "screenshot",
    "markdown_description",
    "clarification",
]


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
    critical_path_coverage_summary: "CriticalPathCoverageSummary | None" = Field(
        default=None,
        description="Critical-path-first coverage result used to gate final delivery and explain fallback or supplement outcomes.",
    )
    fusion_summary: "EvidenceFusionSummary | None" = Field(
        default=None,
        description="Unified evidence-fusion result used by downstream runtime gating and delivery audit.",
    )
    delivery_readiness_breakdown: dict[str, Any] | None = Field(
        default=None,
        description="Structured final/fallback gate breakdown consumed by downstream delivery audit.",
    )
    first_pass_success_breakdown: dict[str, Any] | None = Field(
        default=None,
        description="Structured upstream breakdown describing first-pass success, remediation uplift, and supplement root causes.",
    )
    targeted_acquisition_plan: "TargetedAcquisitionPlan | None" = Field(
        default=None,
        description="Minimal high-value acquisition plan that prioritizes the next evidence action with the strongest expected lift.",
    )
    client_mode_metrics: "ClientModeMetrics | None" = Field(
        default=None,
        description="Unified machine-readable client-mode runtime metrics derived from real coverage, trust, uplift, and burden signals.",
    )
    benchmark_summary: "BenchmarkSummary | None" = Field(
        default=None,
        description="Run-level benchmark summary that explains whether this run is getting closer to the 90%+ client-mode target or merely blocking unsafe output.",
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


class CapturePassPolicy(BaseModel):
    """Deterministic thresholds behind a capture mission pass line."""

    min_image_count: int = Field(
        ge=0,
        description="Minimum screenshot count expected for this delivery mode.",
    )
    min_readable_ratio: float = Field(
        ge=0.0,
        le=1.0,
        description="Minimum readable screenshot ratio for this delivery mode.",
    )
    min_text_evidence_ratio: float = Field(
        ge=0.0,
        le=1.0,
        description="Minimum OCR/markdown/text-cue coverage ratio for this delivery mode.",
    )
    min_page_coverage_ratio: float = Field(
        ge=0.0,
        le=1.0,
        description="Minimum planned page coverage ratio for this delivery mode.",
    )
    min_state_coverage_ratio: float = Field(
        ge=0.0,
        le=1.0,
        description="Minimum planned state coverage ratio for this delivery mode.",
    )
    min_description_ratio_without_ocr: float = Field(
        ge=0.0,
        le=1.0,
        description="Minimum markdown-description coverage ratio required when OCR is unavailable.",
    )
    require_any_description_without_ocr: bool = Field(
        default=False,
        description="Whether at least one markdown description is required when OCR is unavailable.",
    )
    require_trusted_mapping: bool = Field(
        default=False,
        description="Whether only trusted screenshot mappings may count toward this delivery mode.",
    )


class CaptureMission(AnalysisTrace):
    """User-facing and runtime-consumable client-mode capture mission."""

    mission_version: str = Field(description="Capture mission contract version.")
    critical_flows: list[str] = Field(
        default_factory=list,
        description="Critical user flows that drive the first-pass capture task.",
    )
    must_capture_pages: list[str] = Field(
        default_factory=list,
        description="Pages that materially affect delivery readiness and should be captured first.",
    )
    must_capture_states: list[str] = Field(
        default_factory=list,
        description="Page/state combinations that materially affect delivery readiness.",
    )
    nice_to_have_pages: list[str] = Field(
        default_factory=list,
        description="Useful but non-blocking pages that improve confidence or reduce follow-up work.",
    )
    capture_order: list[str] = Field(
        default_factory=list,
        description="Recommended capture order to maximize first-pass evidence coverage.",
    )
    final_delivery_pass_line: list[str] = Field(
        default_factory=list,
        description="Human-readable pass line for final_delivery_ready.",
    )
    fallback_pass_line: list[str] = Field(
        default_factory=list,
        description="Human-readable pass line for fallback_safe.",
    )
    evidence_rationale: list[str] = Field(
        default_factory=list,
        description="Short reasons explaining why each mission item matters.",
    )
    final_delivery_policy: CapturePassPolicy = Field(
        description="Deterministic thresholds that govern final_delivery_ready.",
    )
    fallback_policy: CapturePassPolicy = Field(
        description="Deterministic thresholds that govern fallback_safe.",
    )
    critical_paths: list["CriticalPathDefinition"] = Field(
        default_factory=list,
        description="Critical business paths that downstream coverage and delivery gates must prioritize over generic average coverage.",
    )
    mission_doc_path: str | None = Field(
        default=None,
        description="Optional path to the generated capture_mission.md artifact.",
    )


class CriticalPathDefinition(AnalysisTrace):
    """Runtime-consumable critical business path definition."""

    path_name: str = Field(description="Human-readable critical path name.")
    business_goal: str = Field(description="Short statement of the business goal this path protects.")
    priority: CriticalPathPriority = Field(
        description="Business criticality tier; P0 and P1 govern final delivery, while P2 is secondary.",
    )
    required_pages: list[str] = Field(
        default_factory=list,
        description="Critical pages that must be covered for this path.",
    )
    required_states: list[str] = Field(
        default_factory=list,
        description="Critical page/state combinations that must be evidenced for this path.",
    )


class CriticalPathCoverageRecord(AnalysisTrace):
    """Coverage result for a single critical business path."""

    path_name: str = Field(description="Critical path name.")
    business_goal: str = Field(description="Business goal protected by this path.")
    priority: CriticalPathPriority = Field(description="Priority tier for this path.")
    required_pages: list[str] = Field(default_factory=list, description="Pages expected for this path.")
    required_states: list[str] = Field(default_factory=list, description="States expected for this path.")
    matched_pages: list[str] = Field(default_factory=list, description="Pages currently covered by provisional-or-better evidence.")
    missing_pages: list[str] = Field(default_factory=list, description="Pages still missing from current path coverage.")
    covered_states: list[str] = Field(default_factory=list, description="Covered page/state pairs for this path.")
    missing_states: list[str] = Field(default_factory=list, description="Missing page/state pairs for this path.")
    page_coverage_ratio: float | None = Field(default=None, description="Current page coverage ratio for this path.")
    state_coverage_ratio: float | None = Field(default=None, description="Current state coverage ratio for this path.")
    final_delivery_matched_pages: list[str] = Field(
        default_factory=list,
        description="Pages covered strongly enough to count toward final delivery for this path.",
    )
    final_delivery_missing_pages: list[str] = Field(
        default_factory=list,
        description="Pages still missing from final-delivery-qualified coverage for this path.",
    )
    final_delivery_covered_states: list[str] = Field(
        default_factory=list,
        description="Page/state pairs covered strongly enough to count toward final delivery for this path.",
    )
    final_delivery_missing_states: list[str] = Field(
        default_factory=list,
        description="Page/state pairs still missing from final-delivery-qualified coverage for this path.",
    )
    final_delivery_page_coverage_ratio: float | None = Field(
        default=None,
        description="Final-delivery-qualified page coverage ratio for this path.",
    )
    final_delivery_state_coverage_ratio: float | None = Field(
        default=None,
        description="Final-delivery-qualified state coverage ratio for this path.",
    )
    gates_final_delivery: bool = Field(
        default=False,
        description="Whether this path directly gates final_delivery_ready.",
    )
    gates_fallback_delivery: bool = Field(
        default=False,
        description="Whether this path directly gates fallback_safe.",
    )
    final_delivery_pass: bool = Field(
        default=False,
        description="Whether this path currently passes the final-delivery threshold.",
    )
    fallback_pass: bool = Field(
        default=False,
        description="Whether this path currently passes the fallback threshold.",
    )


class CriticalPathCoverageSummary(AnalysisTrace):
    """Aggregated critical-path-first coverage output for runtime gating."""

    critical_paths: list[CriticalPathCoverageRecord] = Field(
        default_factory=list,
        description="Coverage details for every critical path in this run.",
    )
    failing_final_paths: list[str] = Field(
        default_factory=list,
        description="Critical path labels that still block final delivery.",
    )
    failing_fallback_paths: list[str] = Field(
        default_factory=list,
        description="Critical path labels that still block even bounded fallback sharing.",
    )


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
    capture_mission: CaptureMission = Field(
        description="Capture mission that downstream runtime stages must consume consistently.",
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

    capture_mission: CaptureMission = Field(
        description="User-facing and runtime-consumable capture mission for this run.",
    )
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
    mapping_verdict: FusionVerdict = Field(
        default="ambiguous",
        description="Whether this mapping is trusted, provisional, conflicting, or still ambiguous.",
    )
    fusion_score: int = Field(
        default=0,
        ge=0,
        description="Deterministic fusion score after combining OCR, markdown, metadata, and filename signals.",
    )
    supporting_channels: list[SourceChannel] = Field(
        default_factory=list,
        description="Evidence channels that materially support this mapping.",
    )
    conflicting_candidates: list[str] = Field(
        default_factory=list,
        description="Candidate pages that still conflict with the best mapping hypothesis.",
    )


class ClarificationItem(AnalysisTrace):
    """Minimal user-facing clarification request for an ambiguous screenshot."""

    screenshot_id: str = Field(description="Stable screenshot id that needs confirmation.")
    screenshot_ref: str = Field(
        description="User-facing screenshot reference, usually the relative path that should be confirmed.",
    )
    relative_path: str = Field(description="Relative path of the ambiguous screenshot.")
    candidate_pages: list[str] = Field(
        default_factory=list,
        description="Top candidate pages inferred for this screenshot.",
    )
    candidate_states: list[StateCategory] = Field(
        default_factory=list,
        description="State categories already inferred for this screenshot.",
    )
    ambiguity_reason: str = Field(
        description="Short deterministic reason explaining why this screenshot is still ambiguous.",
    )
    affected_critical_paths: list[str] = Field(
        default_factory=list,
        description="Critical paths whose coverage or final gate would be affected by this clarification.",
    )
    unlocks_final_delivery: bool = Field(
        default=False,
        description="Whether confirming this screenshot can directly help the run move closer to final_delivery_ready.",
    )
    confirmation_prompt: str = Field(
        default="",
        description="Short, concrete confirmation prompt shown to the user.",
    )


class TargetedMetricLift(AnalysisTrace):
    """Expected lift on a concrete runtime metric after one acquisition action."""

    metric: Literal[
        "critical_path_page_hit_rate",
        "critical_path_state_hit_rate",
        "trusted_mapping_rate",
        "clarification_burden",
        "expected_final_unlock_rate",
    ] = Field(description="Runtime metric expected to move after the suggested action.")
    current_value: float = Field(
        default=0.0,
        description="Current metric value before the targeted action.",
    )
    expected_value: float = Field(
        default=0.0,
        description="Estimated metric value after the targeted action succeeds.",
    )
    delta: float = Field(
        default=0.0,
        description="Expected delta from current_value to expected_value.",
    )


class TargetedAcquisitionItem(AnalysisTrace):
    """Single high-value acquisition action that should be taken before generic supplement work."""

    action_class: TargetedAcquisitionAction = Field(
        description="Whether the next best action is to acquire new evidence, clarify existing evidence, or defer as nice-to-have.",
    )
    target_page: str = Field(description="Page that should be captured or clarified first.")
    target_state: str | None = Field(
        default=None,
        description="Specific state that most directly improves coverage when applicable.",
    )
    priority: int = Field(
        ge=0,
        description="Deterministic priority score; higher means higher expected delivery lift.",
    )
    affected_critical_paths: list[str] = Field(
        default_factory=list,
        description="Critical paths that will move if this action succeeds.",
    )
    expected_unlocks_final_delivery: bool = Field(
        default=False,
        description="Whether this single action is expected to unlock or nearly unlock final delivery.",
    )
    expected_metric_lift: list[TargetedMetricLift] = Field(
        default_factory=list,
        description="Metrics most likely to improve if this action succeeds.",
    )
    why_this_first: str = Field(
        default="",
        description="Short product-facing explanation for why this action outranks other supplement work.",
    )
    suggested_input_form: TargetedAcquisitionInputForm = Field(
        description="Lowest-friction input form that can unlock this lift.",
    )
    screenshot_ref: str | None = Field(
        default=None,
        description="Existing screenshot that should be clarified or replaced when relevant.",
    )
    candidate_pages: list[str] = Field(
        default_factory=list,
        description="Candidate pages retained when this action is driven by ambiguity rather than missing evidence.",
    )
    candidate_states: list[StateCategory] = Field(
        default_factory=list,
        description="Candidate states retained when this action is driven by ambiguity rather than missing evidence.",
    )


class TargetedAcquisitionPlan(AnalysisTrace):
    """Minimal high-value acquisition plan for client-mode supplement work."""

    contract_version: str = Field(description="Targeted acquisition contract version.")
    delivery_status: Literal[
        "final_delivery_ready",
        "fallback_safe",
        "supplement_required",
        "blocked",
    ] = Field(
        description="Delivery status that this plan is trying to improve from or maintain.",
    )
    first_pass_final: bool = Field(
        default=False,
        description="Whether the run already achieved final delivery without needing targeted follow-up.",
    )
    supplement_cause_classification: list[str] = Field(
        default_factory=list,
        description="Root-cause classes that explain why targeted acquisition is still needed.",
    )
    must_acquire_now: list[TargetedAcquisitionItem] = Field(
        default_factory=list,
        description="Minimal high-value acquisition set that should be completed first.",
    )
    clarify_existing_evidence: list[TargetedAcquisitionItem] = Field(
        default_factory=list,
        description="Existing screenshots that should be clarified or strengthened before asking for more capture.",
    )
    nice_to_have_later: list[TargetedAcquisitionItem] = Field(
        default_factory=list,
        description="Non-blocking follow-up actions that can wait until the critical gaps are closed.",
    )
    highest_value_next_captures: list[TargetedAcquisitionItem] = Field(
        default_factory=list,
        description="Top next actions across all classes, sorted by expected delivery lift.",
    )
    expected_metric_lift: list[TargetedMetricLift] = Field(
        default_factory=list,
        description="Aggregated metric lift expected from the minimal high-value action set.",
    )
    plan_doc_path: str | None = Field(
        default=None,
        description="Optional path to a generated targeted_acquisition_plan.md artifact.",
    )


class CoverageMetrics(BaseModel):
    """Coverage-side client-mode metrics derived from critical-path runtime truth."""

    critical_path_page_hit_rate: float = Field(default=0.0)
    critical_path_state_hit_rate: float = Field(default=0.0)
    p0_page_coverage: float = Field(default=0.0)
    p0_state_coverage: float = Field(default=0.0)
    p1_page_coverage: float = Field(default=0.0)
    p1_state_coverage: float = Field(default=0.0)


class TrustMetrics(BaseModel):
    """Evidence-trust metrics derived from fusion and downstream qualification state."""

    trusted_mapping_rate: float = Field(default=0.0)
    provisional_mapping_rate: float = Field(default=0.0)
    conflicting_mapping_rate: float = Field(default=0.0)
    unverified_leakage_rate: float = Field(default=0.0)


class SuccessThroughputMetrics(BaseModel):
    """Outcome and uplift metrics that distinguish success from strict blocking."""

    final_delivery_ready_rate: float = Field(default=0.0)
    fallback_safe_rate: float = Field(default=0.0)
    supplement_required_rate: float = Field(default=0.0)
    blocked_rate: float = Field(default=0.0)
    first_pass_final_rate: float = Field(default=0.0)
    auto_remediation_lift: float = Field(default=0.0)
    salvageable_input_rate: float = Field(default=0.0)


class HumanBurdenMetrics(BaseModel):
    """Signals for how much low-value user work still leaks through the runtime."""

    clarification_item_count: int = Field(default=0, ge=0)
    supplement_request_precision: float = Field(default=0.0)
    low_value_work_return_rate: float = Field(default=0.0)


class ClientModeMetrics(AnalysisTrace):
    """Unified machine-readable client-mode metrics contract."""

    contract_version: str = Field(description="Metrics contract version.")
    run_mode: Literal["client"] = Field(
        default="client",
        description="Runtime mode covered by this metrics snapshot.",
    )
    input_quality_class: str = Field(
        default="unknown",
        description="High-level quality class used to compare runs and diagnose the dominant gap type.",
    )
    delivery_status: Literal[
        "final_delivery_ready",
        "fallback_safe",
        "supplement_required",
        "blocked",
    ] = Field(
        description="Current runtime delivery status associated with this metrics snapshot.",
    )
    coverage_metrics: CoverageMetrics = Field(
        description="Critical-path-first coverage metrics.",
    )
    trust_metrics: TrustMetrics = Field(
        description="Fusion and issue-trust metrics.",
    )
    success_metrics: SuccessThroughputMetrics = Field(
        description="Delivery outcome and uplift metrics.",
    )
    human_burden_metrics: HumanBurdenMetrics = Field(
        description="Human-intervention and low-value-work metrics.",
    )
    metric_notes: dict[str, str] = Field(
        default_factory=dict,
        description="Short notes for metrics whose ownership or interpretation depends on downstream stages.",
    )


class BenchmarkSummary(AnalysisTrace):
    """Human- and machine-readable benchmark summary for one client-mode run."""

    contract_version: str = Field(description="Benchmark summary contract version.")
    run_mode: Literal["client"] = Field(
        default="client",
        description="Runtime mode covered by this benchmark summary.",
    )
    input_quality_class: str = Field(
        default="unknown",
        description="High-level quality class for downstream comparison across benchmark runs.",
    )
    delivery_status: Literal[
        "final_delivery_ready",
        "fallback_safe",
        "supplement_required",
        "blocked",
    ] = Field(
        description="Current delivery status summarized by this benchmark artifact.",
    )
    metrics: ClientModeMetrics = Field(
        description="Machine-readable metrics snapshot for this run.",
    )
    met_metrics: list[str] = Field(
        default_factory=list,
        description="Metrics or gates already meeting their intended threshold or contract.",
    )
    unmet_metrics: list[str] = Field(
        default_factory=list,
        description="Metrics or gates still below threshold.",
    )
    distance_to_90_plus: list[str] = Field(
        default_factory=list,
        description="Short statements describing what still blocks the 90%+ target.",
    )
    root_cause: str = Field(
        default="unknown",
        description="Whether the main gap is true missing input, weak readability, unresolved fusion, or system ingestion limits.",
    )
    next_best_action: str = Field(
        default="",
        description="Single highest-value next action derived from runtime evidence.",
    )
    summary_headline: str = Field(
        default="",
        description="Short human-readable summary headline for this run.",
    )
    artifact_paths: dict[str, str] = Field(
        default_factory=dict,
        description="Paths to benchmark-related artifacts and upstream packages used in this summary.",
    )


class PageFusionRecord(AnalysisTrace):
    """Per-screenshot fusion result for page/state mapping."""

    screenshot_id: str = Field(description="Stable screenshot id.")
    relative_path: str = Field(description="Relative path of the screenshot.")
    page_key: str | None = Field(default=None, description="Matched critical page key when available.")
    page_name: str | None = Field(default=None, description="Matched critical page name when available.")
    matched_states: list[StateCategory] = Field(
        default_factory=list,
        description="State categories inferred for this screenshot.",
    )
    mapping_verdict: FusionVerdict = Field(
        description="Whether this fused mapping is trusted, provisional, conflicting, or ambiguous.",
    )
    fusion_score: int = Field(
        ge=0,
        description="Deterministic fusion score for this screenshot mapping.",
    )
    supporting_channels: list[SourceChannel] = Field(
        default_factory=list,
        description="Evidence channels that materially support this mapping.",
    )
    candidate_pages: list[str] = Field(
        default_factory=list,
        description="Candidate pages retained after fusion scoring.",
    )
    final_delivery_eligible: bool = Field(
        default=False,
        description="Whether this mapping may count toward final_delivery_ready.",
    )


class StateFusionRecord(AnalysisTrace):
    """Trusted state evidence derived from a fused screenshot mapping."""

    screenshot_id: str = Field(description="Stable screenshot id.")
    relative_path: str = Field(description="Relative path of the screenshot.")
    page_key: str | None = Field(default=None, description="Matched critical page key when available.")
    page_name: str | None = Field(default=None, description="Matched critical page name when available.")
    state: StateCategory = Field(description="Trusted state category evidenced by this screenshot.")
    mapping_verdict: FusionVerdict = Field(
        description="Fusion verdict inherited from the parent page mapping.",
    )


class ConflictingEvidenceGroup(AnalysisTrace):
    """Explicit multi-source conflicts that must not be counted as trusted evidence."""

    screenshot_id: str = Field(description="Stable screenshot id.")
    relative_path: str = Field(description="Relative path of the screenshot.")
    candidate_pages: list[str] = Field(
        default_factory=list,
        description="Pages that remain in conflict after evidence fusion.",
    )
    conflict_reason: str = Field(
        description="Short deterministic reason why the evidence still conflicts.",
    )
    dominant_channels: list[SourceChannel] = Field(
        default_factory=list,
        description="Channels carrying the strongest but conflicting signals.",
    )


class EvidenceFusionSummary(AnalysisTrace):
    """Unified fusion result across OCR, markdown, metadata, filename, and draft mapping."""

    trusted_page_mappings: list[PageFusionRecord] = Field(
        default_factory=list,
        description="Mappings strong enough to count toward final_delivery_ready coverage.",
    )
    trusted_state_mappings: list[StateFusionRecord] = Field(
        default_factory=list,
        description="Trusted page/state coverage extracted from trusted page mappings.",
    )
    provisional_mappings: list[PageFusionRecord] = Field(
        default_factory=list,
        description="Mappings useful for fallback/remediation but not final delivery.",
    )
    conflicting_evidence_groups: list[ConflictingEvidenceGroup] = Field(
        default_factory=list,
        description="Explicit multi-source conflicts that still require review or clarification.",
    )
    unresolved_ambiguities: list[ClarificationItem] = Field(
        default_factory=list,
        description="Only the screenshots that still need minimal confirmation.",
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
    summary: dict[str, int | float | bool | str | None | list[str]] = Field(
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
    "BenchmarkSummary",
    "CaptureMission",
    "CapturePassPolicy",
    "ClientModeMetrics",
    "ClarificationItem",
    "ConflictingEvidenceGroup",
    "CoverageMetrics",
    "CriticalPathCoverageRecord",
    "CriticalPathCoverageSummary",
    "CriticalPathDefinition",
    "CriticalPathPriority",
    "CriticalStateRequirement",
    "DraftScreenshotMapping",
    "DescriptionLink",
    "EvidenceAssessment",
    "EvidenceFusionSummary",
    "EvidenceInputGuidance",
    "EvidencePageRequirement",
    "FusionVerdict",
    "ImageAnalysisSummary",
    "LoadAnalyzeResult",
    "PageFusionRecord",
    "PlanRequiredEvidenceResult",
    "PreRunStatus",
    "ReadabilityAssessment",
    "RequiredEvidencePlan",
    "ScreenshotRef",
    "SuccessThroughputMetrics",
    "StateFusionRecord",
    "StateCategory",
    "TextCue",
    "TrustMetrics",
    "HumanBurdenMetrics",
]
