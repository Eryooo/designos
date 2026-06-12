# Benchmark Performance Comparison

## Overview

This document provides performance comparison data for DesignOS's image analysis and UX evaluation capabilities across different scenarios. The benchmark framework measures quality, coverage, and automation effectiveness using golden test cases.

## Benchmark Framework

**Contract Version:** 2026-05-27  
**Execution Mode:** Client Mode  
**Harness Location:** `mcp-servers/image-analyzer/benchmark_harness.py`

## Key Metrics

### Coverage Metrics
| Metric | Target | Description |
|--------|--------|-------------|
| **Critical Path Page Hit Rate** | ≥90% | Percentage of critical user journey pages captured |
| **Critical Path State Hit Rate** | ≥90% | Percentage of key UI states (loading, error, success) documented |
| **P0 Page Coverage** | ≥90% | Must-have pages for minimum viable evaluation |
| **P0 State Coverage** | ≥80% | Must-have states for minimum viable evaluation |
| **P1 Page Coverage** | ≥70% | Important but not critical pages |
| **P1 State Coverage** | ≥60% | Important but not critical states |

### Trust Metrics
| Metric | Target | Description |
|--------|--------|-------------|
| **Trusted Mapping Rate** | ≥90% | Screenshot-to-feature mappings with high confidence |
| **Provisional Mapping Rate** | ≤10% | Low-confidence mappings requiring human review |
| **Conflicting Mapping Rate** | <5% | Contradictory evidence across sources |

### Success Metrics
| Metric | Target | Description |
|--------|--------|-------------|
| **First Pass Final Rate** | ≥70% | Cases reaching final delivery without remediation |
| **Auto Remediation Lift** | ≥15% | Additional cases saved by automatic gap-filling |

### Human Burden Metrics
| Metric | Target | Description |
|--------|--------|-------------|
| **Clarification Item Count** | ≤2 | Number of unclear requirements requiring user input |
| **Supplement Request Precision** | ≥85% | Accuracy of system requests for additional materials |
| **Low Value Work Return Rate** | <15% | False positives causing unnecessary manual work |

## Golden Test Cases

### Case 1: High Quality Mainline
**Scenario Class:** `final_capable`  
**Expected Outcome:** `final_delivery_ready`

**Input Characteristics:**
- 5 high-quality screenshots (1440×900)
- Complete OCR text extraction available
- Comprehensive description markdown
- Covers: login, dashboard, settings, report list, export success

**Performance Targets:**
- Critical path page hit rate: ≥90%
- Critical path state hit rate: ≥90%
- Trusted mapping rate: ≥90%
- Clarification count: 0

**Description:** Ideal scenario with complete evidence and clear documentation. System should produce production-ready output without human intervention.

---

### Case 2: High Quality Without Description
**Scenario Class:** `insufficient_description`  
**Expected Outcome:** `bounded_expected`

**Input Characteristics:**
- 5 high-quality screenshots
- No OCR backend available
- No description markdown provided
- Generic filenames (HQ9001.png - HQ9005.png)

**Performance Targets:**
- Delivery status: `fallback_safe`, `supplement_required`, or `blocked`
- Root cause: `input_truly_insufficient`
- Supplement request precision: ≥85%
- Clarification count: ≤1

**Description:** High visual quality but missing contextual information. System should safely identify gaps and request specific supplements rather than hallucinating.

---

### Case 3: Salvageable Input
**Scenario Class:** `salvageable`  
**Expected Outcome:** `final_capable`

**Input Characteristics:**
- 5 screenshots with generic names (shot-01.png - shot-05.png)
- Detailed description markdown with per-screen annotations
- OCR text available
- Covers: login, dashboard, settings, report list, notification center

**Performance Targets:**
- Critical path page hit rate: ≥90%
- Critical path state hit rate: ≥90%
- Auto remediation lift: ≥15%

**Description:** Initially ambiguous but salvageable through intelligent ingestion. Tests system's ability to cross-reference markdown descriptions with OCR and visual analysis.

