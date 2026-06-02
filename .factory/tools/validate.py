"""Validate a skill directory against an archetype specification.

Usage:
    python3 -m tools.validate <skill_dir> --archetype <evaluation|generation|analysis>

Exit codes:
    0 = skill passes all checks
    1 = skill fails one or more checks
    2 = usage error or archetype not found

Per CONTRACT §3.B, this validator enforces:
- Frontmatter required fields + kernel range + skill_type
- Required outputs (OutputType enums)
- Directory layout (required_directories / required_files / eval_layout)
- Stage slots (heuristic mapping from stage IDs to archetype slots)
- Checkpoint slots (C1/C2/C3 must exist)
- Gate slots (QG2/QG3 must exist)
- Mode semantics (allowed_modes / must_be_single_mode)
- Evidence contract (required_fields in pipeline state)
- Constitution requirement

Every violation includes an actionable fix suggestion (CONTRACT §3.E).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure factory and repo root are in sys.path for imports
_FACTORY_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = _FACTORY_ROOT.parent
for _p in (_REPO_ROOT, _FACTORY_ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from _kernel_bridge import OutputType, load_pipeline_skill, parse_frontmatter  # noqa: E402
from archetypes import ArchetypeSpec, load_archetype  # noqa: E402

# Stage slot heuristic mapping: map stage id keywords to archetype slot_id.
# Keywords match either dash-style (task-generation) or underscore-style
# (task_generation) since scaffold uses underscore-equal-to-slot-id by default
# while uxeval's hand-written pipeline uses dashes. Both are valid.
_STAGE_SLOT_KEYWORDS: dict[str, list[str]] = {
    "understanding": [
        "understanding",
        "prd-understanding",
        "prd_understanding",
        "requirement-analysis",
        "requirement_analysis",
    ],
    "principle_mapping": [
        "principle-mapping",
        "principle_mapping",
        "principle",
        "heuristic-mapping",
        "heuristic_mapping",
    ],
    "modeling": [
        "modeling",
        "journey-modeling",
        "journey_modeling",
        "user-journey",
        "user_journey",
    ],
    "task_generation": [
        "task-generation",
        "task_generation",
        "task-gen",
        "task_gen",
        "checklist-generation",
        "checklist_generation",
    ],
    "evidence_planning": [
        "evidence-planning",
        "evidence_planning",
        "evidence-plan",
        "evidence_plan",
    ],
    "evidence_collection": [
        "evidence-collection",
        "evidence_collection",
        "screenshot-loading",
        "screenshot_loading",
        "web-automation",
        "web_automation",
        "capture",
    ],
    "issue_attribution": [
        "issue-attribution",
        "issue_attribution",
        "attribution",
        "detection",
    ],
    "delivery_audit": [
        "delivery-audit",
        "delivery_audit",
        "audit",
        "readiness-audit",
        "readiness_audit",
    ],
    "report_generation": [
        "report-generation",
        "report_generation",
        "report",
        "output",
    ],
    # ─── generation archetype slots (prd2proto, ip-design, ...)
    "prd_understanding": [
        "prd-understanding",
        "prd_understanding",
        "prd-understand",
    ],
    "design_analysis": [
        "design-analysis",
        "design_analysis",
        "ia-analysis",
    ],
    "spec_generation": [
        "spec-generation",
        "spec_generation",
        "design-spec-generation",
    ],
    "dsl_fetch": [
        "dsl-fetch",
        "dsl_fetch",
        "fetch-dsl",
    ],
    "token_extraction": [
        "token-extraction",
        "token_extraction",
        "extract-tokens",
    ],
    "code_generation": [
        "code-generation",
        "code_generation",
        "codegen",
        "generate-code",
    ],
    "review_gate": [
        "review-gate",
        "review_gate",
        "review",
        "quality-review",
    ],
    "preview_launch": [
        "preview-launch",
        "preview_launch",
        "preview",
    ],
    # ─── analysis archetype slots (ai-analytics)
    "requirement_understanding": [
        "requirement-understanding",
        "requirement_understanding",
        "brief-analysis",
    ],
    "data_collection": [
        "data-collection",
        "data_collection",
        "scrape",
        "collect",
    ],
    "methodology_selection": [
        "methodology-selection",
        "methodology_selection",
        "method-pick",
    ],
    "analysis": [
        "analysis",
    ],
    "strategy_synthesis": [
        "strategy-synthesis",
        "strategy_synthesis",
        "synthesis",
        "strategy",
    ],
    # ─── creative-generation archetype slots (ip-design, brand-creative, ...)
    "strategy_alignment": [
        "strategy-alignment",
        "strategy_alignment",
        "brand-strategy",
        "brand_strategy",
    ],
    "worldview_building": [
        "worldview-building",
        "worldview_building",
        "worldview",
    ],
    "persona_modeling": [
        "persona-modeling",
        "persona_modeling",
        "persona",
        "character-modeling",
    ],
    "visual_translation": [
        "visual-translation",
        "visual_translation",
        "visual-system",
        "visual_system",
    ],
    "narrative_planning": [
        "narrative-planning",
        "narrative_planning",
        "content-planning",
        "content_planning",
    ],
    "landing_spec": [
        "landing-spec",
        "landing_spec",
        "material-spec",
        "brand-material",
    ],
}


class Violation:
    """A single validation failure with actionable fix suggestion."""

    def __init__(self, dimension: str, message: str, fix: str) -> None:
        self.dimension = dimension
        self.message = message
        self.fix = fix

    def __repr__(self) -> str:
        return f"Violation({self.dimension}: {self.message})"


class Validator:
    """Validates a skill directory against an archetype specification."""

    def __init__(self, skill_dir: Path, archetype: ArchetypeSpec) -> None:
        self.skill_dir = skill_dir.resolve()
        self.archetype = archetype
        self.violations: list[Violation] = []

    def validate(self) -> bool:
        """Run all validation checks. Returns True if all pass."""
        # Check basic structure first (before kernel load attempt)
        self._check_frontmatter()
        self._check_directory()
        self._check_constitution()

        # Check 0: Can the skill be loaded by kernel?
        self._check_kernel_loadability()
        if any(v.dimension == "kernel_loadability" for v in self.violations):
            # If not loadable, skip pipeline-dependent checks
            return False

        # Check remaining archetype dimensions (require loaded pipeline)
        self._check_outputs()
        self._check_stage_slots()
        self._check_checkpoint_slots()
        self._check_gate_slots()
        self._check_mode_semantics()
        self._check_evidence_contract()

        return len(self.violations) == 0

    def _check_kernel_loadability(self) -> None:
        """Check if the skill can be loaded by kernel (CONTRACT §3.A)."""
        try:
            load_pipeline_skill(self.skill_dir)
        except Exception as exc:
            self.violations.append(
                Violation(
                    dimension="kernel_loadability",
                    message=f"skill is not loadable by kernel: {exc}",
                    fix=(
                        "Ensure SKILL.md has valid frontmatter and pipeline.yaml "
                        "exists with valid YAML syntax. Run "
                        f"`python3 -c 'from kernel.skill_loader import load_pipeline_skill; "
                        f"load_pipeline_skill(Path(\"{self.skill_dir}\"))'` to see the full error."
                    ),
                )
            )

    def _check_frontmatter(self) -> None:
        """Check frontmatter required fields, kernel range, skill_type."""
        skill_md = self.skill_dir / "SKILL.md"
        if not skill_md.exists():
            self.violations.append(
                Violation(
                    dimension="frontmatter",
                    message="SKILL.md is missing",
                    fix=f"Create {skill_md} with YAML frontmatter delimited by '---'.",
                )
            )
            return

        try:
            fm, _body = parse_frontmatter(skill_md)
        except Exception as exc:
            self.violations.append(
                Violation(
                    dimension="frontmatter",
                    message=f"SKILL.md frontmatter is invalid: {exc}",
                    fix="Fix the YAML syntax in the frontmatter block between '---' delimiters.",
                )
            )
            return

        # Check required keys
        for key in self.archetype.frontmatter.required_keys:
            if key not in fm:
                self.violations.append(
                    Violation(
                        dimension="frontmatter",
                        message=f"missing required frontmatter key: {key}",
                        fix=f"Add '{key}: <value>' to the frontmatter in {skill_md}.",
                    )
                )

        # Check kernel range
        requires = fm.get("requires", {})
        if isinstance(requires, dict):
            kernel_range = requires.get("kernel", "")
            expected = self.archetype.frontmatter.required_kernel_range
            if kernel_range != expected:
                self.violations.append(
                    Violation(
                        dimension="frontmatter",
                        message=f"kernel range is '{kernel_range}', expected '{expected}'",
                        fix=f"Set 'requires.kernel: \"{expected}\"' in {skill_md} frontmatter.",
                    )
                )

        # Check skill_type
        skill_type = fm.get("type", "pipeline")
        expected_type = self.archetype.frontmatter.skill_type
        if skill_type != expected_type:
            self.violations.append(
                Violation(
                    dimension="frontmatter",
                    message=f"skill type is '{skill_type}', expected '{expected_type}'",
                    fix=f"Set 'type: {expected_type}' in {skill_md} frontmatter.",
                )
            )

    def _check_outputs(self) -> None:
        """Check that required OutputTypes are declared."""
        skill_md = self.skill_dir / "SKILL.md"
        if not skill_md.exists():
            return  # Already reported in frontmatter check

        try:
            fm, _body = parse_frontmatter(skill_md)
        except Exception:
            return  # Already reported

        outputs_raw = fm.get("outputs", [])
        if not isinstance(outputs_raw, list):
            self.violations.append(
                Violation(
                    dimension="outputs",
                    message="'outputs' must be a list in frontmatter",
                    fix=f"Change 'outputs:' to a YAML list in {skill_md}.",
                )
            )
            return

        declared_types: set[OutputType] = set()
        for entry in outputs_raw:
            if isinstance(entry, dict) and "type" in entry:
                try:
                    declared_types.add(OutputType(entry["type"]))
                except ValueError:
                    pass

        for required_type in self.archetype.outputs.required:
            if required_type not in declared_types:
                self.violations.append(
                    Violation(
                        dimension="outputs",
                        message=f"missing required output type: {required_type.value}",
                        fix=(
                            f"Add an output entry with 'type: {required_type.value}' "
                            f"to the 'outputs:' list in {skill_md}."
                        ),
                    )
                )

    def _check_directory(self) -> None:
        """Check required directories, files, and eval layout."""
        for dir_name in self.archetype.directory.required_directories:
            dir_path = self.skill_dir / dir_name
            if not dir_path.exists():
                self.violations.append(
                    Violation(
                        dimension="directory",
                        message=f"missing required directory: {dir_name}",
                        fix=f"Create directory {dir_path}.",
                    )
                )

        for file_name in self.archetype.directory.required_files:
            file_path = self.skill_dir / file_name
            if not file_path.exists():
                self.violations.append(
                    Violation(
                        dimension="directory",
                        message=f"missing required file: {file_name}",
                        fix=f"Create file {file_path}.",
                    )
                )

        if self.archetype.directory.eval_layout:
            eval_dir = self.skill_dir / "eval"
            golden_dir = eval_dir / "golden"
            failure_dir = eval_dir / "failure"
            promptfoo_yaml = eval_dir / "promptfoo.yaml"

            if not golden_dir.exists():
                self.violations.append(
                    Violation(
                        dimension="directory",
                        message="eval_layout=True but eval/golden/ is missing",
                        fix=f"Create directory {golden_dir} for golden test cases.",
                    )
                )
            if not failure_dir.exists():
                self.violations.append(
                    Violation(
                        dimension="directory",
                        message="eval_layout=True but eval/failure/ is missing",
                        fix=f"Create directory {failure_dir} for failure test cases.",
                    )
                )
            if not promptfoo_yaml.exists():
                self.violations.append(
                    Violation(
                        dimension="directory",
                        message="eval_layout=True but eval/promptfoo.yaml is missing",
                        fix=f"Create {promptfoo_yaml} for promptfoo configuration.",
                    )
                )

    def _check_stage_slots(self) -> None:
        """Check that required stage slots are present in pipeline."""
        pipeline_yaml = self.skill_dir / "pipeline.yaml"
        if not pipeline_yaml.exists():
            self.violations.append(
                Violation(
                    dimension="stage_slots",
                    message="pipeline.yaml is missing",
                    fix=f"Create {pipeline_yaml} with a 'stages:' list.",
                )
            )
            return

        try:
            skill = load_pipeline_skill(self.skill_dir)
            stages = skill.get_stages()
        except Exception:
            return  # Already reported in kernel_loadability

        stage_ids = [s.id for s in stages]

        for slot in self.archetype.stage_slots:
            if not slot.required:
                continue

            # Heuristic mapping: check if any stage id matches keywords
            keywords = _STAGE_SLOT_KEYWORDS.get(slot.slot_id, [slot.slot_id])
            found = any(
                any(kw in stage_id for kw in keywords) for stage_id in stage_ids
            )

            if not found:
                self.violations.append(
                    Violation(
                        dimension="stage_slots",
                        message=f"missing required stage slot: {slot.slot_id}",
                        fix=(
                            f"Add a stage to pipeline.yaml with type={slot.stage_type.value} "
                            f"that implements '{slot.purpose}'. "
                            f"Expected stage id to match one of: {', '.join(keywords)}."
                        ),
                    )
                )

    def _check_checkpoint_slots(self) -> None:
        """Check that required checkpoints are present."""
        try:
            skill = load_pipeline_skill(self.skill_dir)
            stages = skill.get_stages()
        except Exception:
            return  # Already reported

        checkpoint_ids = {
            s.checkpoint.id for s in stages if s.checkpoint is not None
        }

        for slot in self.archetype.checkpoint_slots:
            if not slot.required:
                continue

            if slot.checkpoint_id not in checkpoint_ids:
                self.violations.append(
                    Violation(
                        dimension="checkpoint_slots",
                        message=f"missing required checkpoint: {slot.checkpoint_id}",
                        fix=(
                            f"Add a checkpoint with id='{slot.checkpoint_id}' "
                            f"after the '{slot.after_slot}' stage in pipeline.yaml. "
                            f"Purpose: {slot.purpose}"
                        ),
                    )
                )

    def _check_gate_slots(self) -> None:
        """Check that required gates are present."""
        try:
            skill = load_pipeline_skill(self.skill_dir)
            stages = skill.get_stages()
        except Exception:
            return  # Already reported

        gate_ids = {s.gate.checkpoint_id for s in stages if s.gate is not None and s.gate.checkpoint_id}

        for slot in self.archetype.gate_slots:
            if not slot.required:
                continue

            if slot.gate_id not in gate_ids:
                self.violations.append(
                    Violation(
                        dimension="gate_slots",
                        message=f"missing required gate: {slot.gate_id}",
                        fix=(
                            f"Add a gate with checkpoint_id='{slot.gate_id}' "
                            f"on the '{slot.on_slot}' stage in pipeline.yaml. "
                            f"Purpose: {slot.purpose}"
                        ),
                    )
                )

    def _check_mode_semantics(self) -> None:
        """Check mode constraints (allowed_modes, must_be_single_mode)."""
        skill_md = self.skill_dir / "SKILL.md"
        if not skill_md.exists():
            return

        try:
            fm, _body = parse_frontmatter(skill_md)
        except Exception:
            return

        modes_raw = fm.get("modes", [])
        if not isinstance(modes_raw, list):
            return

        mode_ids: list[str] = []
        for mode in modes_raw:
            if isinstance(mode, dict):
                mode_id = mode.get("id", "")
                if mode_id:
                    mode_ids.append(str(mode_id))
            elif isinstance(mode, str):
                mode_ids.append(mode)

        # Check must_be_single_mode
        if self.archetype.mode_semantics.must_be_single_mode and len(mode_ids) > 1:
            self.violations.append(
                Violation(
                    dimension="mode_semantics",
                    message=f"skill declares multiple modes {mode_ids}, but archetype requires single-mode",
                    fix=f"Remove extra modes from 'modes:' in {skill_md}, keep only one.",
                )
            )

        # Check allowed_modes
        if self.archetype.mode_semantics.allowed_modes:
            allowed = set(self.archetype.mode_semantics.allowed_modes)
            for mode_id in mode_ids:
                if mode_id not in allowed:
                    self.violations.append(
                        Violation(
                            dimension="mode_semantics",
                            message=f"mode '{mode_id}' is not allowed by archetype",
                            fix=(
                                f"Remove mode '{mode_id}' from {skill_md} or use one of: "
                                f"{', '.join(allowed)}."
                            ),
                        )
                    )

    def _check_evidence_contract(self) -> None:
        """Check that required evidence fields are produced in pipeline."""
        if self.archetype.evidence_contract is None:
            return

        try:
            skill = load_pipeline_skill(self.skill_dir)
            stages = skill.get_stages()
        except Exception:
            return

        all_outputs: set[str] = set()
        for stage in stages:
            all_outputs.update(stage.outputs)

        for field in self.archetype.evidence_contract.required_fields:
            if field not in all_outputs:
                self.violations.append(
                    Violation(
                        dimension="evidence_contract",
                        message=f"missing required evidence field: {field}",
                        fix=(
                            f"Add '{field}' to the 'outputs:' list of a stage in pipeline.yaml. "
                            f"This field is required by the {self.archetype.name} archetype."
                        ),
                    )
                )

    def _check_constitution(self) -> None:
        """Check that constitution.md exists if required."""
        if not self.archetype.constitution_required:
            return

        constitution_md = self.skill_dir / "constitution.md"
        if not constitution_md.exists():
            self.violations.append(
                Violation(
                    dimension="constitution",
                    message="constitution.md is missing",
                    fix=f"Create {constitution_md} with the skill's governance rules.",
                )
            )


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate a skill directory against an archetype specification."
    )
    parser.add_argument("skill_dir", type=Path, help="Path to the skill directory")
    parser.add_argument(
        "--archetype",
        required=True,
        choices=["evaluation", "generation", "analysis", "creative-generation"],
        help="Archetype name to validate against",
    )
    args = parser.parse_args()

    skill_dir: Path = args.skill_dir.resolve()
    if not skill_dir.exists():
        print(f"Error: skill directory does not exist: {skill_dir}", file=sys.stderr)
        return 2

    try:
        archetype = load_archetype(args.archetype)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(f"✅ Validating {skill_dir.name} against archetype '{args.archetype}' (v{archetype.version})")
    print()

    validator = Validator(skill_dir, archetype)
    passed = validator.validate()

    if passed:
        print("✅ All checks passed")
        return 0

    # Group violations by dimension
    by_dimension: dict[str, list[Violation]] = {}
    for v in validator.violations:
        by_dimension.setdefault(v.dimension, []).append(v)

    for dimension, violations in sorted(by_dimension.items()):
        print(f"❌ {dimension:<20} FAILED")
        for v in violations:
            print(f"   → {v.message}")
            print(f"   → fix: {v.fix}")
        print()

    print(f"Summary: {len(by_dimension)}/{9} dimensions failed, {len(validator.violations)} violation(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())


