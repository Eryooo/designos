"""Golden benchmark sweep harness for client-mode image-analyzer."""

from __future__ import annotations

import json
from contextlib import ExitStack
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable
from unittest.mock import patch

import core
from ocr_runtime import OCRLine, OCRProbeResult, OCRResult
from PIL import Image

_SWEEP_CONTRACT_VERSION = "2026-05-27"
_SWEEP_JSON_FILENAME = "golden_benchmark_sweep.json"
_SWEEP_MD_FILENAME = "golden_benchmark_sweep.md"


@dataclass(frozen=True)
class GoldenCase:
    case_id: str
    label: str
    scenario_class: str
    expectation: str
    description: str
    runner: Callable[[Path], Any]


def _write_png(path: Path, *, size: tuple[int, int] = (1440, 900)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, "white").save(path)


def _patch_ocr(
    stack: ExitStack,
    *,
    available: bool,
    lines_by_file: dict[str, tuple[str, ...]] | None = None,
) -> None:
    if available:
        stack.enter_context(
            patch.object(
                core,
                "probe_ocr_backend",
                lambda: OCRProbeResult(available=True, backend="tesseract"),
            )
        )
        stack.enter_context(
            patch.object(
                core,
                "run_ocr",
                lambda path, preferred_backend=None: OCRResult(
                    backend="tesseract",
                    lines=tuple(
                        OCRLine(text=text, confidence=0.93)
                        for text in (lines_by_file or {}).get(path.name, ())
                    ),
                    raw_text="\n".join((lines_by_file or {}).get(path.name, ())),
                ),
            )
        )
    else:
        stack.enter_context(
            patch.object(
                core,
                "probe_ocr_backend",
                lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
            )
        )


def _plan_and_analyze(
    *,
    screens: Path,
    output_dir: Path,
    modules: list[str],
    task_checklist_lite: str,
    journey_stages: list[str],
    key_features: list[str] | None = None,
    ocr_available: bool,
    ocr_lines_by_file: dict[str, tuple[str, ...]] | None = None,
    run_id: str,
) -> Any:
    with ExitStack() as stack:
        _patch_ocr(
            stack,
            available=ocr_available,
            lines_by_file=ocr_lines_by_file,
        )
        plan = core.plan_required_evidence(
            modules=[{"name": name} for name in modules],
            key_features=[{"name": name} for name in (key_features or modules)],
            task_checklist_lite=task_checklist_lite,
            journey_stages=journey_stages,
            screenshots_dir=screens,
            output_dir=output_dir,
            run_id=run_id,
            stage_id="evidence-planning",
        )
        return core.load_and_analyze(
            screens,
            task_checklist_lite=task_checklist_lite,
            required_evidence_plan=plan.required_evidence_plan,
            output_dir=output_dir,
            run_id=run_id,
            stage_id="screenshot-loading",
        )


def _case_high_quality_mainline(case_root: Path) -> Any:
    screens = case_root / "screens"
    output_dir = case_root / "outputs"
    for name in (
        "login-screen.png",
        "dashboard-home.png",
        "settings-page.png",
        "report-list.png",
        "export-success.png",
    ):
        _write_png(screens / name)
    (screens / "screens-description.md").write_text(
        "# 关键页面说明\n\n登录、首页、设置、列表和导出成功状态均已覆盖。",
        encoding="utf-8",
    )
    ocr_lines = {
        "login-screen.png": ("login screen",),
        "dashboard-home.png": ("dashboard home",),
        "settings-page.png": ("settings page",),
        "report-list.png": ("report list",),
        "export-success.png": ("export success",),
    }
    return _plan_and_analyze(
        screens=screens,
        output_dir=output_dir,
        modules=["login", "dashboard", "settings", "report", "export"],
        key_features=["login", "dashboard", "settings", "report", "export"],
        task_checklist_lite="- login\n- dashboard\n- settings\n- report\n- export",
        journey_stages=["login", "dashboard", "settings", "report", "export"],
        ocr_available=True,
        ocr_lines_by_file=ocr_lines,
        run_id="golden-final-mainline",
    )


def _case_high_quality_no_description(case_root: Path) -> Any:
    screens = case_root / "screens"
    output_dir = case_root / "outputs"
    for name in ("HQ9001.png", "HQ9002.png", "HQ9003.png", "HQ9004.png", "HQ9005.png"):
        _write_png(screens / name)
    return _plan_and_analyze(
        screens=screens,
        output_dir=output_dir,
        modules=["登录", "工作台首页", "设置页", "报表列表", "通知中心"],
        key_features=["登录", "查看工作台", "保存设置", "查看报表", "通知中心"],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        journey_stages=["登录", "工作台首页", "设置页", "报表列表", "通知中心"],
        ocr_available=False,
        run_id="golden-hq-no-description",
    )


