"""Test fixtures generator for PDF parsing tests."""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def generate_sample_prd(output_path: Path) -> None:
    """Generate a sample PRD PDF with sections.

    Args:
        output_path: Path where the PDF will be saved
    """
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom heading style
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading1"],
        fontSize=14,
        spaceAfter=12,
    )

    story = []

    # Title
    story.append(Paragraph("产品需求文档 (PRD)", styles["Title"]))
    story.append(Spacer(1, 0.3 * inch))

    # Section 1
    story.append(Paragraph("1. 产品概述", heading_style))
    story.append(Paragraph(
        "本产品旨在提供一个高效的文档管理系统，支持多种文件格式的解析和处理。",
        styles["Normal"]
    ))
    story.append(Spacer(1, 0.2 * inch))

    # Section 2
    story.append(Paragraph("2. 核心功能", heading_style))
    story.append(Paragraph(
        "系统需要支持 PDF、Word、Excel 等常见文档格式的解析。",
        styles["Normal"]
    ))
    story.append(Spacer(1, 0.2 * inch))

    # Section 2.1
    story.append(Paragraph("2.1. PDF 解析", heading_style))
    story.append(Paragraph(
        "PDF 解析模块需要提取文档的章节结构、元数据和完整文本内容。",
        styles["Normal"]
    ))
    story.append(Spacer(1, 0.2 * inch))

    # Section 3
    story.append(Paragraph("第三章 技术架构", heading_style))
    story.append(Paragraph(
        "系统采用微服务架构，各模块通过 MCP 协议进行通信。",
        styles["Normal"]
    ))

    doc.build(story)


def generate_empty_pdf(output_path: Path) -> None:
    """Generate an empty PDF (no text content).

    Args:
        output_path: Path where the PDF will be saved
    """
    c = canvas.Canvas(str(output_path), pagesize=letter)
    c.showPage()
    c.save()


def generate_scanned_pdf(output_path: Path) -> None:
    """Generate a PDF simulating a scanned document (no text layer).

    Args:
        output_path: Path where the PDF will be saved
    """
    # For testing purposes, an empty PDF simulates a scanned document
    # (no extractable text layer)
    generate_empty_pdf(output_path)


def main() -> None:
    """Generate all test fixture PDFs."""
    fixtures_dir = Path(__file__).parent
    fixtures_dir.mkdir(exist_ok=True)

    generate_sample_prd(fixtures_dir / "sample-prd.pdf")
    generate_empty_pdf(fixtures_dir / "empty.pdf")
    generate_scanned_pdf(fixtures_dir / "scanned.pdf")

    print(f"Generated test fixtures in {fixtures_dir}")


if __name__ == "__main__":
    main()
