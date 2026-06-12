"""Reverse-extract an :class:`ArchetypeSpec` from an existing skill directory.

Given a skill directory (containing ``SKILL.md`` + ``pipeline.yaml``), this
tool produces an archetype yaml describing the canonical pipeline shape that
that skill embodies. Per CONTRACT §7, every archetype dimension is recovered:

1. frontmatter requirements
2. required + optional outputs
3. stage slots (canonical pipeline topology)
4. checkpoint slots (human pause points)
5. gate slots (runtime quality gates)
6. mode semantics
7. evidence contract
8. delivery contract
9. directory layout

The extraction is heuristic by nature; fields the tool had to guess are
flagged on stderr with ``[warn]`` prefixes and an actionable hint.

CLI
---
Run as a module from the factory root::

    python3 -m tools.extract <skill_dir> [--archetype evaluation] [--output path.yaml]

Stdout receives YAML when ``--output`` is omitted.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal, cast

import yaml

# Absolute import: callers add `.factory/` to sys.path so the bridge sits
# at the top level. Mirrors how archetype_schema.py imports the bridge.
from _kernel_bridge import OutputType, StageType, parse_frontmatter
from archetypes.archetype_schema import (
    ArchetypeSpec,
    CheckpointSlot,
    DeliveryContract,
    DirectoryRequirement,
    EvidenceContract,
    FrontmatterRequirement,
    GateSlot,
    ModeSemantics,
    OutputRequirement,
    StageSlot,
)

ArchetypeName = Literal["evaluation", "generation", "analysis"]

# ---------------------------------------------------------------------------
# Heuristic mappings
# ---------------------------------------------------------------------------

# Map evaluation-pipeline stage IDs to the canonical archetype slot IDs.
# Order matters: the first matching keyword wins. Slot IDs match
# archetypes/evaluation.yaml so extracted spec round-trips cleanly.
#
# Keywords are checked as substrings of the stage id (lower-cased). Rules are
# kept *specific* so non-canonical stages (e.g. uxeval's
# ``prd-screenshot-conflict``, ``task-script-generation``) cleanly fall
# through with a warning instead of being mis-bucketed.
_EVALUATION_STAGE_RULES: list[tuple[tuple[str, ...], str]] = [
    (("prd-understanding", "prd_understanding", "understanding"), "understanding"),
    (("principle-mapping", "principle_mapping"), "principle_mapping"),
    (("journey-modeling", "journey_modeling", "modeling"), "modeling"),
    (("task-generation", "task_generation"), "task_generation"),
    (("evidence-planning", "evidence_planning", "plan_required_evidence"), "evidence_planning"),
    (
        (
            "screenshot-loading",
            "screenshot_loading",
            "web-automation",
            "web_automation",
            "evidence-collection",
            "evidence_collection",
        ),
        "evidence_collection",
    ),
    (("issue-attribution", "issue_attribution", "attribution"), "issue_attribution"),
    (("delivery-audit", "delivery_audit"), "delivery_audit"),
    (("report-generation", "report_generation"), "report_generation"),
]

# Map generation-pipeline stage IDs to canonical slot IDs (best-effort).
_GENERATION_STAGE_RULES: list[tuple[tuple[str, ...], str]] = [
    (("prd-understanding", "prd_understanding", "understanding"), "understanding"),
    (("information-architecture", "information_architecture", "ia-planning", "ia_planning"), "ia_planning"),
    (("design-tokens", "design_tokens", "tokens"), "tokens"),
    (("component-planning", "component_planning"), "component_planning"),
    (("code-generation", "code_generation", "prototype", "frontend"), "code_generation"),
    (("self-review", "self_review", "review"), "self_review"),
]

# Map analysis-pipeline stage IDs to canonical slot IDs (best-effort).
_ANALYSIS_STAGE_RULES: list[tuple[tuple[str, ...], str]] = [
    (("scope", "scoping", "framing"), "scoping"),
    (("data-collection", "data_collection", "collect"), "data_collection"),
    (("comparison", "compare", "matrix"), "comparison"),
    (("synthesis", "synthesi", "insight"), "synthesis"),
    (("report-generation", "report_generation", "report"), "report"),
]

_ARCHETYPE_RULES: dict[ArchetypeName, list[tuple[tuple[str, ...], str]]] = {
    "evaluation": _EVALUATION_STAGE_RULES,
    "generation": _GENERATION_STAGE_RULES,
    "analysis": _ANALYSIS_STAGE_RULES,
}

# Output-type signatures used to guess archetype when --archetype is omitted.
_EVALUATION_SIGNAL_OUTPUTS: set[str] = {
    OutputType.ISSUE_REPORT.value,
    OutputType.HTML_REPORT.value,
    OutputType.EVIDENCE_PACK.value,
    OutputType.DELIVERY_AUDIT_BUNDLE.value,
    OutputType.ACCEPTANCE_REPORT.value,
}
_GENERATION_SIGNAL_OUTPUTS: set[str] = {
    OutputType.PROTOTYPE_CODE.value,
    OutputType.FRONTEND_CODE.value,
    OutputType.COMPONENT_SPEC.value,
    OutputType.DESIGN_TOKENS.value,
    OutputType.DESIGN_TOKEN_SPEC.value,
}
_ANALYSIS_SIGNAL_OUTPUTS: set[str] = {
    OutputType.ANALYSIS_REPORT.value,
    OutputType.COMPARISON_MATRIX.value,
    OutputType.DESIGN_STRATEGY.value,
    OutputType.USER_PERSONA.value,
}

# OutputTypes considered "core" for the evaluation archetype. Matches the
# hand-written evaluation.yaml so the round-trip test stays >= 90% consistent.
_EVALUATION_REQUIRED_OUTPUTS: set[str] = {
    OutputType.ISSUE_REPORT.value,
    OutputType.HTML_REPORT.value,
    OutputType.EVIDENCE_PACK.value,
    OutputType.DELIVERY_AUDIT_BUNDLE.value,
}

_DEFAULT_FRONTMATTER_KEYS: list[str] = [
    "name",
    "version",
    "type",
    "description",
    "requires",
    "outputs",
]

# Common subdirectories every archetype is expected to ship. We only declare
# them in the extracted spec when they actually exist in the skill directory.
_CANDIDATE_DIRECTORIES: list[str] = ["prompts", "reference", "templates", "eval", "tests"]
_CANDIDATE_FILES: list[str] = ["SKILL.md", "pipeline.yaml", "constitution.md", "README.md"]


# ---------------------------------------------------------------------------
# Warning sink
# ---------------------------------------------------------------------------


class WarnSink:
    """Collects heuristic warnings + flushes them to stderr.

    A small wrapper instead of ``logging`` so tests can capture deterministic
    output via capsys.
    """

    def __init__(self, stream: Any | None = None) -> None:
        self._stream = stream if stream is not None else sys.stderr
        self.warnings: list[str] = []

    def warn(self, message: str) -> None:
        self.warnings.append(message)
        print(f"[warn] {message}", file=self._stream)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ExtractError(Exception):
    """Actionable extraction failure.

    The first line is the failure summary; subsequent lines are concrete
    "fix this by ..." hints. Per CONTRACT §3.E error_message_actionable_rate
    must be >= 90%.
    """


def _actionable(summary: str, hints: Iterable[str]) -> str:
    body = "\n".join(f"  -> {h}" for h in hints)
    return f"{summary}\n{body}" if body else summary


# ---------------------------------------------------------------------------
# Skill loading
# ---------------------------------------------------------------------------


def _load_skill(skill_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Read the SKILL.md frontmatter + pipeline.yaml of a skill directory."""
    if not skill_dir.exists():
        raise ExtractError(
            _actionable(
                f"skill directory not found: {skill_dir}",
                [
                    "verify the path is spelled correctly",
                    "pass an absolute path or run from the repo root",
                ],
            )
        )
    if not skill_dir.is_dir():
        raise ExtractError(
            _actionable(
                f"skill path is not a directory: {skill_dir}",
                ["pass the directory that contains SKILL.md, not a file path"],
            )
        )

    skill_md = skill_dir / "SKILL.md"
    pipeline_yaml = skill_dir / "pipeline.yaml"

    if not skill_md.exists():
        raise ExtractError(
            _actionable(
                f"SKILL.md missing in {skill_dir}",
                [
                    f"create {skill_md} with frontmatter (name/version/type/requires/outputs)",
                    "see skills/uxeval/SKILL.md for a reference layout",
                ],
            )
        )
    if not pipeline_yaml.exists():
        raise ExtractError(
            _actionable(
                f"pipeline.yaml missing in {skill_dir}",
                [
                    f"create {pipeline_yaml} declaring stages / mode_prompt",
                    "see skills/uxeval/pipeline.yaml for a reference layout",
                ],
            )
        )

    try:
        frontmatter, _ = parse_frontmatter(skill_md)
    except Exception as exc:  # pragma: no cover - kernel raises ConfigError
        raise ExtractError(
            _actionable(
                f"failed to parse SKILL.md frontmatter: {exc}",
                [
                    "ensure the file starts with '---' and ends the block with '---'",
                    "validate the YAML between the delimiters with `python -c \"import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])\"`",
                ],
            )
        ) from exc

    try:
        pipeline_raw: Any = yaml.safe_load(pipeline_yaml.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ExtractError(
            _actionable(
                f"invalid YAML in {pipeline_yaml}: {exc}",
                [
                    "run `python -c \"import yaml; yaml.safe_load(open('pipeline.yaml').read())\"` to locate the syntax error",
                ],
            )
        ) from exc

    if not isinstance(pipeline_raw, dict):
        raise ExtractError(
            _actionable(
                f"pipeline.yaml must be a mapping: {pipeline_yaml}",
                ["wrap top-level entries (stages, mode_prompt, ...) in a single mapping"],
            )
        )

    return frontmatter, cast(dict[str, Any], pipeline_raw)


# ---------------------------------------------------------------------------
# Archetype detection
# ---------------------------------------------------------------------------


def _detect_archetype(frontmatter: dict[str, Any], warn: WarnSink) -> ArchetypeName:
    output_types: list[str] = [
        str(o.get("type", ""))
        for o in frontmatter.get("outputs", [])
        if isinstance(o, dict)
    ]
    eval_hits = sum(1 for t in output_types if t in _EVALUATION_SIGNAL_OUTPUTS)
    gen_hits = sum(1 for t in output_types if t in _GENERATION_SIGNAL_OUTPUTS)
    ana_hits = sum(1 for t in output_types if t in _ANALYSIS_SIGNAL_OUTPUTS)
    scores: dict[ArchetypeName, int] = {
        "evaluation": eval_hits,
        "generation": gen_hits,
        "analysis": ana_hits,
    }
    best = max(scores, key=lambda k: scores[k])
    if scores[best] == 0:
        raise ExtractError(
            _actionable(
                "could not auto-detect archetype: no recognized OutputType in frontmatter",
                [
                    "declare at least one of issue_report/html_report/evidence_pack (evaluation)",
                    "OR prototype_code/frontend_code (generation)",
                    "OR analysis_report/comparison_matrix (analysis)",
                    "OR pass --archetype evaluation|generation|analysis explicitly",
                ],
            )
        )
    # If two archetypes tie, keep the deterministic priority: evaluation > generation > analysis.
    tied = [a for a, s in scores.items() if s == scores[best]]
    if len(tied) > 1:
        warn.warn(
            f"archetype detection ambiguous (tied: {tied}); picked '{best}'. "
            "Pass --archetype to disambiguate."
        )
    return best


# ---------------------------------------------------------------------------
# Stage / checkpoint / gate extraction
# ---------------------------------------------------------------------------


def _stages_of(pipeline: dict[str, Any]) -> list[dict[str, Any]]:
    raw = pipeline.get("stages", [])
    if not isinstance(raw, list):
        return []
    return [s for s in raw if isinstance(s, dict)]


def _stage_modes(stage: dict[str, Any]) -> list[str]:
    """Return the modes a stage is restricted to via ``only_when``.

    Recognises ``mode == "X"`` and ``mode in ["A", "B"]``. Anything else
    yields an empty list, meaning "no mode restriction".
    """
    only = stage.get("only_when")
    if not isinstance(only, str):
        return []
    text = only.strip()
    # mode == "client"
    if "==" in text:
        rhs = text.split("==", 1)[1].strip().strip('"').strip("'")
        return [rhs] if rhs else []
    # mode in ["client", "web"]
    if " in " in text and "[" in text and "]" in text:
        inside = text.split("[", 1)[1].split("]", 1)[0]
        return [v.strip().strip('"').strip("'") for v in inside.split(",") if v.strip()]
    return []


def _slot_id_for(stage_id: str, archetype: ArchetypeName) -> str | None:
    rules = _ARCHETYPE_RULES[archetype]
    sid = stage_id.lower()
    for keywords, slot in rules:
        if any(k in sid for k in keywords):
            return slot
    return None


def _stage_type(stage: dict[str, Any], warn: WarnSink) -> StageType:
    raw = str(stage.get("type", "")).lower()
    if raw == "llm":
        return StageType.LLM
    if raw == "tool":
        return StageType.TOOL
    if raw == "composite":
        return StageType.COMPOSITE
    warn.warn(
        f"stage '{stage.get('id', '?')}' missing/unknown type '{raw}'; defaulted to 'llm'. "
        "Set `type: llm|tool|composite` in pipeline.yaml."
    )
    return StageType.LLM


def _extract_stage_slots(
    pipeline: dict[str, Any],
    skill_modes: list[str],
    archetype: ArchetypeName,
    warn: WarnSink,
) -> list[StageSlot]:
    by_slot: dict[str, dict[str, Any]] = {}
    for stage in _stages_of(pipeline):
        sid = str(stage.get("id", ""))
        slot = _slot_id_for(sid, archetype)
        if slot is None:
            warn.warn(
                f"stage '{sid}' has no canonical slot mapping; dropped from archetype topology. "
                f"Add a keyword to extract.py rules if it should map."
            )
            continue
        bucket = by_slot.setdefault(
            slot,
            {
                "stages": [],
                "stage_type": _stage_type(stage, warn),
                "modes": set(),
                "inputs": [],
                "outputs": [],
            },
        )
        cast(list[Any], bucket["stages"]).append(sid)
        # Use the first stage's type as the slot type. If a later stage has a
        # different type, warn — slots are meant to be type-stable.
        next_type = _stage_type(stage, warn)
        if next_type is not bucket["stage_type"]:
            warn.warn(
                f"slot '{slot}' contains stages of different types ({bucket['stage_type']} vs {next_type}); "
                f"keeping {bucket['stage_type']}."
            )
        modes_set = cast(set[str], bucket["modes"])
        modes_set.update(_stage_modes(stage))
        for inp in stage.get("inputs", []) or []:
            if isinstance(inp, str) and inp not in cast(list[str], bucket["inputs"]):
                cast(list[str], bucket["inputs"]).append(inp)
        for out in stage.get("outputs", []) or []:
            if isinstance(out, str) and out not in cast(list[str], bucket["outputs"]):
                cast(list[str], bucket["outputs"]).append(out)

    slots: list[StageSlot] = []
    for slot_id, bucket in by_slot.items():
        # If the union of mode constraints covers every mode declared in the
        # skill, there's effectively no restriction; clear the list so the
        # archetype reads "applies to every mode".
        modes_set = cast(set[str], bucket["modes"])
        skill_mode_set = set(skill_modes)
        if not modes_set or (skill_mode_set and modes_set >= skill_mode_set):
            only_when_modes: list[str] = []
        else:
            only_when_modes = sorted(modes_set)

        stage_type = cast(StageType, bucket["stage_type"])
        slots.append(
            StageSlot(
                slot_id=slot_id,
                purpose=_purpose_for(slot_id),
                stage_type=stage_type,
                required=not bool(only_when_modes),
                only_when_modes=only_when_modes,
                required_inputs=cast(list[str], bucket["inputs"]),
                required_outputs=cast(list[str], bucket["outputs"]),
            )
        )

    # Deterministic order matching the canonical evaluation.yaml so the
    # round-trip diff is stable.
    canonical_order = [slot for _, slot in _ARCHETYPE_RULES[archetype]]
    slots.sort(key=lambda s: canonical_order.index(s.slot_id) if s.slot_id in canonical_order else 999)
    return slots


def _purpose_for(slot_id: str) -> str:
    purposes: dict[str, str] = {
        "understanding": "Parse PRD into modules / roles / scenarios / key_tasks.",
        "principle_mapping": "Pick heuristic principles relevant to scope.",
        "modeling": "Build the user-journey / task-flow model the eval will trace.",
        "task_generation": "Convert journey/model into a task checklist.",
        "evidence_planning": "Plan what evidence each task needs (mode-specific).",
        "evidence_collection": "Capture evidence (screenshots / DOM / trace).",
        "issue_attribution": "Detect issues + attribute to principles + bind evidence.",
        "delivery_audit": "Runtime audit deciding final/fallback/supplement/blocked.",
        "report_generation": "Render issues + evidence into Excel + HTML report.",
        # Generation
        "ia_planning": "Plan information architecture from PRD.",
        "tokens": "Produce design tokens / palette.",
        "component_planning": "Plan components from IA.",
        "code_generation": "Generate prototype / frontend code.",
        "self_review": "Self-review output for spec compliance.",
        # Analysis
        "scoping": "Frame the analysis scope.",
        "data_collection": "Collect competitor / market data.",
        "comparison": "Build comparison matrix / scoring.",
        "synthesis": "Synthesize insights.",
        "report": "Render analysis report.",
    }
    return purposes.get(slot_id, f"Stage slot '{slot_id}' (extracted heuristically).")


def _extract_checkpoint_slots(
    pipeline: dict[str, Any], stage_to_slot: dict[str, str], warn: WarnSink
) -> list[CheckpointSlot]:
    slots: list[CheckpointSlot] = []
    for stage in _stages_of(pipeline):
        cp = stage.get("checkpoint")
        if not isinstance(cp, dict):
            continue
        cp_id = str(cp.get("id", "")).strip()
        if not cp_id:
            warn.warn(
                f"stage '{stage.get('id', '?')}' has a checkpoint without an id; skipped. "
                "Add `checkpoint.id: C<n>` in pipeline.yaml."
            )
            continue
        sid = str(stage.get("id", ""))
        slot_id = stage_to_slot.get(sid, "")
        if not slot_id:
            warn.warn(
                f"checkpoint '{cp_id}' attaches to unmapped stage '{sid}'; "
                "after_slot left blank. Add a slot mapping for the stage."
            )
        purpose = str(cp.get("message", "")).strip() or f"Checkpoint {cp_id}."
        slots.append(
            CheckpointSlot(
                checkpoint_id=cp_id,
                after_slot=slot_id,
                purpose=purpose,
                required=True,
            )
        )
    slots.sort(key=lambda c: c.checkpoint_id)
    return slots


def _extract_gate_slots(
    pipeline: dict[str, Any], stage_to_slot: dict[str, str], warn: WarnSink
) -> list[GateSlot]:
    slots: list[GateSlot] = []
    for stage in _stages_of(pipeline):
        # Gates may live on the stage itself or inside a nested ``gate:`` key.
        gate = stage.get("gate")
        if isinstance(gate, dict):
            gate_id = str(gate.get("checkpoint_id", "")).strip() or str(gate.get("id", "")).strip()
            if not gate_id:
                warn.warn(
                    f"stage '{stage.get('id', '?')}' has a gate without an id; skipped. "
                    "Add `gate.checkpoint_id: QG<n>` in pipeline.yaml."
                )
                continue
            sid = str(stage.get("id", ""))
            slot_id = stage_to_slot.get(sid, "")
            purpose = str(gate.get("message", "")).strip() or f"Gate {gate_id}."
            modes = _stage_modes({"only_when": gate.get("only_when", "")})
            slots.append(
                GateSlot(
                    gate_id=gate_id,
                    on_slot=slot_id,
                    purpose=purpose,
                    required=True,
                    only_when_modes=modes,
                )
            )
    # Dedupe gates with the same id (some pipelines list QG2 in multiple
    # places); keep the first occurrence + warn.
    seen: set[str] = set()
    deduped: list[GateSlot] = []
    for g in slots:
        if g.gate_id in seen:
            warn.warn(f"duplicate gate '{g.gate_id}' in pipeline; kept first occurrence.")
            continue
        seen.add(g.gate_id)
        deduped.append(g)
    deduped.sort(key=lambda g: g.gate_id)
    return deduped


# ---------------------------------------------------------------------------
# Other dimensions
# ---------------------------------------------------------------------------


def _extract_modes(frontmatter: dict[str, Any], pipeline: dict[str, Any]) -> list[str]:
    modes: list[str] = []
    for m in frontmatter.get("modes", []) or []:
        if isinstance(m, dict) and "id" in m:
            modes.append(str(m["id"]))
    if not modes:
        prompt = pipeline.get("mode_prompt")
        if isinstance(prompt, dict):
            for opt in prompt.get("options", []) or []:
                if isinstance(opt, dict) and "id" in opt:
                    modes.append(str(opt["id"]))
    return modes


def _mode_semantics_for(archetype: ArchetypeName, modes: list[str], warn: WarnSink) -> ModeSemantics:
    semantic_type: Literal["evidence_collection", "fidelity", "data_source", "none"]
    if archetype == "evaluation":
        semantic_type = "evidence_collection" if modes else "none"
    elif archetype == "generation":
        semantic_type = "fidelity" if modes else "none"
    elif archetype == "analysis":
        semantic_type = "data_source" if modes else "none"
    else:  # pragma: no cover - exhaustive for ArchetypeName
        semantic_type = "none"

    if modes:
        warn.warn(
            f"mode_semantics.semantic_type defaulted to '{semantic_type}' from the archetype. "
            "Confirm manually — the same word 'mode' carries different semantics across archetypes."
        )
    return ModeSemantics(
        semantic_type=semantic_type,
        allowed_modes=modes,
        must_be_single_mode=False,
    )


def _extract_evidence_contract(pipeline: dict[str, Any]) -> EvidenceContract | None:
    fields: list[str] = []
    for stage in _stages_of(pipeline):
        for out in stage.get("outputs", []) or []:
            if isinstance(out, str) and out.endswith("_assessment") and out not in fields:
                fields.append(out)
    if not fields:
        return None
    return EvidenceContract(
        required_fields=fields,
        trusted_evidence_threshold=0.99,
        fallback_evidence_threshold=0.85,
    )


def _extract_directory(skill_dir: Path) -> DirectoryRequirement:
    dirs = [d for d in _CANDIDATE_DIRECTORIES if (skill_dir / d).is_dir()]
    files = [f for f in _CANDIDATE_FILES if (skill_dir / f).is_file()]
    eval_layout = (skill_dir / "eval" / "promptfoo.yaml").exists()
    return DirectoryRequirement(
        required_directories=dirs,
        required_files=files,
        eval_layout=eval_layout,
    )


def _extract_outputs(frontmatter: dict[str, Any], archetype: ArchetypeName, warn: WarnSink) -> OutputRequirement:
    declared_types: list[str] = []
    for o in frontmatter.get("outputs", []) or []:
        if isinstance(o, dict):
            t = str(o.get("type", "")).strip()
            if t and t not in declared_types:
                declared_types.append(t)

    required_set: set[str]
    if archetype == "evaluation":
        required_set = _EVALUATION_REQUIRED_OUTPUTS & set(declared_types)
    elif archetype == "generation":
        required_set = _GENERATION_SIGNAL_OUTPUTS & set(declared_types)
    elif archetype == "analysis":
        required_set = _ANALYSIS_SIGNAL_OUTPUTS & set(declared_types)
    else:  # pragma: no cover
        required_set = set()

    optional = [t for t in declared_types if t not in required_set]

    valid_outputs: set[str] = {ot.value for ot in OutputType}
    required_enum: list[OutputType] = []
    for t in declared_types:
        if t in required_set:
            if t in valid_outputs:
                required_enum.append(OutputType(t))
            else:
                warn.warn(f"output type '{t}' is not a known kernel OutputType; dropped.")
    optional_enum: list[OutputType] = []
    for t in optional:
        if t in valid_outputs:
            optional_enum.append(OutputType(t))
        else:
            warn.warn(f"output type '{t}' is not a known kernel OutputType; dropped.")

    return OutputRequirement(required=required_enum, optional=optional_enum)


# ---------------------------------------------------------------------------
# Top-level extract
# ---------------------------------------------------------------------------


def extract(
    skill_dir: Path,
    archetype: ArchetypeName | None = None,
    *,
    warn_stream: Any | None = None,
) -> ArchetypeSpec:
    """Reverse-extract an :class:`ArchetypeSpec` from ``skill_dir``."""
    warn = WarnSink(warn_stream)
    frontmatter, pipeline = _load_skill(skill_dir)

    chosen: ArchetypeName = archetype if archetype is not None else _detect_archetype(frontmatter, warn)

    skill_modes = _extract_modes(frontmatter, pipeline)
    stage_slots = _extract_stage_slots(pipeline, skill_modes, chosen, warn)

    # Build a stage-id -> slot-id index for checkpoint / gate extraction.
    stage_to_slot: dict[str, str] = {}
    for stage in _stages_of(pipeline):
        sid = str(stage.get("id", ""))
        slot = _slot_id_for(sid, chosen)
        if slot is not None:
            stage_to_slot[sid] = slot

    checkpoints = _extract_checkpoint_slots(pipeline, stage_to_slot, warn)
    gates = _extract_gate_slots(pipeline, stage_to_slot, warn)

    description = str(frontmatter.get("description", "")).strip() or (
        f"Extracted from skills/{skill_dir.name}/."
    )
    if not frontmatter.get("description"):
        warn.warn(
            f"SKILL.md is missing a `description:` frontmatter key; defaulted. "
            f"Add a one-paragraph description to {skill_dir / 'SKILL.md'}."
        )

    spec = ArchetypeSpec(
        name=chosen,
        version="1.0.0",
        description=description,
        representative_skill=skill_dir.name,
        frontmatter=FrontmatterRequirement(
            required_keys=list(_DEFAULT_FRONTMATTER_KEYS),
            required_kernel_range=str(
                (frontmatter.get("requires", {}) or {}).get("kernel", ">=1.0.0,<2.0.0")
            ),
            skill_type="pipeline" if frontmatter.get("type", "pipeline") == "pipeline" else "group",
        ),
        outputs=_extract_outputs(frontmatter, chosen, warn),
        stage_slots=stage_slots,
        checkpoint_slots=checkpoints,
        gate_slots=gates,
        mode_semantics=_mode_semantics_for(chosen, skill_modes, warn),
        evidence_contract=_extract_evidence_contract(pipeline) if chosen == "evaluation" else None,
        delivery_contract=DeliveryContract() if chosen == "evaluation" else None,
        directory=_extract_directory(skill_dir),
        constitution_required=(skill_dir / "constitution.md").is_file(),
    )
    return spec


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def spec_to_yaml(spec: ArchetypeSpec) -> str:
    """Serialize an :class:`ArchetypeSpec` to deterministic YAML."""
    data = spec.model_dump(mode="json")
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="extract",
        description="Reverse-extract an archetype spec from an existing skill directory.",
    )
    parser.add_argument(
        "skill_dir",
        type=Path,
        help="Path to a skill directory (must contain SKILL.md + pipeline.yaml).",
    )
    parser.add_argument(
        "--archetype",
        choices=("evaluation", "generation", "analysis"),
        default=None,
        help="Force a specific archetype. If omitted, auto-detected from outputs.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Where to write the extracted YAML. Defaults to stdout.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    archetype: ArchetypeName | None = (
        cast(ArchetypeName, args.archetype) if args.archetype is not None else None
    )

    try:
        spec = extract(args.skill_dir, archetype)
    except ExtractError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2

    yaml_text = spec_to_yaml(spec)
    if args.output is not None:
        out_path: Path = args.output
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(yaml_text, encoding="utf-8")
        print(f"[ok] wrote {out_path}", file=sys.stderr)
    else:
        sys.stdout.write(yaml_text)
    return 0


if __name__ == "__main__":  # pragma: no cover - entrypoint
    # Make `python tools/extract.py …` work in addition to `python -m tools.extract …`.
    factory_root = Path(__file__).resolve().parent.parent
    repo_root = factory_root.parent
    for entry in (str(factory_root), str(repo_root)):
        if entry not in sys.path:
            sys.path.insert(0, entry)
    raise SystemExit(main())


__all__ = [
    "ExtractError",
    "WarnSink",
    "extract",
    "main",
    "spec_to_yaml",
]
