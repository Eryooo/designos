# Changelog

All notable changes to DesignOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0a1] - 2026-05-29

Pre-release alpha covering the skills factory build-out and the prd2proto P1
skeleton. Distributed via the `factory-and-prd2proto-p1` branch only — not
yet published to PyPI / npm.

### Added

#### Skills Factory (`.factory/`)
- `CONTRACT.md` defines the factory's metric system (north-star indicators,
  five driver buckets, five acceptance gates) and the agent collaboration
  rules that govern parallel tool development.
- `_kernel_bridge.py` is the single import point for kernel schemas; the
  factory never redefines `SkillConfig` / `StageConfig` / `OutputType` etc.
- `archetypes/`: `ArchetypeSpec` Pydantic model + `evaluation.yaml`
  (extracted from uxeval) + `analysis.yaml` and `generation.yaml`
  (provisional placeholders to seed scaffolding before ai-analytics /
  prd2proto ship for real).
- `tools/extract.py`: reverse-extracts an `ArchetypeSpec` from any skill;
  uxeval round-trips at ≥90 % match against the hand-written archetype.
- `tools/validate.py`: archetype conformance checker with actionable fix
  suggestions. Catches eight+ violation classes (missing SKILL.md, broken
  pipeline, missing checkpoints/gates, output-type drift, etc.).
- `tools/scaffold.py`: one-shot generator that produces a skeleton already
  loadable by the kernel, passing preflight, and passing validate.
- 46 factory tests, all green; kernel zero-regression.

#### frontend-codegen Mock MCP (`mcp-servers/frontend-codegen/`)
- Four tools: `fetch_dsl`, `extract_tokens`, `map_components`,
  `generate_code`.
- Sources: Figma + MasterGo. Component libs: antd-vue, element-plus,
  antd-react, custom. Frameworks: React, Vue.
- Mock implementation produces a runnable skeleton; Pydantic schemas are
  stable so the P3 real implementation can swap in without changing
  pipeline wiring. 12 tests, all green.

#### prd2proto skill — P1 (`skills/prd2proto/`)
- Generation-archetype skill with eight stages, three modes
  (`pm` / `designer-spec` / `designer-dsl`), four checkpoints
  (C1/C2/C3/C4) and the `QG_REVIEW` gate.
- `figma-mcp` and `mastergo-mcp` are declared as builtin=false external
  dependencies guarded by `required_when='mode == "designer-dsl"'` so
  preflight prompts the user only when designer-dsl mode is selected.
- Four LLM stage prompts (01 prd-understanding / 02 design-analysis /
  03a spec-generation / 06 review-gate) plus matching reference
  knowledge bases covering Story Mapping, Atomic Design, W3C Design
  Tokens, and the four-rule code constitution.
- `test_p1_smoke.py` locks in the per-mode stage filtering, MCP wiring,
  and end-to-end mock codegen path. 14 tests total, all green.

#### Plans (`docs/plans/`)
- `2026-05-29-prd2proto-implementation-plan.md`: P1–P4 batch split,
  four-rule constitution rollout strategy, time estimates.
- `2026-05-29-prd2proto-p1-completion.md`: P1 deliverables and metrics.
- `2026-05-29-prd2proto-p1-trial-runbook.md`: operator manual for
  running a real PRD through pm mode on a fresh machine.
- `wave3-validation-checklist.md`: factory acceptance evidence.

### Changed
- Aligned `install.sh` `VERSION` with `pyproject.toml` and
  `npm-package/package.json` (was 0.2.0, now 0.5.0a1) so the three
  surfaces no longer disagree.

### Test baseline at 0.5.0a1
- `tests/unit/`: 180/180
- `.factory/tests/`: 46/46
- `mcp-servers/frontend-codegen/tests/`: 12/12
- `skills/prd2proto/tests/`: 14/14
- Total: **252/252, zero regression** vs the 0.4.0 baseline.

### Known limitations
- frontend-codegen is a mock; real DSL parsing / token extraction /
  component mapping arrives in P3.
- prd2proto's review-gate is an LLM soft check; it becomes a static
  AST-level constitution enforcer only after P3.
- Four scaffolding gaps captured in `.factory/CHANGELOG.md` v0.3.0
  backlog (no `inputs:` rendering, `only_when` not consumed, no external
  MCP declaration, MCP list not differentiated per archetype) — these
  will land in a follow-up factory iteration, not this alpha.

## [Unreleased]

### Added
- Initial repository bootstrap: pyproject.toml, ruff, pyright, pytest, GitHub Actions CI.
- Frozen `kernel/contracts/` interfaces, schemas, enums and error hierarchy.
- Typer-based CLI scaffold (`designos` entry point).