def _case_salvageable(case_root: Path) -> Any:
    screens = case_root / "screens"
    output_dir = case_root / "outputs"
    for name in ("shot-01.png", "shot-02.png", "shot-03.png", "shot-04.png", "shot-05.png"):
        _write_png(screens / name)
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## 登录页",
                "主按钮为登录，成功态进入首页。",
                "",
                "## 工作台首页",
                "顶部有首页导航。",
                "",
                "## 设置页",
                "保存后会提示保存成功。",
                "",
                "## 报表列表",
                "页面提示暂无数据。",
                "",
                "## 通知中心",
                "页面标题为消息中心。",
            ]
        ),
        encoding="utf-8",
    )
    ocr_lines = {
        "shot-01.png": ("登录",),
        "shot-02.png": ("首页",),
        "shot-03.png": ("保存成功",),
        "shot-04.png": ("暂无数据",),
        "shot-05.png": ("消息中心",),
    }
    return _plan_and_analyze(
        screens=screens,
        output_dir=output_dir,
        modules=["登录", "工作台首页", "设置页", "报表列表", "通知中心"],
        key_features=["登录", "查看工作台", "保存设置", "查看报表", "通知中心"],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        journey_stages=["登录", "工作台首页", "设置页", "报表列表", "通知中心"],
        ocr_available=True,
        ocr_lines_by_file=ocr_lines,
        run_id="golden-salvageable",
    )


def _case_missing_evidence(case_root: Path) -> Any:
    screens = case_root / "screens"
    output_dir = case_root / "outputs"
    for name in ("screen-01.png", "screen-02.png"):
        _write_png(screens / name)
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## screen-01.png",
                "这是登录页，主按钮为登录。",
                "",
                "## screen-02.png",
                "这是工作台首页，顶部有首页导航，错误态会提示重试。",
            ]
        ),
        encoding="utf-8",
    )
    return _plan_and_analyze(
        screens=screens,
        output_dir=output_dir,
        modules=["登录", "工作台首页"],
        key_features=["登录", "查看工作台"],
        task_checklist_lite="- 登录\n- 工作台首页",
        journey_stages=["登录", "工作台首页"],
        ocr_available=False,
        run_id="golden-missing-evidence",
    )


def _case_complex_multi_module(case_root: Path) -> Any:
    screens = case_root / "screens"
    output_dir = case_root / "outputs"
    screenshot_names = (
        "CX1001.png",
        "CX1002.png",
        "CX1003.png",
        "CX1004.png",
        "CX1005.png",
        "CX1006.png",
        "CX1007.png",
        "CX1008.png",
        "CX1009.png",
        "CX1010.png",
    )
    for name in screenshot_names:
        _write_png(screens / name)
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## CX1001.png",
                "这是登录页加载态。",
                "",
                "## CX1002.png",
                "这是登录页成功态。",
                "",
                "## CX1003.png",
                "这是工作台首页加载态。",
                "",
                "## CX1004.png",
                "这是工作台首页空状态。",
                "",
                "## CX1005.png",
                "这是设置页加载态。",
                "",
                "## CX1006.png",
                "这是设置页保存成功态。",
                "",
                "## CX1007.png",
                "这是报表列表加载态。",
                "",
                "## CX1008.png",
                "这是报表列表空状态。",
                "",
                "## CX1009.png",
                "这是通知中心默认态。",
                "",
                "## CX1010.png",
                "这是通知中心成功反馈态。",
            ]
        ),
        encoding="utf-8",
    )
    ocr_lines = {
        "CX1001.png": ("登录", "加载中"),
        "CX1002.png": ("登录", "登录成功"),
        "CX1003.png": ("工作台首页", "加载中"),
        "CX1004.png": ("工作台首页", "暂无数据"),
        "CX1005.png": ("设置页", "加载中"),
        "CX1006.png": ("设置页", "保存成功"),
        "CX1007.png": ("报表列表", "加载中"),
        "CX1008.png": ("报表列表", "暂无数据"),
        "CX1009.png": ("通知中心", "消息中心"),
        "CX1010.png": ("通知中心", "提交成功"),
    }
    return _plan_and_analyze(
        screens=screens,
        output_dir=output_dir,
        modules=["登录", "工作台首页", "设置页", "报表列表", "通知中心"],
        key_features=["登录", "查看工作台", "保存设置", "查看报表", "通知中心"],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        journey_stages=["登录", "工作台首页", "设置页", "报表列表", "通知中心"],
        ocr_available=True,
        ocr_lines_by_file=ocr_lines,
        run_id="golden-complex-multimodule",
    )


