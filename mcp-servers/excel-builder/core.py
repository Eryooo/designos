"""Core Excel report generation logic for DesignOS.

Pure functions that build Excel workbooks from Issue data structures.
All functions are type-annotated and side-effect-free (except file I/O).
"""

from __future__ import annotations

import html
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet


class ExcelBuilderError(Exception):
    """Base exception for excel-builder errors."""

    pass


# Severity level color mapping
SEVERITY_COLORS = {
    "critical": "FFCCCC",  # Red
    "major": "FFE5CC",  # Orange
    "minor": "FFFFCC",  # Yellow
    "suggestion": "E6E6E6",  # Gray
}

HEADER_FILL = PatternFill(start_color="D6EAF8", end_color="D6EAF8", fill_type="solid")
HEADER_FONT = Font(bold=True)


def _require_worksheet(sheet: object, *, label: str) -> Worksheet:
    """Return a concrete worksheet or raise a typed builder error."""
    if not isinstance(sheet, Worksheet):
        raise ExcelBuilderError(f"{label} is not a writable worksheet")
    return cast(Worksheet, sheet)


def _auto_adjust_column_width(ws: Worksheet, max_width: int = 50) -> None:
    """Auto-adjust column widths based on content length."""
    for column in ws.columns:
        max_length = 0
        column_index = column[0].column
        if isinstance(column_index, str):
            column_letter = column_index
        elif isinstance(column_index, int):
            column_letter = get_column_letter(column_index)
        else:
            continue

        for cell in column:
            if cell.value:
                cell_length = len(str(cell.value))
                if cell_length > max_length:
                    max_length = cell_length

        adjusted_width = min(max_length + 2, max_width)
        ws.column_dimensions[column_letter].width = adjusted_width


def _apply_header_style(ws: Worksheet, row_num: int = 1) -> None:
    """Apply header styling to the specified row."""
    for cell in ws[row_num]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")


def _build_uxeval_template(wb: Workbook, issues: list[dict[str, Any]]) -> None:
    """Build the uxeval template with 3 sheets."""
    # Sheet 1: 问题清单
    ws_issues = _require_worksheet(wb.active, label="uxeval issues sheet")
    ws_issues.title = "问题清单"

    headers = ["ID", "标题", "严重等级", "原则", "描述", "证据", "建议"]
    ws_issues.append(headers)
    _apply_header_style(ws_issues)

    for issue in issues:
        severity = issue.get("severity", "")
        principle_ids = ", ".join(issue.get("principle_ids", []))
        evidence_refs = ", ".join(issue.get("evidence_refs", []))

        row = [
            issue.get("id", ""),
            issue.get("title", ""),
            severity,
            principle_ids,
            issue.get("description", ""),
            evidence_refs,
            issue.get("suggestion", ""),
        ]
        ws_issues.append(row)

        # Apply severity color to the severity column
        row_num = ws_issues.max_row
        severity_cell = ws_issues.cell(row=row_num, column=3)
        if severity in SEVERITY_COLORS:
            severity_cell.fill = PatternFill(
                start_color=SEVERITY_COLORS[severity],
                end_color=SEVERITY_COLORS[severity],
                fill_type="solid",
            )

    _auto_adjust_column_width(ws_issues)

    # Sheet 2: 摘要
    ws_summary = _require_worksheet(wb.create_sheet("摘要"), label="uxeval summary sheet")
    ws_summary.append(["严重等级", "数量"])
    _apply_header_style(ws_summary)

    severity_counts: dict[str, int] = {}
    for issue in issues:
        severity = issue.get("severity", "unknown")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    for severity in ["critical", "major", "minor", "suggestion"]:
        count = severity_counts.get(severity, 0)
        ws_summary.append([severity, count])

    _auto_adjust_column_width(ws_summary)

    # Sheet 3: 原则覆盖
    ws_principles = _require_worksheet(wb.create_sheet("原则覆盖"), label="uxeval principles sheet")
    ws_principles.append(["原则ID", "问题数量"])
    _apply_header_style(ws_principles)

    principle_counts: dict[str, int] = {}
    for issue in issues:
        for principle_id in issue.get("principle_ids", []):
            principle_counts[principle_id] = principle_counts.get(principle_id, 0) + 1

    for principle_id, count in sorted(principle_counts.items()):
        ws_principles.append([principle_id, count])

    _auto_adjust_column_width(ws_principles)