---

### Case 4: Missing Evidence
**Scenario Class:** `missing_evidence`  
**Expected Outcome:** `bounded_expected`

**Input Characteristics:**
- Only 2 screenshots provided
- Description markdown covers login and dashboard only
- No OCR available
- Objectively insufficient for 5-module evaluation

**Performance Targets:**
- Delivery status: `supplement_required` or `blocked`
- Root cause: `input_truly_insufficient`
- Distance to 90%: clearly articulated
- Supplement request precision: ≥85%

**Description:** Genuinely insufficient input. System should precisely identify which evidence is missing and avoid low-value manual burden.

---

### Case 5: Complex Multi-Module
**Scenario Class:** `complex_multi_module`  
**Expected Outcome:** `final_capable`

**Input Characteristics:**
- 10 screenshots covering 5 modules × 2 states each
- Comprehensive markdown with per-screen annotations
- Rich OCR data (2 text lines per screenshot)
- Covers loading/success states for: login, dashboard, settings, reports, notifications

**Performance Targets:**
- Critical path page hit rate: ≥90%
- Critical path state hit rate: ≥90%
- Trusted mapping rate: ≥90%
- First pass final rate: ≥70%

**Description:** High-complexity scenario testing multi-state handling and cross-module consistency. Represents realistic production evaluation scope.

## Aggregate Performance Targets

### V1.5 Quality Gate

For a system release to meet V1.5 quality standards:

**Final-Capable Cases** (should reach `final_delivery_ready`):
- Critical path page hit rate ≥90%
- Critical path state hit rate ≥90%
- Trusted mapping rate ≥90%
- Clarification count = 0

**Bounded Cases** (should safely block on insufficient input):
- Delivery status: `fallback_safe`, `supplement_required`, or `blocked`
- Root cause: `input_truly_insufficient`
- Supplement request precision ≥85%
- Clarification count ≤1

### Freeze Recommendation Criteria

**Ready for Freeze:**
- All final-capable golden cases pass V1.5 line
- All bounded cases correctly identify input insufficiency
- No system ingestion gaps causing false blocks

**Needs One More Quality Lift:**
- At least one final-capable case still fails V1.5 line
- System ingestion gaps preventing final delivery

## Performance Analysis

### Strongest vs Weakest Case Ranking

Cases are ranked by:
1. Delivery status priority: `blocked` < `supplement_required` < `fallback_safe` < `final_delivery_ready`
2. Combined coverage score: critical_path_page_hit_rate + critical_path_state_hit_rate + trusted_mapping_rate
3. Inverse clarification count (fewer is better)

### Bottleneck Identification

The benchmark automatically identifies the most common unmet constraint across final-capable cases:

- **critical_path_page_hit_rate**: Insufficient page coverage detection
- **critical_path_state_hit_rate**: Missing UI state identification
- **trusted_mapping_rate**: Low confidence in screenshot-to-feature mapping
- **clarification_residue**: Excessive unclear requirements
- **objective_input_insufficiency**: Input quality limits (not a system bug)

## Benchmark Artifacts

Each benchmark run produces:

### JSON Output
**Location:** `outputs/benchmark/client_mode_benchmark_summary.json`

```json
{
  "contract_version": "2026-05-27",
  "run_mode": "client",
  "generated_at": "2026-06-08T...",
  "cases": [...],
  "aggregate": {
    "v1_5_target_met_rate": 0.800,
    "final_delivery_ready_case_count": 3,
    "strongest_case": {...},
    "weakest_case": {...},
    "largest_remaining_bottleneck_metric": "...",
    "freeze_recommendation": "..."
  }
}
```

### Markdown Report
**Location:** `outputs/benchmark/client_mode_benchmark_summary.md`

Human-readable summary with per-case metrics, aggregate statistics, and actionable recommendations.

## Running Benchmarks

### Prerequisites
```bash
# Ensure test environment is ready
pip install -e ".[dev]"
```

