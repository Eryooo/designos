"""Scaffold a new skill skeleton from an archetype spec.

Per CONTRACT §3.A and §4 Gate 2, the produced skeleton must immediately:

- Be loadable by ``kernel.skill_loader.load_pipeline_skill`` without error.
- Pass ``kernel.preflight.PreflightChecker.check`` against a minimal context.
- Pass ``validate.py`` (downstream Agent B will consume the same archetype).

The scaffold writes a *minimal-but-compliant* tree: enough structure for the
kernel and the factory validators to be happy, plus placeholder content for
business prompts, knowledge files, templates, golden cases and tests.

CLI shape::

    python3 -m tools.scaffold \\
        --archetype <evaluation|generation|analysis> \\
        --name <skill-name> \\
        [--output-dir <dir>] \\
        [--dry-run] \\
        [--force]

The module is importable as ``scaffold`` (see ``main`` / ``scaffold_skill``).
"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

# Absolute import: callers add `.factory/` to sys.path so the bridge is at top level.
from archetypes import load_archetype
from archetypes.archetype_schema import (
    ArchetypeSpec,
    CheckpointSlot,
    GateSlot,
    StageSlot,
)
from _kernel_bridge import StageType


_DEFAULT_OUTPUT_DIR: Path = Path(__file__).resolve().parents[2] / "skills"

# MCP servers used in the scaffolded SKILL.md frontmatter. Both are builtin
# and ship with the repo's mcp-servers/ tree, so PreflightChecker can locate
# them without external probes — preflight stays green for the new skill out
# of the box. Skill authors can expand the list as they wire real tools.
_DEFAULT_MCP_SERVERS: list[str] = ["pdf-parser", "excel-builder"]


# ---------------------------------------------------------------------------
# Plan model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScaffoldPlan:
    """Materialised plan describing exactly what scaffold will write."""

    skill_dir: Path
    directories: tuple[Path, ...]
    files: tuple[tuple[Path, str], ...]

    def all_relative_paths(self) -> list[Path]:
        """All paths (dirs + files) relative to ``skill_dir`` for display."""
        rels: list[Path] = []
        for d in self.directories:
            rels.append(d.relative_to(self.skill_dir))
        for path, _content in self.files:
            rels.append(path.relative_to(self.skill_dir))
        return sorted(rels)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def scaffold_skill(
    *,
    archetype_name: str,
    skill_name: str,
    output_dir: Path | None = None,
    dry_run: bool = False,
    force: bool = False,
) -> ScaffoldPlan:
    """Build a skill skeleton on disk and return the materialised plan.

    Args:
        archetype_name: One of ``evaluation`` / ``generation`` / ``analysis``.
        skill_name: New skill folder name (must be a valid identifier).
        output_dir: Parent directory; the skill is created at
            ``output_dir/skill_name``. Defaults to ``<repo>/skills``.
        dry_run: When ``True`` returns the plan without touching the filesystem.
        force: When ``True`` overwrites an existing skill directory.

    Raises:
        ValueError: When ``skill_name`` is empty or not a safe identifier.
        FileExistsError: When the skill directory exists and ``force`` is
            ``False``.
        FileNotFoundError: Bubbled from ``load_archetype`` when the spec is
            unknown.
    """
    if not skill_name or not skill_name.strip():
        raise ValueError("skill_name must be non-empty")
    cleaned: str = skill_name.strip()
    if not _is_safe_identifier(cleaned):
        raise ValueError(
            f"skill_name '{cleaned}' must contain only letters, digits, hyphens or underscores; "
            "fix: rename to e.g. 'ai-analytics' or 'design_acceptance'"
        )

    spec: ArchetypeSpec = load_archetype(archetype_name)

    parent: Path = (output_dir if output_dir is not None else _DEFAULT_OUTPUT_DIR).resolve()
    skill_dir: Path = parent / cleaned

    if skill_dir.exists() and not force and not dry_run:
        raise FileExistsError(
            f"target directory already exists: {skill_dir}; "
            "fix: pass --force to overwrite, or pick a different --name"
        )

    plan: ScaffoldPlan = _build_plan(spec=spec, skill_dir=skill_dir, skill_name=cleaned)

    if dry_run:
        return plan

    _materialise(plan=plan, force=force)
    return plan


# ---------------------------------------------------------------------------
# Plan builders
# ---------------------------------------------------------------------------


def _build_plan(*, spec: ArchetypeSpec, skill_dir: Path, skill_name: str) -> ScaffoldPlan:
    directories: list[Path] = [skill_dir]
    files: list[tuple[Path, str]] = []

    # ---- top-level required directories from the archetype ---------------
    for rel_dir in spec.directory.required_directories:
        directories.append(skill_dir / rel_dir)

    # ---- top-level required files ----------------------------------------
    files.append((skill_dir / "SKILL.md", _render_skill_md(spec=spec, skill_name=skill_name)))
    files.append((skill_dir / "pipeline.yaml", _render_pipeline_yaml(spec=spec)))
    if spec.constitution_required:
        files.append((skill_dir / "constitution.md", _render_constitution_md(skill_name=skill_name)))
    files.append((skill_dir / "README.md", _render_readme_md(spec=spec, skill_name=skill_name)))

    # ---- prompts: one per stage slot (LLM stages get full content; tool stages
    #              get a "no-prompt" placeholder doc so the directory is populated) ----
    indexed_slots: list[tuple[int, StageSlot]] = list(enumerate(spec.stage_slots, start=1))
    for index, slot in indexed_slots:
        prompt_filename: str = _prompt_filename(index, slot)
        files.append(
            (skill_dir / "prompts" / prompt_filename, _render_prompt_placeholder(slot=slot))
        )

    # ---- reference knowledge bases for LLM stages ------------------------
    for index, slot in indexed_slots:
        if slot.stage_type != StageType.LLM:
            continue
        ref_filename: str = _reference_filename(index, slot)
        files.append(
            (skill_dir / "reference" / ref_filename, _render_reference_placeholder(slot=slot))
        )

    # ---- templates placeholder -------------------------------------------
    files.append(
        (
            skill_dir / "templates" / "report-template.md",
            _render_report_template_placeholder(skill_name=skill_name),
        )
    )

    # ---- eval layout (when archetype demands it) -------------------------
    if spec.directory.eval_layout:
        directories.extend(
            [
                skill_dir / "eval" / "golden",
                skill_dir / "eval" / "failure",
                skill_dir / "eval" / "golden" / "case-001-placeholder",
                skill_dir / "eval" / "golden" / "case-001-placeholder" / "input",
                skill_dir / "eval" / "golden" / "case-001-placeholder" / "expected",
                skill_dir / "eval" / "failure" / "F001-placeholder",
            ]
        )
        files.append(
            (skill_dir / "eval" / "promptfoo.yaml", _render_promptfoo_yaml(spec=spec))
        )
        files.append(
            (
                skill_dir / "eval" / "golden" / "case-001-placeholder" / "annotations.yaml",
                _render_annotations_yaml(),
            )
        )
        files.append(
            (
                skill_dir / "eval" / "golden" / "case-001-placeholder" / "input" / ".gitkeep",
                "",
            )
        )
        files.append(
            (
                skill_dir / "eval" / "golden" / "case-001-placeholder" / "expected" / ".gitkeep",
                "",
            )
        )
        files.append(
            (skill_dir / "eval" / "failure" / "F001-placeholder" / ".gitkeep", "")
        )

    # ---- tests directory --------------------------------------------------
    directories.append(skill_dir / "tests" / "fixtures")
    files.append((skill_dir / "tests" / "conftest.py", _render_tests_conftest()))
    files.append(
        (skill_dir / "tests" / "test_frontmatter_runtime.py", _render_test_frontmatter())
    )
    files.append(
        (skill_dir / "tests" / "test_pipeline_integration.py", _render_test_pipeline_integration())
    )
    files.append((skill_dir / "tests" / "fixtures" / "sample-prd.md", _render_sample_prd()))
    files.append((skill_dir / "tests" / "fixtures" / "sample-scope.md", _render_sample_scope()))

    # de-dupe directories preserving order
    seen: set[Path] = set()
    deduped_dirs: list[Path] = []
    for d in directories:
        if d not in seen:
            seen.add(d)
            deduped_dirs.append(d)

    return ScaffoldPlan(
        skill_dir=skill_dir,
        directories=tuple(deduped_dirs),
        files=tuple(files),
    )


# ---------------------------------------------------------------------------
# Materialisation
# ---------------------------------------------------------------------------


def _materialise(*, plan: ScaffoldPlan, force: bool) -> None:
    if plan.skill_dir.exists() and force:
        shutil.rmtree(plan.skill_dir)
    for directory in plan.directories:
        directory.mkdir(parents=True, exist_ok=True)
    for path, content in plan.files:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Renderers — SKILL.md
# ---------------------------------------------------------------------------


def _render_skill_md(*, spec: ArchetypeSpec, skill_name: str) -> str:
    description: str = (
        f"{skill_name} skill scaffold (archetype: {spec.name}). "
        "Replace this description before shipping."
    )
    frontmatter: dict[str, object] = {
        "name": skill_name,
        "version": "0.1.0",
        "type": spec.frontmatter.skill_type,
        "description": description,
        "requires": {
            "kernel": spec.frontmatter.required_kernel_range,
            "mcp_servers": [
                {"name": name, "builtin": True} for name in _DEFAULT_MCP_SERVERS
            ],
        },
        "outputs": _render_outputs_block(spec=spec),
    }
    if spec.mode_semantics.allowed_modes and not spec.mode_semantics.must_be_single_mode:
        frontmatter["modes"] = [
            {"id": mode_id, "label": f"{mode_id} mode (placeholder)"}
            for mode_id in spec.mode_semantics.allowed_modes
        ]

    yaml_block: str = yaml.safe_dump(
        frontmatter,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    ).strip()
    body: str = _render_skill_md_body(spec=spec, skill_name=skill_name)
    return f"---\n{yaml_block}\n---\n\n{body}\n"


def _render_outputs_block(*, spec: ArchetypeSpec) -> list[dict[str, str]]:
    """Map archetype required OutputType members to SKILL.md output entries."""
    out: list[dict[str, str]] = []
    for ot in spec.outputs.required:
        out.append(
            {
                "id": str(ot.value),
                "type": str(ot.value),
                "format": _default_format_for_output(ot.value),
            }
        )
    return out


def _default_format_for_output(output_type: str) -> str:
    """Pick a reasonable physical format for each OutputType.

    Skill authors will likely tune this; the goal here is a kernel-loadable
    default. Allowed formats: markdown, xlsx, html, json, directory.
    """
    if output_type == "issue_report":
        return "xlsx"
    if output_type == "html_report":
        return "html"
    if output_type in {"evidence_pack", "delivery_audit_bundle", "automated_eval_trace"}:
        return "directory"
    if output_type in {"prototype_code", "frontend_code", "evaluation_script"}:
        return "directory"
    if output_type in {"design_tokens", "design_token_spec", "page_mapping"}:
        return "json"
    return "markdown"


def _render_skill_md_body(*, spec: ArchetypeSpec, skill_name: str) -> str:
    return (
        f"# {skill_name} (scaffold)\n\n"
        f"This skill was scaffolded from the **{spec.name}** archetype. "
        "The structure is kernel-loadable but the prompts, knowledge bases "
        "and templates are placeholders — fill them in before running for real.\n\n"
        "## Triggering\n\n"
        "Define the natural-language triggers and slash commands here.\n\n"
        "## Pipeline overview\n\n"
        "See `pipeline.yaml`. Each stage delegates to a prompt under `prompts/` "
        "or to an MCP tool. Checkpoints (C1/C2/C3) and gates (QG*) are pre-wired "
        "to match the archetype contract.\n\n"
        "## Constitution\n\n"
        "See `constitution.md` for the non-negotiable rules.\n"
    )


# ---------------------------------------------------------------------------
# Renderers — pipeline.yaml
# ---------------------------------------------------------------------------


def _render_pipeline_yaml(*, spec: ArchetypeSpec) -> str:
    indexed_slots: list[tuple[int, StageSlot]] = list(enumerate(spec.stage_slots, start=1))

    # Index checkpoints and gates by the slot they attach to.
    checkpoints_by_slot: dict[str, list[CheckpointSlot]] = {}
    for cp in spec.checkpoint_slots:
        checkpoints_by_slot.setdefault(cp.after_slot, []).append(cp)
    gates_by_slot: dict[str, list[GateSlot]] = {}
    for g in spec.gate_slots:
        gates_by_slot.setdefault(g.on_slot, []).append(g)

    stages: list[dict[str, object]] = []
    for index, slot in indexed_slots:
        if not slot.required:
            # Skip optional slots in the scaffold to keep the pipeline minimal.
            continue
        stages.append(_render_stage(index=index, slot=slot,
                                    checkpoints=checkpoints_by_slot.get(slot.slot_id, []),
                                    gates=gates_by_slot.get(slot.slot_id, [])))

    pipeline: dict[str, object] = {
        "name": "scaffold-pipeline",
        "description": (
            "Auto-generated pipeline skeleton. Replace prompts and tool wiring "
            "before running."
        ),
        "stages": stages,
        "constitution": "constitution.md",
    }

    header: str = (
        "# Auto-generated by .factory/tools/scaffold.py — fill in business logic.\n"
        "# Stage IDs match archetype slot IDs; rename freely as long as the\n"
        "# canonical topology (checkpoints + gates) is preserved.\n\n"
    )
    body: str = yaml.safe_dump(
        pipeline,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    return header + body


def _render_stage(
    *,
    index: int,
    slot: StageSlot,
    checkpoints: list[CheckpointSlot],
    gates: list[GateSlot],
) -> dict[str, object]:
    stage: dict[str, object] = {
        "id": slot.slot_id,
        "type": str(slot.stage_type.value),
    }
    if slot.stage_type == StageType.LLM:
        stage["prompt"] = f"prompts/{_prompt_filename(index, slot)}"
        stage["knowledge"] = [f"reference/{_reference_filename(index, slot)}"]
    else:
        # Tool stages need an MCP server hint. Use a builtin we know exists so
        # preflight stays green; skill authors swap in the real server.
        stage["mcp_server"] = "excel-builder"
        stage["mcp_tool"] = f"placeholder_{slot.slot_id}"
    if slot.required_inputs:
        stage["inputs"] = list(slot.required_inputs)
    if slot.required_outputs:
        stage["outputs"] = list(slot.required_outputs)
    if slot.only_when_modes:
        stage["only_when"] = " or ".join(
            f'mode == "{m}"' for m in slot.only_when_modes
        )
    if checkpoints:
        cp = checkpoints[0]
        stage["checkpoint"] = {
            "id": cp.checkpoint_id,
            "message": cp.purpose,
            "allow": ["continue", "modify", "supplement"],
        }
    if gates:
        # Pick the first required gate as the primary gate; if multiple gates
        # land on the same slot, the scaffold preserves only one — the user
        # will replicate the rest by hand because each gate's `when` clause
        # is highly business-specific. The archetype spec only requires that
        # the canonical id appears somewhere in the pipeline.
        gate = next((g for g in gates if g.required), gates[0])
        stage["gate"] = {
            "when": "false  # TODO replace with real condition",
            "action": "pause",
            "checkpoint_id": gate.gate_id,
            "message": gate.purpose,
        }
    return stage


# ---------------------------------------------------------------------------
# Renderers — supporting docs
# ---------------------------------------------------------------------------


def _render_constitution_md(*, skill_name: str) -> str:
    return (
        f"# {skill_name} Constitution (placeholder)\n\n"
        "These rules are non-negotiable. Replace the placeholders before "
        "shipping. The eight-rule structure follows the evaluation archetype "
        "(uxeval baseline) but applies to any archetype with adaptation.\n\n"
        "1. Only output what the archetype scope permits.\n"
        "2. Every finding must cite explicit evidence.\n"
        "3. Map every finding to a known principle / rubric.\n"
        "4. Severity / quality ratings need a written rationale.\n"
        "5. Never invent inputs or outputs not present in the source.\n"
        "6. Mark all inferred content with `[inferred]`.\n"
        "7. Refuse to emit unsupported subjective claims.\n"
        "8. Evidence must demonstrably match the finding's scenario.\n"
    )


def _render_readme_md(*, spec: ArchetypeSpec, skill_name: str) -> str:
    return (
        f"# {skill_name}\n\n"
        f"Scaffolded from the **{spec.name}** archetype on first creation.\n\n"
        "## Status\n\n"
        "Skeleton only — prompts, knowledge bases, templates and golden cases "
        "are placeholders. Wire in business logic before running.\n\n"
        "## Quick checks\n\n"
        "```bash\n"
        f"python3 -c 'from kernel.skill_loader import load_pipeline_skill; "
        f"load_pipeline_skill(\"./skills/{skill_name}\")'\n"
        "```\n"
    )


def _render_prompt_placeholder(*, slot: StageSlot) -> str:
    role: str = "LLM" if slot.stage_type == StageType.LLM else "TOOL stage"
    return (
        f"# Stage: {slot.slot_id}\n\n"
        f"Type: `{slot.stage_type.value}` ({role}). Purpose: {slot.purpose}\n\n"
        "Replace this placeholder with the real prompt before running. The "
        "stage signature must continue to match the archetype contract:\n\n"
        f"- Required inputs: `{', '.join(slot.required_inputs) or '(none)'}`\n"
        f"- Required outputs: `{', '.join(slot.required_outputs) or '(none)'}`\n"
    )


def _render_reference_placeholder(*, slot: StageSlot) -> str:
    return (
        f"# Reference for `{slot.slot_id}`\n\n"
        f"{slot.purpose}\n\n"
        "Drop the domain knowledge for this stage here. The pipeline lazy-loads "
        "this file into the LLM context whenever the stage executes.\n"
    )


def _render_report_template_placeholder(*, skill_name: str) -> str:
    return (
        f"# {skill_name} report (placeholder)\n\n"
        "Replace this with the real Markdown / HTML template that backs the "
        "skill's primary artifact.\n"
    )


def _render_promptfoo_yaml(*, spec: ArchetypeSpec) -> str:
    cfg: dict[str, object] = {
        "description": f"{spec.name} skill scaffold prompt eval set",
        "prompts": [
            f"file://prompts/{_prompt_filename(idx, slot)}"
            for idx, slot in enumerate(spec.stage_slots, start=1)
            if slot.stage_type == StageType.LLM and slot.required
        ],
        "providers": [
            {
                "id": "anthropic:messages:claude-opus-4-7",
                "config": {"max_tokens": 8000, "temperature": 0.2},
            }
        ],
        "tests": [
            {
                "description": "placeholder golden case 001",
                "vars": {},
                "assert": [
                    {"type": "javascript", "value": "return true;  // TODO"},
                ],
            }
        ],
    }
    return (
        "# Auto-generated by scaffold; replace prompts/tests with real ones.\n"
        + yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True)
    )


def _render_annotations_yaml() -> str:
    return (
        "# Placeholder golden case annotations.\n"
        "case_id: case-001-placeholder\n"
        "summary: replace with the real golden-case summary\n"
        "expected_outcomes: []\n"
    )


# ---------------------------------------------------------------------------
# Renderers — tests
# ---------------------------------------------------------------------------


def _render_tests_conftest() -> str:
    return (
        '"""Shared pytest fixtures for the scaffolded skill."""\n'
        "\n"
        "from __future__ import annotations\n"
        "\n"
        "from pathlib import Path\n"
        "\n"
        "import pytest\n"
        "\n"
        "SKILL_DIR: Path = Path(__file__).resolve().parent.parent\n"
        "FIXTURES_DIR: Path = Path(__file__).resolve().parent / \"fixtures\"\n"
        "\n"
        "\n"
        "@pytest.fixture\n"
        "def skill_dir() -> Path:\n"
        "    \"\"\"Absolute path to this skill directory.\"\"\"\n"
        "    return SKILL_DIR\n"
        "\n"
        "\n"
        "@pytest.fixture\n"
        "def sample_prd_path() -> Path:\n"
        "    return FIXTURES_DIR / \"sample-prd.md\"\n"
        "\n"
        "\n"
        "@pytest.fixture\n"
        "def sample_scope_path() -> Path:\n"
        "    return FIXTURES_DIR / \"sample-scope.md\"\n"
    )


def _render_test_frontmatter() -> str:
    return (
        '"""Frontmatter sanity tests for the scaffolded skill."""\n'
        "\n"
        "from __future__ import annotations\n"
        "\n"
        "from pathlib import Path\n"
        "\n"
        "from kernel.skill_loader import parse_frontmatter\n"
        "\n"
        "\n"
        "def test_skill_md_has_required_top_level_keys(skill_dir: Path) -> None:\n"
        "    fm, _body = parse_frontmatter(skill_dir / \"SKILL.md\")\n"
        "    for key in (\"name\", \"version\", \"type\", \"requires\", \"outputs\"):\n"
        "        assert key in fm, f\"SKILL.md missing key: {key}\"\n"
        "\n"
        "\n"
        "def test_skill_md_declares_kernel_range(skill_dir: Path) -> None:\n"
        "    fm, _body = parse_frontmatter(skill_dir / \"SKILL.md\")\n"
        "    requires = fm.get(\"requires\") or {}\n"
        "    assert isinstance(requires, dict)\n"
        "    assert str(requires.get(\"kernel\", \"\")).startswith(\">=\")\n"
    )


def _render_test_pipeline_integration() -> str:
    return (
        '"""Pipeline-loader smoke tests for the scaffolded skill."""\n'
        "\n"
        "from __future__ import annotations\n"
        "\n"
        "from pathlib import Path\n"
        "\n"
        "from kernel.skill_loader.pipeline_loader import load_pipeline_skill\n"
        "\n"
        "\n"
        "def test_skill_dir_is_kernel_loadable(skill_dir: Path) -> None:\n"
        "    skill = load_pipeline_skill(skill_dir)\n"
        "    assert skill.config.name\n"
        "    assert skill.get_stages(), \"pipeline.yaml produced no stages\"\n"
        "\n"
        "\n"
        "def test_pipeline_yaml_exists(skill_dir: Path) -> None:\n"
        "    assert (skill_dir / \"pipeline.yaml\").exists()\n"
    )


def _render_sample_prd() -> str:
    return (
        "# Sample PRD (placeholder)\n\n"
        "Replace this fixture with a real PRD excerpt that exercises the skill's "
        "stage-1 understanding logic.\n"
    )


def _render_sample_scope() -> str:
    return (
        "# Sample scope (placeholder)\n\n"
        "- Goal: replace with a real evaluation goal.\n"
        "- Roles: replace with target user roles.\n"
        "- Out of scope: list anything the skill must NOT touch.\n"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _prompt_filename(index: int, slot: StageSlot) -> str:
    return f"{index:02d}-{slot.slot_id.replace('_', '-')}.md"


def _reference_filename(index: int, slot: StageSlot) -> str:
    return f"m{index:02d}-{slot.slot_id.replace('_', '-')}.md"


def _is_safe_identifier(value: str) -> bool:
    if not value:
        return False
    for ch in value:
        if not (ch.isalnum() or ch in "-_"):
            return False
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scaffold",
        description="Generate a kernel-loadable skill skeleton from an archetype.",
    )
    parser.add_argument(
        "--archetype",
        required=True,
        choices=["evaluation", "generation", "analysis"],
        help="Archetype family to scaffold from (matches .factory/archetypes/*.yaml).",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="New skill folder name (letters / digits / hyphen / underscore).",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Parent directory for the new skill. Defaults to <repo>/skills.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the file plan without writing anything.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing target directory.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser: argparse.ArgumentParser = _build_arg_parser()
    args = parser.parse_args(argv)
    output_dir: Path | None = Path(args.output_dir).resolve() if args.output_dir else None
    try:
        plan = scaffold_skill(
            archetype_name=args.archetype,
            skill_name=args.name,
            output_dir=output_dir,
            dry_run=bool(args.dry_run),
            force=bool(args.force),
        )
    except FileExistsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    mode_label: str = "[dry-run]" if args.dry_run else "[written]"
    print(f"{mode_label} skill_dir: {plan.skill_dir}")
    print(f"{mode_label} entries (sorted):")
    for rel in plan.all_relative_paths():
        print(f"  - {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