def _build_design_acceptance_template(wb: Workbook, issues: list[dict[str, Any]]) -> None:
    """Build the design-acceptance template with 3 sheets."""
    # Sheet 1: 差异清单
    ws_diff = _require_worksheet(wb.active, label="design acceptance diff sheet")
    ws_diff.title = "差异清单"

    headers = ["ID", "页面", "差异类型", "设计值", "实现值", "偏差量"]
    ws_diff.append(headers)
    _apply_header_style(ws_diff)

    for issue in issues:
        row = [
            issue.get("id", ""),
            issue.get("module_id", ""),
            issue.get("title", ""),
            "",  # 设计值 placeholder
            "",  # 实现值 placeholder
            "",  # 偏差量 placeholder
        ]
        ws_diff.append(row)

    _auto_adjust_column_width(ws_diff)

    # Sheet 2: 页面汇总
    ws_page = _require_worksheet(wb.create_sheet("页面汇总"), label="design acceptance page sheet")
    ws_page.append(["页面", "问题数量"])
    _apply_header_style(ws_page)

    page_counts: dict[str, int] = {}
    for issue in issues:
        page = issue.get("module_id", "unknown")
        page_counts[page] = page_counts.get(page, 0) + 1

    for page, count in sorted(page_counts.items()):
        ws_page.append([page, count])

    _auto_adjust_column_width(ws_page)

    # Sheet 3: 组件汇总
    ws_component = _require_worksheet(
        wb.create_sheet("组件汇总"),
        label="design acceptance component sheet",
    )
    ws_component.append(["组件", "问题数量"])
    _apply_header_style(ws_component)

    # Placeholder: group by task_id as component proxy
    component_counts: dict[str, int] = {}
    for issue in issues:
        component = issue.get("task_id", "unknown")
        component_counts[component] = component_counts.get(component, 0) + 1

    for component, count in sorted(component_counts.items()):
        ws_component.append([component, count])

    _auto_adjust_column_width(ws_component)


def _build_competitor_template(wb: Workbook, issues: list[dict[str, Any]]) -> None:
    """Build the competitor template with 2 sheets."""
    # Sheet 1: 功能对比矩阵
    ws_matrix = _require_worksheet(wb.active, label="competitor matrix sheet")
    ws_matrix.title = "功能对比矩阵"

    headers = ["功能", "产品A", "产品B", "产品C"]
    ws_matrix.append(headers)
    _apply_header_style(ws_matrix)

    # Placeholder: use issue titles as features
    for issue in issues[:10]:  # Limit to 10 for demo
        row = [issue.get("title", ""), "✓", "✗", "✓"]
        ws_matrix.append(row)

    _auto_adjust_column_width(ws_matrix)

    # Sheet 2: 维度评分
    ws_score = _require_worksheet(wb.create_sheet("维度评分"), label="competitor score sheet")
    ws_score.append(["维度", "产品A", "产品B", "产品C"])
    _apply_header_style(ws_score)

    dimensions = ["易用性", "功能完整性", "性能", "视觉设计", "一致性"]
    for dimension in dimensions:
        ws_score.append([dimension, 8, 7, 9])

    _auto_adjust_column_width(ws_score)