### Execute Golden Sweep
```python
from pathlib import Path
from mcp_servers.image_analyzer.benchmark_harness import run_golden_benchmark_sweep

output_dir = Path("/path/to/benchmark-output")
summary = run_golden_benchmark_sweep(output_dir)

print(f"V1.5 Target Met Rate: {summary['aggregate']['v1_5_target_met_rate']:.1%}")
print(f"Freeze Recommendation: {summary['aggregate']['freeze_recommendation']}")
```

### Validation Commands
```bash
# Syntax validation
./.venv/bin/python -m compileall mcp-servers/image-analyzer/

# Unit tests
./.venv/bin/python -m pytest -q mcp-servers/image-analyzer/tests/test_core.py

# Integration tests
./.venv/bin/python -m pytest -q tests/integration/test_kernel_mcp_integration.py

# Full test suite
./.venv/bin/python -m pytest -q

# Code quality
./.venv/bin/python -m ruff check .
./.venv/bin/python -m pyright
```

## Historical Context

### Batch 8: Metrics Instrumentation Foundation
**Date:** 2026-05-27  
**Goal:** Transform client mode from "feature fix pipeline" to "metrics-driven system"

**Achievements:**
- Unified `client_mode_metrics` runtime output
- Stable benchmark artifact generation
- Machine-readable performance contract
- Coverage/trust/success/human-burden four-category metrics

**Impact:** Enabled horizontal metric comparison across batches without guessing "better at doing" vs "better at blocking."

### Quality Journey
- **Route B Batch 8:** Metrics instrumentation + benchmark harness core
- **Route B Batch 9:** Benchmark-driven quality lift (core)
- **Route B Batch 10:** Golden benchmark sweep validation

## Interpreting Results

### Delivery Status Classification

| Status | Meaning | Action |
|--------|---------|--------|
| `final_delivery_ready` | ≥90% coverage + confidence, ready for production | Ship to downstream |
| `fallback_safe` | Usable but below ideal thresholds | Review before shipping |
| `supplement_required` | Missing specific evidence, system knows what | Provide targeted materials |
| `blocked` | Critical gaps prevent evaluation | Major input rework needed |

### Root Cause Analysis

| Root Cause | Interpretation | Resolution |
|------------|----------------|------------|
| `input_truly_insufficient` | User didn't provide enough materials | Request specific supplements |
| `system_ingestion_gap` | Materials exist but system can't extract them | System quality improvement needed |

### Distance to 90%+ Threshold

When a case doesn't meet targets, `distance_to_90_plus` lists specific gaps:

```
- critical_path_page_hit_rate: 0.75 (need 0.90+)
- trusted_mapping_rate: 0.82 (need 0.90+)
```

This enables surgical quality improvements rather than broad guessing.

## Integration with DesignOS Skills

The benchmark framework validates the foundation for these skills:

- **uxeval (v1.0.0):** Heuristic UX evaluation engine
- **prd2proto (v0.2.0):** PRD to prototype pipeline
- **ai-analytics (v0.1.0):** Analytics system audit

All skills inherit the same quality standards and metrics instrumentation.

## Future Enhancements

- **Web Mode Benchmarks:** Extend framework to web-based evidence
- **OCR Backend Comparison:** Tesseract vs cloud OCR performance
- **Multi-language Support:** Benchmark non-English UI evaluation
- **Streaming Metrics:** Real-time quality feedback during long runs
- **Regression Detection:** Automated alerts when metrics degrade

## References

- **Benchmark Harness:** `mcp-servers/image-analyzer/benchmark_harness.py`
- **Core Schemas:** `mcp-servers/image-analyzer/schemas.py`
- **Runtime Engine:** `mcp-servers/image-analyzer/core.py`
- **Design Docs:** `docs/plans/2026-05-27-route-b-batch-8-metrics-instrumentation-benchmark-harness-core.md`

---

**Last Updated:** 2026-06-08  
**Benchmark Contract Version:** 2026-05-27