_GOLDEN_CASES = (
    GoldenCase(
        case_id="case-final-mainline",
        label="高质量输入、主链路覆盖充分",
        scenario_class="final_capable",
        expectation="final_capable",
        description="高质量截图 + OCR/说明充分，主链路和关键状态已覆盖。",
        runner=_case_high_quality_mainline,
    ),
    GoldenCase(
        case_id="case-hq-no-description",
        label="高质量截图、但说明不足",
        scenario_class="insufficient_description",
        expectation="bounded_expected",
        description="截图质量高，但没有 OCR 和说明文件支撑，系统应诚实阻断。",
        runner=_case_high_quality_no_description,
    ),
    GoldenCase(
        case_id="case-salvageable",
        label="输入可挽救的 salvageable case",
        scenario_class="salvageable",
        expectation="final_capable",
        description="已有输入基本够，但需要更强 ingestion/remediation 才能抬到 final。",
        runner=_case_salvageable,
    ),
    GoldenCase(
        case_id="case-missing-evidence",
        label="真缺关键证据",
        scenario_class="missing_evidence",
        expectation="bounded_expected",
        description="关键页面数量客观不足，应 bounded 输出并精确归因为 missing_evidence。",
        runner=_case_missing_evidence,
    ),
    GoldenCase(
        case_id="case-complex-multi-module",
        label="复杂多模块、多状态场景",
        scenario_class="complex_multi_module",
        expectation="final_capable",
        description="多模块、多状态、强 OCR + markdown 互证的高复杂度 final 场景。",
        runner=_case_complex_multi_module,
    ),
)


def _case_meets_v1_5(case: GoldenCase, record: dict[str, Any]) -> tuple[bool, str]:
    if case.expectation == "final_capable":
        metrics_ok = (
            record["delivery_status"] == "final_delivery_ready"
            and record["critical_path_page_hit_rate"] >= 0.9
            and record["critical_path_state_hit_rate"] >= 0.9
            and record["trusted_mapping_rate"] >= 0.9
            and record["clarification_item_count"] == 0
        )
        if metrics_ok:
            return True, "final-capable case reached final_delivery_ready with 90%+ critical-path and trusted coverage"
        return False, "final-capable case still cannot cross the final gate under current runtime quality"
    bounded_ok = (
        record["delivery_status"] in {"fallback_safe", "supplement_required", "blocked"}
        and record["root_cause"] == "input_truly_insufficient"
        and record["supplement_request_precision"] >= 0.85
        and record["clarification_item_count"] <= 1
    )
    if bounded_ok:
        return True, "insufficient-input case is bounded truthfully without inflating low-value manual burden"
    return False, "insufficient-input case is not yet being bounded and explained precisely enough"


def _build_case_record(case: GoldenCase, result: Any) -> dict[str, Any]:
    metrics = result.evidence_assessment.client_mode_metrics
    benchmark = result.evidence_assessment.benchmark_summary
    if metrics is None or benchmark is None:
        raise ValueError(f"{case.case_id} did not produce runtime benchmark artifacts")
    record = {
        "case_id": case.case_id,
        "case_label": case.label,
        "scenario_class": case.scenario_class,
        "expectation": case.expectation,
        "description": case.description,
        "delivery_status": benchmark.delivery_status,
        "input_quality_class": benchmark.input_quality_class,
        "critical_path_page_hit_rate": metrics.coverage_metrics.critical_path_page_hit_rate,
        "critical_path_state_hit_rate": metrics.coverage_metrics.critical_path_state_hit_rate,
        "p0_page_coverage": metrics.coverage_metrics.p0_page_coverage,
        "p0_state_coverage": metrics.coverage_metrics.p0_state_coverage,
        "p1_page_coverage": metrics.coverage_metrics.p1_page_coverage,
        "p1_state_coverage": metrics.coverage_metrics.p1_state_coverage,
        "trusted_mapping_rate": metrics.trust_metrics.trusted_mapping_rate,
        "provisional_mapping_rate": metrics.trust_metrics.provisional_mapping_rate,
        "conflicting_mapping_rate": metrics.trust_metrics.conflicting_mapping_rate,
        "first_pass_final_rate": metrics.success_metrics.first_pass_final_rate,
        "auto_remediation_lift": metrics.success_metrics.auto_remediation_lift,
        "clarification_item_count": metrics.human_burden_metrics.clarification_item_count,
        "supplement_request_precision": metrics.human_burden_metrics.supplement_request_precision,
        "low_value_work_return_rate": metrics.human_burden_metrics.low_value_work_return_rate,
        "root_cause": benchmark.root_cause,
        "distance_to_90_plus": benchmark.distance_to_90_plus,
        "met_metrics": benchmark.met_metrics,
        "unmet_metrics": benchmark.unmet_metrics,
        "benchmark_json_path": benchmark.artifact_paths.get("benchmark_json_path", ""),
        "benchmark_markdown_path": benchmark.artifact_paths.get("benchmark_markdown_path", ""),
    }
    met, reason = _case_meets_v1_5(case, record)
    record["v1_5_target_met"] = met
    record["v1_5_reason"] = reason
    return record


