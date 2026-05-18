"""Core Excel report generation logic for DesignOS.

Pure functions that build Excel workbooks from Issue data structures.
All functions are type-annotated and side-effect-free (except file I/O).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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


def _auto_adjust_column_width(ws: Worksheet, max_width: int = 50) -> None:
    """Auto-adjust column widths based on content length."""
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)

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
    ws_issues = wb.active
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
    ws_summary = wb.create_sheet("摘要")
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
    ws_principles = wb.create_sheet("原则覆盖")
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
    ws_diff = wb.active
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
    ws_page = wb.create_sheet("页面汇总")
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
    ws_component = wb.create_sheet("组件汇总")
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
    ws_matrix = wb.active
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
    ws_score = wb.create_sheet("维度评分")
    ws_score.append(["维度", "产品A", "产品B", "产品C"])
    _apply_header_style(ws_score)

    dimensions = ["易用性", "功能完整性", "性能", "视觉设计", "一致性"]
    for dimension in dimensions:
        ws_score.append([dimension, 8, 7, 9])

    _auto_adjust_column_width(ws_score)


def build_issue_report(
    issues: list[dict[str, Any]],
    output_path: str | None = None,
    template: str = "uxeval",
    journey_map: Any = None,  # noqa: ARG001 — reserved for M2
    principles: Any = None,  # noqa: ARG001 — reserved for M2
) -> dict[str, Any]:
    """Build an Excel report from a list of issues.

    Args:
        issues: List of Issue objects serialized as dicts.
        output_path: Absolute path where the Excel file should be written.
            If None, generates a timestamped path in /tmp.
        template: Report template name ('uxeval', 'design-acceptance', 'competitor').
        journey_map: Journey map context (reserved for M2).
        principles: Principles list (reserved for M2).

    Returns:
        Dict with 'path' (str) and 'sheet_count' (int).

    Raises:
        ExcelBuilderError: If template is unknown, path is invalid, or issues is empty.
    """
    # Validate template
    if template not in ["uxeval", "design-acceptance", "competitor"]:
        raise ExcelBuilderError(f"Unknown template: {template}")

    # Generate default output path if not provided
    if output_path is None:
        import datetime
        timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
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

    return {
        "path": str(output_file.absolute()),
        "sheet_count": len(wb.sheetnames),
    }


__all__ = ["build_issue_report", "ExcelBuilderError"]
