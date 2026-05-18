"""Tests for core Excel generation logic."""

import pytest
from pathlib import Path
from openpyxl import load_workbook

from core import build_issue_report, ExcelBuilderError


def test_build_uxeval_report(temp_output_dir, mock_issues):
    """Test building a uxeval template report."""
    output_path = temp_output_dir / "uxeval_report.xlsx"

    result = build_issue_report(
        issues=mock_issues,
        output_path=str(output_path),
        template="uxeval",
    )

    assert result["sheet_count"] == 3
    assert Path(result["path"]).exists()

    # Verify workbook can be loaded
    wb = load_workbook(output_path)
    assert len(wb.sheetnames) == 3
    assert "问题清单" in wb.sheetnames
    assert "摘要" in wb.sheetnames
    assert "原则覆盖" in wb.sheetnames

    # Verify 问题清单 sheet content
    ws_issues = wb["问题清单"]
    assert ws_issues.cell(1, 1).value == "ID"
    assert ws_issues.cell(2, 1).value == "I-001"
    assert ws_issues.cell(2, 2).value == "登录按钮位置不明显"
    assert ws_issues.cell(2, 3).value == "critical"

    # Verify 摘要 sheet content
    ws_summary = wb["摘要"]
    assert ws_summary.cell(1, 1).value == "严重等级"
    assert ws_summary.cell(2, 1).value == "critical"
    assert ws_summary.cell(2, 2).value == 1  # 1 critical issue

    wb.close()


def test_build_design_acceptance_report(temp_output_dir, mock_issues):
    """Test building a design-acceptance template report."""
    output_path = temp_output_dir / "design_acceptance_report.xlsx"

    result = build_issue_report(
        issues=mock_issues,
        output_path=str(output_path),
        template="design-acceptance",
    )

    assert result["sheet_count"] == 3
    assert Path(result["path"]).exists()

    # Verify workbook can be loaded
    wb = load_workbook(output_path)
    assert len(wb.sheetnames) == 3
    assert "差异清单" in wb.sheetnames
    assert "页面汇总" in wb.sheetnames
    assert "组件汇总" in wb.sheetnames

    wb.close()


def test_build_competitor_report(temp_output_dir, mock_issues):
    """Test building a competitor template report."""
    output_path = temp_output_dir / "competitor_report.xlsx"

    result = build_issue_report(
        issues=mock_issues,
        output_path=str(output_path),
        template="competitor",
    )

    assert result["sheet_count"] == 2
    assert Path(result["path"]).exists()

    # Verify workbook can be loaded
    wb = load_workbook(output_path)
    assert len(wb.sheetnames) == 2
    assert "功能对比矩阵" in wb.sheetnames
    assert "维度评分" in wb.sheetnames

    wb.close()


def test_unknown_template_raises_error(temp_output_dir, mock_issues):
    """Test that unknown template raises ExcelBuilderError."""
    output_path = temp_output_dir / "report.xlsx"

    with pytest.raises(ExcelBuilderError, match="Unknown template"):
        build_issue_report(
            issues=mock_issues,
            output_path=str(output_path),
            template="unknown-template",
        )


def test_invalid_output_path_raises_error(mock_issues):
    """Test that invalid output path raises ExcelBuilderError."""
    output_path = "/nonexistent/directory/report.xlsx"

    with pytest.raises(ExcelBuilderError, match="Output directory does not exist"):
        build_issue_report(
            issues=mock_issues,
            output_path=output_path,
            template="uxeval",
        )


def test_empty_issues_for_uxeval_raises_error(temp_output_dir):
    """Test that empty issues list raises error for uxeval template."""
    output_path = temp_output_dir / "report.xlsx"

    with pytest.raises(ExcelBuilderError, match="Issues list cannot be empty"):
        build_issue_report(
            issues=[],
            output_path=str(output_path),
            template="uxeval",
        )


def test_file_overwrite(temp_output_dir, mock_issues):
    """Test that existing file is overwritten."""
    output_path = temp_output_dir / "report.xlsx"

    # Create first report
    result1 = build_issue_report(
        issues=mock_issues,
        output_path=str(output_path),
        template="uxeval",
    )
    assert Path(result1["path"]).exists()

    # Overwrite with second report
    result2 = build_issue_report(
        issues=mock_issues[:2],  # Fewer issues
        output_path=str(output_path),
        template="uxeval",
    )
    assert Path(result2["path"]).exists()

    # Verify the file was overwritten
    wb = load_workbook(output_path)
    ws = wb["问题清单"]
    # Should have 2 issues + 1 header = 3 rows
    assert ws.max_row == 3

    wb.close()


def test_severity_color_coding(temp_output_dir, mock_issues):
    """Test that severity levels have correct color coding."""
    output_path = temp_output_dir / "report.xlsx"

    build_issue_report(
        issues=mock_issues,
        output_path=str(output_path),
        template="uxeval",
    )

    wb = load_workbook(output_path)
    ws = wb["问题清单"]

    # Check critical issue (row 2)
    critical_cell = ws.cell(2, 3)
    assert critical_cell.fill.start_color.rgb == "FFCCCC"

    # Check major issue (row 3)
    major_cell = ws.cell(3, 3)
    assert major_cell.fill.start_color.rgb == "FFE5CC"

    # Check minor issue (row 4)
    minor_cell = ws.cell(4, 3)
    assert minor_cell.fill.start_color.rgb == "FFFFCC"

    # Check suggestion (row 5)
    suggestion_cell = ws.cell(5, 3)
    assert suggestion_cell.fill.start_color.rgb == "E6E6E6"

    wb.close()


def test_principle_aggregation(temp_output_dir, mock_issues):
    """Test that principles are correctly aggregated."""
    output_path = temp_output_dir / "report.xlsx"

    build_issue_report(
        issues=mock_issues,
        output_path=str(output_path),
        template="uxeval",
    )

    wb = load_workbook(output_path)
    ws = wb["原则覆盖"]

    # H1 appears in 3 issues (I-001, I-003, I-005)
    # Find H1 row
    h1_count = None
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] == "H1":
            h1_count = row[1]
            break

    assert h1_count == 3

    wb.close()


__all__ = []