def _strongest_case(records: list[dict[str, Any]]) -> dict[str, Any]:
    return max(
        records,
        key=lambda item: (
            1 if item["delivery_status"] == "final_delivery_ready" else 0,
            item["critical_path_page_hit_rate"] + item["critical_path_state_hit_rate"] + item["trusted_mapping_rate"],
            -item["clarification_item_count"],
        ),
    )


def _weakest_case(records: list[dict[str, Any]]) -> dict[str, Any]:
    return min(
        records,
        key=lambda item: (
            {"blocked": 0, "supplement_required": 1, "fallback_safe": 2, "final_delivery_ready": 3}.get(
                item["delivery_status"],
                -1,
            ),
            item["critical_path_page_hit_rate"] + item["critical_path_state_hit_rate"] + item["trusted_mapping_rate"],
            -len(item["distance_to_90_plus"]),
        ),
    )


def _largest_remaining_bottleneck(records: list[dict[str, Any]]) -> tuple[str, str]:
    final_capable_failures = [
        record
        for record in records
        if record["expectation"] == "final_capable" and not record["v1_5_target_met"]
    ]
    if not final_capable_failures:
        return (
            "objective_input_insufficiency",
            "当前 final-capable cases 已经过线，剩余主要差距集中在输入客观不足的 bounded cases。",
        )
    counts = {
        "critical_path_page_hit_rate": 0,
        "critical_path_state_hit_rate": 0,
        "trusted_mapping_rate": 0,
        "clarification_residue": 0,
    }
    for record in final_capable_failures:
        for unmet in record["unmet_metrics"]:
            if str(unmet).startswith("critical_path_page_hit_rate"):
                counts["critical_path_page_hit_rate"] += 1
            elif str(unmet).startswith("critical_path_state_hit_rate"):
                counts["critical_path_state_hit_rate"] += 1
            elif str(unmet).startswith("trusted_mapping_rate"):
                counts["trusted_mapping_rate"] += 1
            elif str(unmet).startswith("clarification_item_count") or "clarification" in str(unmet):
                counts["clarification_residue"] += 1
    metric = max(counts, key=lambda key: counts[key])
    return metric, f"{metric} is still the most common unmet constraint across final-capable golden cases."