def _render_html_report(
    issues: list[dict[str, Any]],
    *,
    target_path: Path,
    journey_map: Any,
    principles: Any,
) -> None:
    """Render a small standalone HTML report for Stage 7."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    issue_items = "\n".join(
        (
            "<li>"
            f"<strong>{html.escape(str(issue.get('id', '')))} {html.escape(str(issue.get('title', '')))}</strong>"
            f" <span>({html.escape(str(issue.get('severity', '')) or 'unknown')})</span><br/>"
            f"<span>{html.escape(str(issue.get('description', '')))}</span>"
            "</li>"
        )
        for issue in issues
    )
    payload = {
        "journey_map": journey_map,
        "principles": principles,
        "issues": issues,
    }
    document = (
        "<!DOCTYPE html>\n"
        "<html lang=\"zh-CN\">\n"
        "<head>\n"
        "<meta charset=\"utf-8\" />\n"
        "<title>UXEval HTML Report</title>\n"
        "<style>"
        "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:2rem;color:#1f2937;}"
        "h1,h2{margin:0 0 1rem;}"
        "section{margin:2rem 0;}"
        "ul{padding-left:1.25rem;}"
        "li{margin-bottom:0.75rem;}"
        "pre{background:#f3f4f6;padding:1rem;border-radius:8px;overflow:auto;}"
        "</style>\n"
        "</head>\n"
        "<body>\n"
        "<h1>UXEval Report</h1>\n"
        f"<p>Total issues: {len(issues)}</p>\n"
        "<section>\n"
        "<h2>Issue list</h2>\n"
        f"<ul>{issue_items}</ul>\n"
        "</section>\n"
        "<section>\n"
        "<h2>Structured payload</h2>\n"
        f"<pre>{html.escape(json.dumps(payload, ensure_ascii=False, indent=2, default=str))}</pre>\n"
        "</section>\n"
        "</body>\n"
        "</html>\n"
    )
    target_path.write_text(document, encoding="utf-8")


def _write_evidence_pack(
    evidence_dir: Path,
    *,
    issues: list[dict[str, Any]],
    journey_map: Any,
    principles: Any,
    excel_path: Path,
    html_path: Path,
    template: str,
) -> int:
    """Write a real evidence directory with a manifest and source payloads."""
    evidence_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "template": template,
        "issue_count": len(issues),
        "issue_report_path": str(excel_path),
        "html_report_path": str(html_path),
    }
    files: dict[str, Any] = {
        "manifest.json": manifest,
        "issues.json": issues,
        "journey_map.json": journey_map,
        "principles.json": principles,
    }
    written = 0
    for filename, payload in files.items():
        (evidence_dir / filename).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        written += 1
    return written


def _artifact_payload(
    *,
    artifact_id: str,
    output_type: str,
    path: Path,
    format: str,
    summary: str,
    **metadata: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": artifact_id,
        "type": output_type,
        "path": str(path.resolve()),
        "format": format,
        "summary": summary,
    }
    payload.update(metadata)
    return payload


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            cleaned = str(item).strip()
            if cleaned:
                items.append(cleaned)
        return items
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []
    return []


def _unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        unique.append(value)
    return unique


def _issue_audit_failures(issue: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if str(issue.get("verification_status", "")).strip() != "verified":
        failures.append("verification_status != verified")
    if not _string_list(issue.get("evidence_refs")):
        failures.append("missing evidence_refs")
    if not _string_list(issue.get("evidence_basis")):
        failures.append("missing evidence_basis")
    return failures


def _is_key_unverified_issue(issue: dict[str, Any]) -> bool:
    severity = str(issue.get("severity", "")).strip().lower()
    if severity in {"critical", "major"}:
        return True
    if issue.get("blocks_final_delivery") is True:
        return True
    return severity == ""


def _render_bounded_issue_pass(
    *,
    safe_main_issues: list[dict[str, Any]],
    demoted_main_issues: list[dict[str, Any]],
    audited_delivery_assessment: dict[str, Any],
) -> str:
    lines = [
        "# Bounded Issue Pass",
        "",
        f"- delivery_status: {audited_delivery_assessment['delivery_status']}",
        f"- qualified_issue_count: {len(safe_main_issues)}",
        f"- demoted_main_issue_count: {len(demoted_main_issues)}",
        "",
        "## 当前可直接使用的可信主结论",
    ]
    if safe_main_issues:
        for issue in safe_main_issues:
            evidence_refs = ", ".join(_string_list(issue.get("evidence_refs")))
            evidence_basis = "；".join(_string_list(issue.get("evidence_basis"))[:3])
            lines.extend(
                [
                    f"### {issue.get('id', '')} {issue.get('title', '')}",
                    f"- severity: {issue.get('severity', '')}",
                    f"- user_impact: {issue.get('user_impact', '')}",
                    f"- evidence_refs: {evidence_refs or '(missing)'}",
                    f"- evidence_basis: {evidence_basis or '(missing)'}",
                    f"- suggestion: {issue.get('suggestion', '')}",
                    "",
                ]
            )
    else:
        lines.extend(
            [
                "- 当前没有足够稳定的主问题结论可直接分享。",
                "",
            ]
        )

    lines.append("## 被 runtime audit 从主清单剔除的问题")
    if demoted_main_issues:
        for issue in demoted_main_issues:
            lines.extend(
                [
                    f"- {issue.get('id', '')} {issue.get('title', '')}: "
                    + "；".join(_string_list(issue.get("audit_failures"))),
                ]
            )
    else:
        lines.append("- 无")

    return "\n".join(lines).strip() + "\n"


def _render_supplement_request(
    *,
    audited_delivery_assessment: dict[str, Any],
    evidence_assessment: dict[str, Any],
    key_unverified_issues: list[dict[str, Any]],
    demoted_main_issues: list[dict[str, Any]],
) -> str:
    coverage_summary = evidence_assessment.get("coverage_summary", {})
    if not isinstance(coverage_summary, dict):
        coverage_summary = {}

    lines = [
        "# Supplement Request",
        "",
        f"- audited_delivery_status: {audited_delivery_assessment['delivery_status']}",
        f"- status_reason: {audited_delivery_assessment.get('status_reason', '')}",
        "",
        "## Required actions",
    ]
    actions = _string_list(audited_delivery_assessment.get("required_actions"))
    if actions:
        lines.extend(f"- {action}" for action in actions)
    else:
        lines.append("- 无额外补料要求。")

    missing_tasks = _string_list(coverage_summary.get("missing_tasks"))
    missing_states = _string_list(coverage_summary.get("missing_state_categories"))
    low_readability = _string_list(coverage_summary.get("low_readability_paths"))
    missing_desc = _string_list(coverage_summary.get("missing_description_paths"))
    missing_ocr = _string_list(coverage_summary.get("missing_ocr_paths"))
    missing_planned_pages = _string_list(coverage_summary.get("missing_critical_pages"))
    missing_planned_states = _string_list(coverage_summary.get("missing_planned_states"))
    missing_required_descriptions = _string_list(coverage_summary.get("missing_required_description_pages"))
    naming_issues = _string_list(coverage_summary.get("naming_issues"))

    lines.extend(
        [
            "",
            "## Missing evidence coverage",
        ]
    )
    coverage_items = [
        ("missing_tasks", missing_tasks),
        ("missing_state_categories", missing_states),
        ("missing_critical_pages", missing_planned_pages),
        ("missing_planned_states", missing_planned_states),
        ("missing_required_description_pages", missing_required_descriptions),
        ("low_readability_paths", low_readability),
        ("missing_description_paths", missing_desc),
        ("missing_ocr_paths", missing_ocr),
        ("naming_issues", naming_issues),
    ]
    any_coverage = False
    for label, values in coverage_items:
        if not values:
            continue
        any_coverage = True
        lines.append(f"- {label}: {'；'.join(values[:6])}")
    if not any_coverage:
        lines.append("- 当前没有额外的结构化 coverage gap。")

    lines.extend(["", "## Still-unverified issues"])
    if key_unverified_issues or demoted_main_issues:
        for issue in [*key_unverified_issues, *demoted_main_issues]:
            issue_id = issue.get("id", "")
            title = issue.get("title", "")
            blockers = _string_list(issue.get("blocked_by")) + _string_list(issue.get("audit_failures"))
            lines.append(f"- {issue_id} {title}: {'；'.join(blockers) or '待补充证据'}")
    else:
        lines.append("- 无")

    return "\n".join(lines).strip() + "\n"


def audit_delivery_readiness(
    issues: list[dict[str, Any]],
    unverified_issues: list[dict[str, Any]] | None = None,
    evidence_assessment: dict[str, Any] | None = None,
    delivery_assessment: dict[str, Any] | None = None,
    output_dir: str | None = None,
    run_id: str | None = None,
    skill_name: str | None = None,
    skill_version: str | None = None,
    stage_id: str | None = None,
) -> dict[str, Any]:
    """Deterministically audit final-delivery readiness and write a bounded package."""
    unverified_source = list(unverified_issues or [])
    evidence = dict(evidence_assessment or {})
    llm_delivery = dict(delivery_assessment or {})

    if output_dir is None:
        raise ExcelBuilderError("output_dir is required for delivery audit packaging")
    bundle_dir = Path(output_dir) / "delivery_audit_bundle"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    safe_main_issues: list[dict[str, Any]] = []
    demoted_main_issues: list[dict[str, Any]] = []
    demoted_actions: list[str] = []
    for issue in issues:
        failures = _issue_audit_failures(issue)
        if failures:
            demoted = dict(issue)
            demoted["audit_failures"] = failures
            demoted["demoted_from_main_list"] = True
            demoted_main_issues.append(demoted)
            demoted_actions.append(
                f"修正主清单问题 {issue.get('id', '')} 的审计缺口：{'；'.join(failures)}"
            )
        else:
            safe_main_issues.append(issue)

    merged_unverified = [*unverified_source, *demoted_main_issues]
    key_unverified = [issue for issue in merged_unverified if _is_key_unverified_issue(issue)]

    evidence_delivery_status = str(evidence.get("delivery_status", "blocked")).strip() or "blocked"
    missing_coverage = _string_list(evidence.get("missing_coverage"))
    evidence_required_actions = _string_list(evidence.get("required_actions"))
    evidence_verification_gaps = _string_list(evidence.get("verification_gaps"))
    coverage_summary = evidence.get("coverage_summary", {})
    if not isinstance(coverage_summary, dict):
        coverage_summary = {}

    audit_failures: list[str] = []
    if evidence_delivery_status != "final_delivery_ready":
        audit_failures.append(
            f"evidence_assessment.delivery_status={evidence_delivery_status}, not final_delivery_ready"
        )
    if demoted_main_issues:
        audit_failures.append(
            f"{len(demoted_main_issues)} main-list issue(s) failed deterministic verification"
        )
    if key_unverified:
        audit_failures.append(
            f"{len(key_unverified)} key unverified issue(s) still affect the main conclusion"
        )
    if missing_coverage:
        audit_failures.append("critical evidence coverage gaps remain unresolved")

    final_delivery_ready = bool(safe_main_issues) and not audit_failures
    fallback_safe = False
    audited_status = "final_delivery_ready"
    if not final_delivery_ready:
        if evidence_delivery_status in {"final_delivery_ready", "fallback_safe"} and safe_main_issues:
            audited_status = "fallback_safe"
            fallback_safe = True
        elif evidence_delivery_status == "blocked":
            audited_status = "blocked"
        else:
            audited_status = "supplement_required"

    required_actions = _unique_preserve_order(
        evidence_required_actions + demoted_actions
    )
    if audited_status == "fallback_safe" and not required_actions:
        required_actions.append("补关键页面或关键状态证据后再升级为最终报告")

    verification_gaps = _unique_preserve_order(
        evidence_verification_gaps
        + _string_list(evidence.get("missing_coverage"))
        + [
            f"{issue.get('id', '')} requires verification before entering the final main issue list"
            for issue in demoted_main_issues
        ]
    )

    if final_delivery_ready:
        status_reason = (
            "Runtime delivery audit passed: all main-list issues are verified, evidence-complete, "
            "and no blocking coverage gap remains."
        )
    elif audited_status == "fallback_safe":
        status_reason = (
            "Runtime delivery audit downgraded this run to bounded fallback sharing. "
            "Some verified conclusions are usable, but final report release is blocked."
        )
    elif audited_status == "blocked":
        status_reason = (
            "Runtime delivery audit blocked delivery because evidence is not trustworthy enough "
            "for either final report or bounded sharing."
        )
    else:
        status_reason = (
            "Runtime delivery audit requires supplementary evidence before this run can become "
            "a reliable final delivery."
        )

    audited_delivery_assessment: dict[str, Any] = {
        "delivery_status": audited_status,
        "final_delivery_ready": final_delivery_ready,
        "fallback_safe": fallback_safe,
        "status_reason": status_reason,
        "confidence": "high" if final_delivery_ready else "medium" if fallback_safe else "low",
        "required_actions": required_actions,
        "verification_gaps": verification_gaps,
        "evidence_basis": [
            f"main_issue_count={len(issues)}",
            f"qualified_issue_count={len(safe_main_issues)}",
            f"demoted_main_issue_count={len(demoted_main_issues)}",
            f"unverified_issue_count={len(merged_unverified)}",
            f"evidence_delivery_status={evidence_delivery_status}",
            f"llm_delivery_status={str(llm_delivery.get('delivery_status', 'unknown'))}",
        ],
        "audit_failures": audit_failures,
        "coverage_summary": {
            "missing_tasks": _string_list(coverage_summary.get("missing_tasks")),
            "missing_state_categories": _string_list(coverage_summary.get("missing_state_categories")),
            "missing_critical_pages": _string_list(coverage_summary.get("missing_critical_pages")),
            "missing_planned_states": _string_list(coverage_summary.get("missing_planned_states")),
            "missing_required_description_pages": _string_list(coverage_summary.get("missing_required_description_pages")),
            "naming_issues": _string_list(coverage_summary.get("naming_issues")),
            "low_readability_paths": _string_list(coverage_summary.get("low_readability_paths")),
            "missing_description_paths": _string_list(coverage_summary.get("missing_description_paths")),
            "missing_ocr_paths": _string_list(coverage_summary.get("missing_ocr_paths")),
        },
        "run_id": run_id,
        "skill_name": skill_name,
        "skill_version": skill_version,
        "stage_id": stage_id,
    }

    bounded_issue_pass_path = bundle_dir / "bounded_issue_pass.md"
    bounded_issue_pass_path.write_text(
        _render_bounded_issue_pass(
            safe_main_issues=safe_main_issues,
            demoted_main_issues=demoted_main_issues,
            audited_delivery_assessment=audited_delivery_assessment,
        ),
        encoding="utf-8",
    )

    unverified_path = bundle_dir / "unverified_issues.json"
    unverified_path.write_text(
        json.dumps(merged_unverified, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    supplement_request_path = bundle_dir / "supplement_request.md"
    supplement_request_path.write_text(
        _render_supplement_request(
            audited_delivery_assessment=audited_delivery_assessment,
            evidence_assessment=evidence,
            key_unverified_issues=key_unverified,
            demoted_main_issues=demoted_main_issues,
        ),
        encoding="utf-8",
    )

    audited_assessment_path = bundle_dir / "audited_delivery_assessment.json"
    audited_assessment_path.write_text(
        json.dumps(audited_delivery_assessment, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    audit_manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "delivery_status": audited_status,
        "qualified_issue_count": len(safe_main_issues),
        "demoted_main_issue_count": len(demoted_main_issues),
        "unverified_issue_count": len(merged_unverified),
        "files": [
            "bounded_issue_pass.md",
            "unverified_issues.json",
            "supplement_request.md",
            "audited_delivery_assessment.json",
        ],
    }
    (bundle_dir / "manifest.json").write_text(
        json.dumps(audit_manifest, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    return {
        "audited_delivery_assessment": audited_delivery_assessment,
        "delivery_audit_bundle": _artifact_payload(
            artifact_id="delivery_audit_bundle",
            output_type="delivery_audit_bundle",
            path=bundle_dir,
            format="directory",
            summary=(
                "Runtime-audited bounded fallback package."
                if audited_status != "final_delivery_ready"
                else "Runtime delivery audit bundle for a final-ready run."
            ),
            file_count=5,
            delivery_status=audited_status,
            qualified_issue_count=len(safe_main_issues),
            demoted_main_issue_count=len(demoted_main_issues),
        ),
    }


def build_issue_report(
    issues: list[dict[str, Any]],
    output_path: str | None = None,
    template: str = "uxeval",
    journey_map: Any = None,
    principles: Any = None,
    output_dir: str | None = None,
    run_id: str | None = None,
    skill_name: str | None = None,
    skill_version: str | None = None,
    stage_id: str | None = None,
) -> dict[str, Any]:
    """Build an Excel report from a list of issues.

    Args:
        issues: List of Issue objects serialized as dicts.
        output_path: Absolute path where the Excel file should be written.
            If None, generates a timestamped path in /tmp.
        template: Report template name ('uxeval', 'design-acceptance', 'competitor').
        journey_map: Journey map context included in html/evidence outputs.
        principles: Principles list included in html/evidence outputs.
        output_dir: Optional output directory used to derive stable artifact paths.

    Returns:
        Dict with ``issue_report`` / ``html_report`` / ``evidence_pack`` payloads.

    Raises:
        ExcelBuilderError: If template is unknown, path is invalid, or issues is empty.
    """
    # Validate template
    if template not in ["uxeval", "design-acceptance", "competitor"]:
        raise ExcelBuilderError(f"Unknown template: {template}")

    # Generate default output path if not provided
    if output_path is None:
        if output_dir is not None:
            output_path = str(Path(output_dir) / "issue_report.xlsx")
        else:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            output_path = f"/tmp/issue_report_{timestamp}.xlsx"

    # Validate output path
    output_file = Path(output_path)
    if not output_file.parent.exists():
        raise ExcelBuilderError(f"Output directory does not exist: {output_file.parent}")

    # Allow empty issues for some templates
    if not issues and template != "competitor":
        raise ExcelBuilderError("Issues list cannot be empty for this template")

    # Create workbook
    wb = Workbook()

    # Build template-specific sheets
    if template == "uxeval":
        _build_uxeval_template(wb, issues)
    elif template == "design-acceptance":
        _build_design_acceptance_template(wb, issues)
    elif template == "competitor":
        _build_competitor_template(wb, issues)

    # Save workbook
    wb.save(output_path)

    html_path = output_file.with_suffix(".html")
    _render_html_report(
        issues,
        target_path=html_path,
        journey_map=journey_map,
        principles=principles,
    )

    evidence_dir = output_file.parent / "evidence_pack"
    evidence_file_count = _write_evidence_pack(
        evidence_dir,
        issues=issues,
        journey_map=journey_map,
        principles=principles,
        excel_path=output_file,
        html_path=html_path,
        template=template,
    )

    return {
        "issue_report": _artifact_payload(
            artifact_id="issue_report",
            output_type="issue_report",
            path=output_file,
            format="xlsx",
            summary=f"{template} issue workbook with {len(issues)} issues.",
            sheet_count=len(wb.sheetnames),
            issue_count=len(issues),
        ),
        "html_report": _artifact_payload(
            artifact_id="html_report",
            output_type="html_report",
            path=html_path,
            format="html",
            summary=f"{template} HTML report with {len(issues)} issues.",
            issue_count=len(issues),
        ),
        "evidence_pack": _artifact_payload(
            artifact_id="evidence_pack",
            output_type="evidence_pack",
            path=evidence_dir,
            format="directory",
            summary="Evidence pack with manifest and structured source payloads.",
            file_count=evidence_file_count,
        ),
    }


__all__ = ["audit_delivery_readiness", "build_issue_report", "ExcelBuilderError"]
