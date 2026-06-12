# Batch 4A — UXEval Stage 7 Output Contract

## Scope

- Make `report-generation` return a real Stage 7 contract across:
  - `skills/uxeval/SKILL.md`
  - `skills/uxeval/pipeline.yaml`
  - `mcp-servers/excel-builder`
  - `kernel/pipeline/stage_runner.py`
  - `runs/<id>/run.yaml`
- Do not expand into image analysis, new skills, report schema redesign, or CLI feature work.

## Decisions

1. `SKILL.md` frontmatter stays the runtime declaration source for Stage 7 output ids and types.
2. `excel-builder.build_issue_report()` now returns same-named structured outputs:
   - `issue_report`
   - `html_report`
   - `evidence_pack`
3. `StageRunner` promotes those payloads into `ArtifactRef`, so `SkillResult.artifacts` and run manifests consume the same contract.
4. `html_report` is now a first-class `OutputType` instead of pretending to be `issue_report`.

## Real Sample

Generated on 2026-05-21 via `build_issue_report(..., output_dir="/private/tmp/batch4a-stage7-sample")`.

Returned payload:

```json
{
  "issue_report": {
    "id": "issue_report",
    "type": "issue_report",
    "path": "/private/tmp/batch4a-stage7-sample/issue_report.xlsx",
    "format": "xlsx",
    "summary": "uxeval issue workbook with 1 issues.",
    "sheet_count": 3,
    "issue_count": 1
  },
  "html_report": {
    "id": "html_report",
    "type": "html_report",
    "path": "/private/tmp/batch4a-stage7-sample/issue_report.html",
    "format": "html",
    "summary": "uxeval HTML report with 1 issues.",
    "issue_count": 1
  },
  "evidence_pack": {
    "id": "evidence_pack",
    "type": "evidence_pack",
    "path": "/private/tmp/batch4a-stage7-sample/evidence_pack",
    "format": "directory",
    "summary": "Evidence pack with manifest and structured source payloads.",
    "file_count": 4
  }
}
```

Materialized files:

```text
issue_report.xlsx
issue_report.html
evidence_pack/
  manifest.json
  issues.json
  journey_map.json
  principles.json
```

## Validation

- `tests/unit/test_kernel_pipeline.py`
- `tests/unit/test_kernel_skill_loader.py`
- `tests/unit/test_cli_run_history.py`
- `skills/uxeval/tests/test_frontmatter_runtime.py`
- `skills/uxeval/tests/test_pipeline_integration.py`
- `mcp-servers/excel-builder/tests/test_core.py`
- `tests/integration/test_kernel_mcp_integration.py`
- `tests/e2e/test_run_history_closure.py`