def _render_sweep_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Golden Benchmark Sweep",
        "",
        f"- contract_version: {summary['contract_version']}",
        f"- run_mode: {summary['run_mode']}",
        f"- generated_at: {summary['generated_at']}",
        f"- v1_5_target_met_rate: {summary['aggregate']['v1_5_target_met_rate']:.3f}",
        f"- final_delivery_ready_case_count: {summary['aggregate']['final_delivery_ready_case_count']}",
        f"- fallback_safe_case_count: {summary['aggregate']['fallback_safe_case_count']}",
        f"- supplement_required_case_count: {summary['aggregate']['supplement_required_case_count']}",
        f"- blocked_case_count: {summary['aggregate']['blocked_case_count']}",
        f"- strongest_case: {summary['aggregate']['strongest_case']['case_id']}",
        f"- weakest_case: {summary['aggregate']['weakest_case']['case_id']}",
        f"- largest_remaining_bottleneck_metric: {summary['aggregate']['largest_remaining_bottleneck_metric']}",
        f"- largest_remaining_bottleneck_reason: {summary['aggregate']['largest_remaining_bottleneck_reason']}",
        "",
        "## Case summary",
    ]
    for case in summary["cases"]:
        lines.extend(
            [
                f"### {case['case_id']} - {case['case_label']}",
                f"- delivery_status: {case['delivery_status']}",
                f"- input_quality_class: {case['input_quality_class']}",
                f"- v1_5_target_met: {case['v1_5_target_met']}",
                f"- root_cause: {case['root_cause']}",
                f"- critical_path_page_hit_rate: {case['critical_path_page_hit_rate']:.3f}",
                f"- critical_path_state_hit_rate: {case['critical_path_state_hit_rate']:.3f}",
                f"- trusted_mapping_rate: {case['trusted_mapping_rate']:.3f}",
                f"- first_pass_final_rate: {case['first_pass_final_rate']:.3f}",
                f"- auto_remediation_lift: {case['auto_remediation_lift']:.3f}",
                f"- clarification_item_count: {case['clarification_item_count']}",
                f"- supplement_request_precision: {case['supplement_request_precision']:.3f}",
                f"- v1_5_reason: {case['v1_5_reason']}",
            ]
        )
        if case["distance_to_90_plus"]:
            lines.append("- distance_to_90_plus:")
            lines.extend([f"  - {item}" for item in case["distance_to_90_plus"]])
        else:
            lines.append("- distance_to_90_plus: []")
        lines.append("")
    lines.extend(
        [
            "## Aggregate conclusion",
            f"- current strongest scenario: {summary['aggregate']['strongest_case']['case_label']}",
            f"- current weakest scenario: {summary['aggregate']['weakest_case']['case_label']}",
            f"- final-capable pass rate: {summary['aggregate']['final_capable_pass_rate']:.3f}",
            f"- bounded-safety pass rate: {summary['aggregate']['bounded_safety_pass_rate']:.3f}",
            f"- freeze recommendation: {summary['aggregate']['freeze_recommendation']}",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def run_golden_benchmark_sweep(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    case_records: list[dict[str, Any]] = []
    for case in _GOLDEN_CASES:
        case_root = output_dir / case.case_id
        result = case.runner(case_root)
        case_records.append(_build_case_record(case, result))

    strongest = _strongest_case(case_records)
    weakest = _weakest_case(case_records)
    bottleneck_metric, bottleneck_reason = _largest_remaining_bottleneck(case_records)
    final_capable = [case for case in case_records if case["expectation"] == "final_capable"]
    bounded_expected = [case for case in case_records if case["expectation"] == "bounded_expected"]
    aggregate = {
        "case_count": len(case_records),
        "v1_5_target_met_count": sum(1 for case in case_records if case["v1_5_target_met"]),
        "v1_5_target_met_rate": round(
            sum(1 for case in case_records if case["v1_5_target_met"]) / max(1, len(case_records)),
            3,
        ),
        "final_delivery_ready_case_count": sum(
            1 for case in case_records if case["delivery_status"] == "final_delivery_ready"
        ),
        "fallback_safe_case_count": sum(
            1 for case in case_records if case["delivery_status"] == "fallback_safe"
        ),
        "supplement_required_case_count": sum(
            1 for case in case_records if case["delivery_status"] == "supplement_required"
        ),
        "blocked_case_count": sum(
            1 for case in case_records if case["delivery_status"] == "blocked"
        ),
        "final_capable_pass_rate": round(
            sum(1 for case in final_capable if case["v1_5_target_met"]) / max(1, len(final_capable)),
            3,
        ),
        "bounded_safety_pass_rate": round(
            sum(1 for case in bounded_expected if case["v1_5_target_met"]) / max(1, len(bounded_expected)),
            3,
        ),
        "input_truly_insufficient_case_ids": [
            case["case_id"] for case in case_records if case["root_cause"] == "input_truly_insufficient"
        ],
        "system_ingestion_gap_case_ids": [
            case["case_id"] for case in case_records if case["root_cause"] == "system_ingestion_gap"
        ],
        "strongest_case": {
            "case_id": strongest["case_id"],
            "case_label": strongest["case_label"],
            "delivery_status": strongest["delivery_status"],
        },
        "weakest_case": {
            "case_id": weakest["case_id"],
            "case_label": weakest["case_label"],
            "delivery_status": weakest["delivery_status"],
        },
        "largest_remaining_bottleneck_metric": bottleneck_metric,
        "largest_remaining_bottleneck_reason": bottleneck_reason,
        "freeze_recommendation": (
            "Recommend Freeze: final-capable golden cases are all above the V1.5 line, and the remaining bounded cases are explained by objectively insufficient input rather than system quality gaps."
            if all(case["v1_5_target_met"] for case in final_capable)
            and all(case["v1_5_target_met"] for case in bounded_expected)
            else "Do one more quality-lift batch before Freeze: at least one final-capable golden case still fails the V1.5 line."
        ),
    }
    summary = {
        "contract_version": _SWEEP_CONTRACT_VERSION,
        "run_mode": "client",
        "generated_at": datetime.now(UTC).isoformat(),
        "cases": case_records,
        "aggregate": aggregate,
    }
    (output_dir / _SWEEP_JSON_FILENAME).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / _SWEEP_MD_FILENAME).write_text(
        _render_sweep_markdown(summary),
        encoding="utf-8",
    )
    return summary
