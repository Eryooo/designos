"""Unit tests for image-analyzer core logic."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))

import benchmark_harness
import core
from ocr_runtime import OCRLine, OCRProbeResult, OCRResult
from schemas import DraftScreenshotMapping, EvidenceAssessment, ImageAnalysisSummary, LoadAnalyzeResult, ScreenshotRef


def _write_png(path: Path, *, size: tuple[int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, "white").save(path)


def _write_screen_bundle(
    screens: Path,
    entries: list[tuple[str, str, str, str | None]],
) -> None:
    sections: list[str] = ["# 关键页面说明", ""]
    for filename, page_name, state_name, description in entries:
        _write_png(screens / filename, size=(1440, 900))
        sections.extend(
            [
                f"## {filename}",
                description or f"这是{page_name}{state_name}。",
                "",
            ]
        )
    (screens / "screens-description.md").write_text(
        "\n".join(sections),
        encoding="utf-8",
    )


def _patch_ocr_by_filename(
    monkeypatch: pytest.MonkeyPatch,
    *,
    lines_by_file: dict[str, tuple[str, ...]],
) -> None:
    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=True, backend="tesseract"),
    )
    monkeypatch.setattr(
        core,
        "run_ocr",
        lambda path, preferred_backend=None: OCRResult(
            backend="tesseract",
            lines=tuple(
                OCRLine(text=text, confidence=0.93)
                for text in lines_by_file[path.name]
            ),
            raw_text="\n".join(lines_by_file[path.name]),
        ),
    )


def test_recursive_inventory_discovers_nested_assets(
    fixtures_path: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Nested screenshot and markdown files should be discovered recursively."""
    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )
    target = tmp_path / "screens"
    nested = target / "nested" / "state"
    nested.mkdir(parents=True)
    shutil.copy(fixtures_path / "screen-01.png", target / "screen-01.png")
    shutil.copy(fixtures_path / "screen-02.png", nested / "screen-02.png")
    shutil.copy(fixtures_path / "screens-description.md", nested / "screens-description.md")

    result = core.load_and_analyze(target)

    assert isinstance(result, LoadAnalyzeResult)
    assert [ref.relative_path for ref in result.screenshots] == [
        "nested/state/screen-02.png",
        "nested/state/screens-description.md",
        "screen-01.png",
    ]
    assert [ref.id for ref in result.screenshots] == ["S-001", "S-002", "S-003"]


def test_image_analyzer_returns_structured_text_evidence_when_ocr_available(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    _write_png(screens / "login-screen.png", size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "# 登录页说明\n\n登录页包含「登录」按钮和错误状态说明。",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=True, backend="tesseract"),
    )
    monkeypatch.setattr(
        core,
        "run_ocr",
        lambda path, preferred_backend=None: OCRResult(
            backend="tesseract",
            lines=(
                OCRLine(text="登录", confidence=0.93),
                OCRLine(text="提交", confidence=0.91),
                OCRLine(text="加载失败", confidence=0.88),
            ),
            raw_text="登录\n提交\n加载失败",
        ),
    )

    result = core.load_and_analyze(screens)

    assert isinstance(result.image_analysis, ImageAnalysisSummary)
    assert isinstance(result.evidence_assessment, EvidenceAssessment)
    assert result.image_analysis.analyzer_kind == "text_evidence_inventory"
    assert result.image_analysis.ocr_available is True
    assert result.image_analysis.ocr_backend == "tesseract"
    assert result.evidence_assessment.verdict == "sufficient"
    assert result.evidence_assessment.delivery_status == "fallback_safe"
    assert result.evidence_assessment.final_delivery_ready is False
    assert result.evidence_assessment.fallback_safe is True

    image_refs = [ref for ref in result.screenshots if ref.kind == "image"]
    assert len(image_refs) == 1
    ref = image_refs[0]
    assert isinstance(ref, ScreenshotRef)
    assert ref.readability.level == "high"
    assert ref.ocr_text_preview == "登录\n提交\n加载失败"
    assert any(cue.value == "登录" and cue.source_channel == "ocr" for cue in ref.page_title_candidates)
    assert any(cue.value == "提交" and cue.source_channel == "ocr" for cue in ref.button_text_candidates)
    assert any(
        cue.value == "加载失败" and cue.source_channel == "ocr"
        for cue in ref.state_text_candidates
    )
    assert ref.description_links
    assert ref.description_links[0].source_channel == "markdown"
    assert ref.description_links[0].confidence in {"medium", "high"}


def test_high_quality_with_description_can_continue_without_ocr(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    _write_png(screens / "dashboard-home.png", size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "# 工作台首页\n\n顶部导航包含首页、设置；主按钮为「新建任务」。",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    result = core.load_and_analyze(screens)

    assert result.image_analysis.ocr_available is False
    assert result.evidence_assessment.verdict == "sufficient"
    assert result.evidence_assessment.delivery_status == "fallback_safe"
    assert result.evidence_assessment.final_delivery_ready is False
    image_ref = next(ref for ref in result.screenshots if ref.kind == "image")
    assert image_ref.description_links
    assert any(cue.source_channel == "markdown" for cue in image_ref.page_title_candidates)
    assert any(cue.source_channel == "markdown" for cue in image_ref.button_text_candidates)
    assert any(cue.source_channel == "markdown" for cue in image_ref.navigation_text_candidates)


def test_low_quality_with_description_requests_supplement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    _write_png(screens / "tiny-screen.png", size=(320, 200))
    (screens / "screens-description.md").write_text(
        "# Tiny Screen\n\n页面是登录态首页，但截图分辨率很低。",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    result = core.load_and_analyze(screens)

    assert result.evidence_assessment.verdict == "supplement_needed"
    assert result.evidence_assessment.delivery_status == "supplement_required"
    assert "补高分辨率截图，建议宽度 >= 1280 像素" in result.evidence_assessment.required_actions
    image_ref = next(ref for ref in result.screenshots if ref.kind == "image")
    assert image_ref.readability.level == "low"


def test_no_ocr_and_no_descriptions_blocks_with_required_actions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    _write_png(screens / "mystery.png", size=(320, 200))

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    result = core.load_and_analyze(screens)

    assert result.image_analysis.ocr_available is False
    assert result.evidence_assessment.verdict == "blocked"
    assert result.evidence_assessment.delivery_status == "blocked"
    assert any("screens-description.md" in action for action in result.evidence_assessment.required_actions)
    assert any("高分辨率截图" in action for action in result.evidence_assessment.required_actions)
    image_ref = next(ref for ref in result.screenshots if ref.kind == "image")
    assert "no linked markdown description for this screenshot" in image_ref.verification_gaps


def test_high_coverage_ocr_bundle_is_final_delivery_ready(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    filenames = [
        "login-screen.png",
        "dashboard-home.png",
        "settings-page.png",
        "report-list.png",
        "export-success.png",
    ]
    for name in filenames:
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "# 关键页面说明\n\n登录、首页、设置、列表和导出成功状态均已覆盖。",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=True, backend="tesseract"),
    )

    def _fake_ocr(path: Path, preferred_backend=None) -> OCRResult:
        stem = path.stem.replace("-", " ")
        return OCRResult(
            backend="tesseract",
            lines=(OCRLine(text=stem, confidence=0.93),),
            raw_text=stem,
        )

    monkeypatch.setattr(core, "run_ocr", _fake_ocr)

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- login\n- dashboard\n- settings\n- report\n- export",
    )

    assert result.evidence_assessment.verdict == "sufficient"
    assert result.evidence_assessment.delivery_status == "final_delivery_ready"
    assert result.evidence_assessment.final_delivery_ready is True
    assert result.evidence_assessment.fallback_safe is False
    assert result.evidence_assessment.missing_coverage == []
    assert result.evidence_assessment.coverage_summary["image_count"] == 5
    assert result.evidence_assessment.coverage_summary["key_task_coverage_ratio"] == 1.0
    breakdown = result.evidence_assessment.delivery_readiness_breakdown
    assert isinstance(breakdown, dict)
    assert breakdown["final_gate_pass"] is True
    assert breakdown["failing_final_gates"] == []
    gates = {gate["gate"]: gate for gate in breakdown["gates"]}
    assert gates["critical_path_coverage"]["final_status"] == "pass"
    assert gates["trusted_evidence_sufficiency"]["final_status"] == "pass"
    assert gates["clarification_residue"]["final_status"] == "pass"
    assert gates["issue_qualification"]["final_status"] == "pending"


def test_high_confidence_mapping_counts_toward_final_delivery_ready(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    for name in (
        "IMG1001.png",
        "IMG1002.png",
        "IMG1003.png",
        "IMG1004.png",
        "IMG1005.png",
        "IMG1006.png",
        "IMG1007.png",
        "IMG1008.png",
        "IMG1009.png",
        "IMG1010.png",
    ):
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## IMG1001.png",
                "这是登录页加载态。",
                "",
                "## IMG1002.png",
                "这是登录页错误态。",
                "",
                "## IMG1003.png",
                "这是登录页成功态。",
                "",
                "## IMG1004.png",
                "这是工作台首页加载态。",
                "",
                "## IMG1005.png",
                "这是工作台首页空状态。",
                "",
                "## IMG1006.png",
                "这是设置页加载态。",
                "",
                "## IMG1007.png",
                "这是设置页成功态。",
                "",
                "## IMG1008.png",
                "这是设置页错误态。",
                "",
                "## IMG1009.png",
                "这是报表列表加载态。",
                "",
                "## IMG1010.png",
                "这是报表列表空状态。",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )
    original_apply = core._apply_draft_mappings

    def _force_high_confidence(refs, *, plan):
        updated_refs, clarification_items = original_apply(refs, plan=plan)
        forced_refs = []
        for ref in updated_refs:
            if ref.kind != "image" or ref.draft_mapping is None:
                forced_refs.append(ref)
                continue
            forced_refs.append(
                ref.model_copy(
                    update={
                        "draft_mapping": ref.draft_mapping.model_copy(
                            update={
                                "confidence": "high",
                                "final_delivery_eligible": True,
                                "final_delivery_reason": "forced high-confidence mapping for final-gate regression",
                            }
                        )
                    }
                )
            )
        return forced_refs, clarification_items

    monkeypatch.setattr(core, "_apply_draft_mappings", _force_high_confidence)

    plan = core.plan_required_evidence(
        modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}, {"name": "报表列表"}],
        key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}, {"name": "查看报表"}],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        journey_stages=["进入登录", "进入工作台", "保存设置", "查看报表"],
        screenshots_dir=screens,
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir,
        run_id="001-high-map-final",
        stage_id="screenshot-loading",
    )

    summary = result.evidence_assessment.coverage_summary
    assert result.evidence_assessment.delivery_status == "final_delivery_ready"
    assert summary["final_delivery_trusted_mapping_count"] == 10
    assert summary["final_delivery_page_coverage_ratio"] == 1.0
    assert summary["final_delivery_state_coverage_ratio"] == 1.0


def test_medium_confidence_mapping_does_not_unlock_final_delivery_ready(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    for name in (
        "IMG1001.png",
        "IMG1002.png",
        "IMG1003.png",
        "IMG1004.png",
        "IMG1005.png",
        "IMG1006.png",
        "IMG1007.png",
        "IMG1008.png",
        "IMG1009.png",
        "IMG1010.png",
    ):
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## IMG1001.png",
                "这是登录页加载态。",
                "",
                "## IMG1002.png",
                "这是登录页错误态。",
                "",
                "## IMG1003.png",
                "这是登录页成功态。",
                "",
                "## IMG1004.png",
                "这是工作台首页加载态。",
                "",
                "## IMG1005.png",
                "这是工作台首页空状态。",
                "",
                "## IMG1006.png",
                "这是设置页加载态。",
                "",
                "## IMG1007.png",
                "这是设置页成功态。",
                "",
                "## IMG1008.png",
                "这是设置页错误态。",
                "",
                "## IMG1009.png",
                "这是报表列表加载态。",
                "",
                "## IMG1010.png",
                "这是报表列表空状态。",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    original_apply = core._apply_draft_mappings

    def _force_medium_only(refs, *, plan):
        updated_refs, clarification_items = original_apply(refs, plan=plan)
        forced_refs = []
        for ref in updated_refs:
            if ref.kind != "image" or ref.draft_mapping is None:
                forced_refs.append(ref)
                continue
            forced_refs.append(
                ref.model_copy(
                    update={
                        "draft_mapping": ref.draft_mapping.model_copy(
                            update={
                                "confidence": "medium",
                                "final_delivery_eligible": False,
                                "final_delivery_reason": "forced provisional mapping for final-gate regression",
                            }
                        )
                    }
                )
            )
        return forced_refs, clarification_items

    monkeypatch.setattr(core, "_apply_draft_mappings", _force_medium_only)

    plan = core.plan_required_evidence(
        modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}, {"name": "报表列表"}],
        key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}, {"name": "查看报表"}],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        journey_stages=["进入登录", "进入工作台", "保存设置", "查看报表"],
        screenshots_dir=screens,
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir,
        run_id="001-medium-map-fallback",
        stage_id="screenshot-loading",
    )

    summary = result.evidence_assessment.coverage_summary
    assert result.evidence_assessment.delivery_status == "fallback_safe"
    assert result.evidence_assessment.final_delivery_ready is False
    assert summary["planned_page_coverage_ratio"] == 1.0
    assert summary["final_delivery_trusted_mapping_count"] == 0
    assert summary["final_delivery_page_coverage_ratio"] == 0.0
    assert summary["final_delivery_missing_critical_pages"]
    assert result.evidence_assessment.clarification_items == []
    breakdown = result.evidence_assessment.delivery_readiness_breakdown
    assert isinstance(breakdown, dict)
    assert breakdown["final_gate_pass"] is False
    assert "trusted_evidence_sufficiency" in breakdown["failing_final_gates"]
    first_pass = result.evidence_assessment.first_pass_success_breakdown
    assert isinstance(first_pass, dict)
    assert "fusion_insufficient" in first_pass["supplement_cause_classification"]
    assert "missing_evidence" not in first_pass["supplement_cause_classification"]
    assert any(
        "provisional mapping" in gap
        for gap in result.evidence_assessment.verification_gaps
    )
    assert result.evidence_assessment.fusion_summary is not None
    assert result.evidence_assessment.fusion_summary.trusted_page_mappings == []
    assert result.evidence_assessment.fusion_summary.provisional_mappings
    targeted_plan = result.evidence_assessment.targeted_acquisition_plan
    assert targeted_plan is not None
    assert "fusion_insufficient" in targeted_plan.supplement_cause_classification
    assert targeted_plan.highest_value_next_captures
    assert targeted_plan.highest_value_next_captures[0].action_class == "clarify_existing_evidence"
    assert targeted_plan.highest_value_next_captures[0].suggested_input_form in {
        "markdown_description",
        "clarification",
    }


def test_evidence_fusion_promotes_trusted_mapping_when_ocr_and_markdown_align(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    screenshot_names = ("IMG5001.png", "IMG5002.png", "IMG5003.png", "IMG5004.png", "IMG5005.png")
    for name in screenshot_names:
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## IMG5001.png",
                "这是登录页加载态，主按钮为登录。",
                "",
                "## IMG5002.png",
                "这是登录页错误态，会提示登录失败。",
                "",
                "## IMG5003.png",
                "这是工作台首页加载态，顶部是首页导航。",
                "",
                "## IMG5004.png",
                "这是设置页成功态，页面提示保存成功。",
                "",
                "## IMG5005.png",
                "这是报表列表空状态，页面提示暂无数据。",
            ]
        ),
        encoding="utf-8",
    )

    plan = core.plan_required_evidence(
        modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}, {"name": "报表列表"}],
        key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}, {"name": "查看报表"}],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        journey_stages=["进入登录", "进入工作台", "保存设置", "查看报表"],
        screenshots_dir=screens,
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )
    without_ocr = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir / "without-ocr",
        run_id="001-fusion-no-ocr",
        stage_id="screenshot-loading",
    )

    ocr_lines_by_file = {
        "IMG5001.png": ("登录", "加载中"),
        "IMG5002.png": ("登录", "登录失败"),
        "IMG5003.png": ("工作台首页", "加载中"),
        "IMG5004.png": ("设置页", "保存成功"),
        "IMG5005.png": ("报表列表", "暂无数据"),
    }
    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=True, backend="tesseract"),
    )
    monkeypatch.setattr(
        core,
        "run_ocr",
        lambda path, preferred_backend=None: OCRResult(
            backend="tesseract",
            lines=tuple(
                OCRLine(text=text, confidence=0.93)
                for text in ocr_lines_by_file[path.name]
            ),
            raw_text="\n".join(ocr_lines_by_file[path.name]),
        ),
    )
    with_ocr = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir / "with-ocr",
        run_id="001-fusion-with-ocr",
        stage_id="screenshot-loading",
    )

    no_ocr_summary = without_ocr.evidence_assessment.fusion_summary
    with_ocr_summary = with_ocr.evidence_assessment.fusion_summary
    assert no_ocr_summary is not None
    assert with_ocr_summary is not None
    assert with_ocr.evidence_assessment.coverage_summary["naming_issues"]
    assert len(with_ocr_summary.trusted_page_mappings) >= len(no_ocr_summary.trusted_page_mappings)
    assert len(with_ocr_summary.trusted_page_mappings) >= 5
    assert sum(mapping.fusion_score for mapping in with_ocr_summary.trusted_page_mappings) > sum(
        mapping.fusion_score for mapping in no_ocr_summary.trusted_page_mappings
    )
    assert all("ocr" in mapping.supporting_channels for mapping in with_ocr_summary.trusted_page_mappings)
    assert all("markdown" in mapping.supporting_channels for mapping in with_ocr_summary.trusted_page_mappings)
    assert with_ocr.evidence_assessment.coverage_summary["final_delivery_trusted_mapping_count"] == len(
        with_ocr_summary.trusted_page_mappings
    )


def test_evidence_fusion_does_not_trust_multi_source_conflict(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    _write_png(screens / "IMG6001.png", size=(1440, 900))
    (screens / "IMG6001.md").write_text(
        "\n".join(
            [
                "报表列表页面",
                "",
                "当前看到列表区域和分页。",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=True, backend="tesseract"),
    )
    monkeypatch.setattr(
        core,
        "run_ocr",
        lambda path, preferred_backend=None: OCRResult(
            backend="tesseract",
            lines=(
                OCRLine(text="设置页", confidence=0.95),
                OCRLine(text="保存", confidence=0.91),
            ),
            raw_text="设置页\n保存",
        ),
    )

    plan = core.plan_required_evidence(
        modules=[{"name": "设置页"}, {"name": "报表列表"}],
        key_features=[{"name": "浏览页面"}],
        task_checklist_lite="- 设置页\n- 报表列表",
        journey_stages=["查看页面"],
        screenshots_dir=screens,
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 设置页\n- 报表列表",
        required_evidence_plan=plan.required_evidence_plan,
    )

    fusion_summary = result.evidence_assessment.fusion_summary
    assert fusion_summary is not None
    assert fusion_summary.trusted_page_mappings == []
    assert len(fusion_summary.conflicting_evidence_groups) == 1
    assert fusion_summary.conflicting_evidence_groups[0].relative_path == "IMG6001.png"
    assert "设置页" in fusion_summary.conflicting_evidence_groups[0].candidate_pages
    assert "报表列表" in fusion_summary.conflicting_evidence_groups[0].candidate_pages
    assert result.evidence_assessment.coverage_summary["final_delivery_trusted_mapping_count"] == 0
    assert result.evidence_assessment.clarification_items


def test_plan_required_evidence_marks_ready_when_current_inputs_cover_critical_pages(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    for name in (
        "登录-加载.png",
        "登录-错误.png",
        "登录-成功.png",
        "工作台首页-加载.png",
        "工作台首页-空状态.png",
        "设置页-加载.png",
        "设置页-成功.png",
        "设置页-错误.png",
        "报表列表-加载.png",
        "报表列表-空状态.png",
    ):
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "# 登录-加载.png\n\n登录页加载态。\n\n# 登录-错误.png\n\n登录页错误态。\n\n# 登录-成功.png\n\n登录成功后进入首页。\n\n# 工作台首页-加载.png\n\n工作台首页加载态。\n\n# 工作台首页-空状态.png\n\n工作台首页空状态。\n\n# 设置页-加载.png\n\n设置页加载态。\n\n# 设置页-成功.png\n\n设置页保存成功态。\n\n# 设置页-错误.png\n\n设置页错误态。\n\n# 报表列表-加载.png\n\n报表列表加载态。\n\n# 报表列表-空状态.png\n\n报表列表空状态。",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    result = core.plan_required_evidence(
        modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}, {"name": "报表列表"}],
        key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}, {"name": "查看报表"}],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        journey_stages=["进入登录", "进入工作台", "保存设置", "查看报表"],
        screenshots_dir=screens,
    )

    assert result.evidence_input_guidance.pre_run_status == "ready"
    assert result.evidence_input_guidance.current_input_sufficient is True
    assert result.evidence_input_guidance.missing_pages == []
    assert result.required_evidence_plan.critical_page_count >= 4


def test_messy_names_do_not_gate_pre_run_when_markdown_supports_auto_mapping(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    for name in (
        "IMG1001.png",
        "IMG1002.png",
        "IMG1003.png",
        "IMG1004.png",
        "IMG1005.png",
        "IMG1006.png",
        "IMG1007.png",
        "IMG1008.png",
        "IMG1009.png",
        "IMG1010.png",
    ):
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## IMG1001.png",
                "这是登录页加载态。",
                "",
                "## IMG1002.png",
                "这是登录页错误态。",
                "",
                "## IMG1003.png",
                "这是登录页成功态。",
                "",
                "## IMG1004.png",
                "这是工作台首页加载态。",
                "",
                "## IMG1005.png",
                "这是工作台首页空状态。",
                "",
                "## IMG1006.png",
                "这是设置页加载态。",
                "",
                "## IMG1007.png",
                "这是设置页成功态。",
                "",
                "## IMG1008.png",
                "这是设置页错误态。",
                "",
                "## IMG1009.png",
                "这是报表列表加载态。",
                "",
                "## IMG1010.png",
                "这是报表列表空状态。",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    result = core.plan_required_evidence(
        modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}, {"name": "报表列表"}],
        key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}, {"name": "查看报表"}],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        journey_stages=["进入登录", "进入工作台", "保存设置", "查看报表"],
        screenshots_dir=screens,
    )

    assert result.evidence_input_guidance.pre_run_status == "ready"
    assert result.evidence_input_guidance.current_input_sufficient is True
    assert result.evidence_input_guidance.naming_issues
    assert result.evidence_input_guidance.clarification_items == []


def test_p0_critical_path_missing_blocks_final_even_with_high_average_coverage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    entries = [
        ("dashboard-home.png", "工作台首页", "默认态。", None),
        ("settings-page.png", "设置页", "保存成功态。", None),
        ("report-list.png", "报表列表", "空状态。", None),
        ("export-center.png", "导出中心", "成功态。", None),
        ("notice-center.png", "通知中心", "默认态。", None),
    ]
    _write_screen_bundle(screens, entries)
    _patch_ocr_by_filename(
        monkeypatch,
        lines_by_file={
            "dashboard-home.png": ("工作台首页", "加载中"),
            "settings-page.png": ("设置页", "保存成功"),
            "report-list.png": ("报表列表", "暂无数据"),
            "export-center.png": ("导出中心", "导出成功"),
            "notice-center.png": ("通知中心", "消息中心"),
        },
    )

    plan = core.plan_required_evidence(
        modules=[{"name": name} for name in ("登录", "工作台首页", "设置页", "报表列表", "导出中心", "通知中心")],
        key_features=[{"name": name} for name in ("登录", "查看工作台", "保存设置", "查看报表", "导出中心", "通知中心")],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 导出中心\n- 通知中心",
        journey_stages=["登录", "工作台首页", "设置页", "报表列表", "导出中心", "通知中心"],
        screenshots_dir=screens,
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 导出中心\n- 通知中心",
        required_evidence_plan=plan.required_evidence_plan,
    )

    summary = result.evidence_assessment.coverage_summary
    critical = result.evidence_assessment.critical_path_coverage_summary
    assert summary["planned_page_coverage_ratio"] == 0.833
    assert result.evidence_assessment.delivery_status == "supplement_required"
    assert critical is not None
    assert "[P0] 登录" in critical.failing_final_paths
    assert "[P0] 登录" in critical.failing_fallback_paths
    assert any("critical path" in gap for gap in result.evidence_assessment.verification_gaps)
    assert any("[P0] 登录" in item for item in result.evidence_assessment.missing_coverage)


def test_p2_gap_does_not_block_final_when_p0_and_p1_paths_pass(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    entries = [
        ("login-screen.png", "登录", "成功态。", None),
        ("dashboard-home.png", "工作台首页", "默认态。", None),
        ("settings-page.png", "设置页", "保存成功态。", None),
        ("report-list.png", "报表列表", "空状态。", None),
        ("export-center.png", "导出中心", "成功态。", None),
    ]
    _write_screen_bundle(screens, entries)
    _patch_ocr_by_filename(
        monkeypatch,
        lines_by_file={
            "login-screen.png": ("登录", "登录成功"),
            "dashboard-home.png": ("工作台首页", "首页"),
            "settings-page.png": ("设置页", "保存成功"),
            "report-list.png": ("报表列表", "暂无数据"),
            "export-center.png": ("导出中心", "导出成功"),
        },
    )

    plan = core.plan_required_evidence(
        modules=[{"name": name} for name in ("登录", "工作台首页", "设置页", "报表列表", "导出中心", "通知中心")],
        key_features=[{"name": name} for name in ("登录", "查看工作台", "保存设置", "查看报表", "导出中心", "通知中心")],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 导出中心\n- 通知中心",
        journey_stages=["登录", "工作台首页", "设置页", "报表列表", "导出中心", "通知中心"],
        screenshots_dir=screens,
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 导出中心\n- 通知中心",
        required_evidence_plan=plan.required_evidence_plan,
    )

    summary = result.evidence_assessment.coverage_summary
    critical = result.evidence_assessment.critical_path_coverage_summary
    assert summary["planned_page_coverage_ratio"] == 0.833
    assert result.evidence_assessment.delivery_status == "final_delivery_ready"
    assert critical is not None
    assert critical.failing_final_paths == []
    assert critical.failing_fallback_paths == []
    assert "通知中心" in summary["missing_tasks"]


def test_p1_critical_path_gap_downgrades_to_fallback_with_path_explanation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    entries = [
        ("login-screen.png", "登录", "成功态。", None),
        ("dashboard-home.png", "工作台首页", "默认态。", None),
        ("report-list.png", "报表列表", "空状态。", None),
        ("notice-center.png", "通知中心", "默认态。", None),
    ]
    _write_screen_bundle(screens, entries)
    _patch_ocr_by_filename(
        monkeypatch,
        lines_by_file={
            "login-screen.png": ("登录", "登录成功"),
            "dashboard-home.png": ("工作台首页", "首页"),
            "report-list.png": ("报表列表", "暂无数据"),
            "notice-center.png": ("通知中心", "消息中心"),
        },
    )

    plan = core.plan_required_evidence(
        modules=[{"name": name} for name in ("登录", "工作台首页", "设置页", "报表列表", "通知中心")],
        key_features=[{"name": name} for name in ("登录", "查看工作台", "保存设置", "查看报表", "通知中心")],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        journey_stages=["登录", "工作台首页", "设置页", "报表列表", "通知中心"],
        screenshots_dir=screens,
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        required_evidence_plan=plan.required_evidence_plan,
    )

    critical = result.evidence_assessment.critical_path_coverage_summary
    assert result.evidence_assessment.delivery_status == "fallback_safe"
    assert critical is not None
    assert "[P1] 设置页" in critical.failing_final_paths
    assert critical.failing_fallback_paths == []
    assert any("critical path" in gap for gap in result.evidence_assessment.verification_gaps)
    assert any("设置页" in action for action in result.evidence_assessment.required_actions)


def test_plan_required_evidence_returns_structured_one_shot_gap_list(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    _write_png(screens / "login-default.png", size=(1440, 900))
    _write_png(screens / "dashboard-default.png", size=(1440, 900))

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    result = core.plan_required_evidence(
        modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}, {"name": "报表列表"}],
        key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}, {"name": "查看报表"}],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        journey_stages=["进入登录", "进入工作台", "保存设置", "查看报表"],
        screenshots_dir=screens,
        output_dir=output_dir,
    )

    assert result.capture_mission.must_capture_pages
    assert result.capture_mission.critical_flows
    assert result.capture_mission.final_delivery_pass_line
    assert result.capture_mission.fallback_pass_line
    assert result.capture_mission.mission_doc_path is not None
    assert Path(result.capture_mission.mission_doc_path).exists()
    assert result.evidence_input_guidance.pre_run_status == "supplement_required"
    assert "设置页" in "；".join(result.evidence_input_guidance.missing_pages)
    assert "报表列表" in "；".join(result.evidence_input_guidance.missing_pages)
    assert any(
        "Capture Mission" in action or "must_capture_pages" in action
        for action in result.evidence_input_guidance.required_actions
    )


def test_load_and_analyze_uses_required_evidence_plan_for_coverage_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    for name in ("login-default.png", "dashboard-default.png", "settings-default.png"):
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "# 登录\n\n登录默认态。\n\n# 工作台首页\n\n首页默认态。\n\n# 设置页\n\n设置默认态。",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    plan = core.plan_required_evidence(
        modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}, {"name": "报表列表"}],
        key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}, {"name": "查看报表"}],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        journey_stages=["进入登录", "进入工作台", "保存设置", "查看报表"],
        screenshots_dir=screens,
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        required_evidence_plan=plan.required_evidence_plan,
    )

    summary = result.evidence_assessment.coverage_summary
    assert summary["required_evidence_plan_version"] == "2026-05-25"
    assert summary["capture_mission_version"] == "2026-05-25"
    assert summary["final_delivery_pass_line"] == plan.capture_mission.final_delivery_pass_line
    assert summary["fallback_pass_line"] == plan.capture_mission.fallback_pass_line
    assert "报表列表" in "；".join(summary["missing_critical_pages"])
    assert "报表列表" in "；".join(result.evidence_assessment.missing_coverage)
    assert any(
        "final pass line:" in gap
        for gap in result.evidence_assessment.verification_gaps
    )


def test_missing_p0_critical_path_blocks_final_even_when_average_page_coverage_is_high(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    ocr_pages = {
        "home.png": ("工作台首页",),
        "settings.png": ("设置页",),
        "report.png": ("报表列表",),
        "export.png": ("导出中心",),
        "notify.png": ("通知中心",),
    }
    for name in ocr_pages:
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## home.png",
                "这是工作台首页加载态。",
                "",
                "## settings.png",
                "这是设置页成功态。",
                "",
                "## report.png",
                "这是报表列表空状态。",
                "",
                "## export.png",
                "这是导出中心成功态。",
                "",
                "## notify.png",
                "这是通知中心默认态。",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=True, backend="tesseract"),
    )
    monkeypatch.setattr(
        core,
        "run_ocr",
        lambda path, preferred_backend=None: OCRResult(
            backend="tesseract",
            lines=tuple(OCRLine(text=text, confidence=0.93) for text in ocr_pages[path.name]),
            raw_text="\n".join(ocr_pages[path.name]),
        ),
    )

    plan = core.plan_required_evidence(
        modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}, {"name": "报表列表"}, {"name": "导出中心"}, {"name": "通知中心"}],
        key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}, {"name": "查看报表"}, {"name": "导出中心"}, {"name": "通知中心"}],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 导出中心\n- 通知中心",
        journey_stages=["登录", "进入工作台", "保存设置", "查看报表", "导出中心", "通知中心"],
        screenshots_dir=screens,
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 导出中心\n- 通知中心",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir,
        run_id="001-p0-missing",
        stage_id="screenshot-loading",
    )

    assert result.evidence_assessment.delivery_status == "supplement_required"
    assert result.evidence_assessment.coverage_summary["planned_page_coverage_ratio"] == 0.833
    assert result.evidence_assessment.critical_path_coverage_summary is not None
    assert "[P0] 登录" in result.evidence_assessment.critical_path_coverage_summary.failing_final_paths
    assert "[P0] 登录" in result.evidence_assessment.critical_path_coverage_summary.failing_fallback_paths
    assert any("[P0] 登录" in item for item in result.evidence_assessment.missing_coverage)


def test_missing_p2_path_does_not_block_final_when_p0_p1_paths_are_covered(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    ocr_pages = {
        "login.png": ("登录",),
        "home.png": ("工作台首页",),
        "settings.png": ("设置页",),
        "report.png": ("报表列表",),
        "export.png": ("导出中心",),
    }
    for name in ocr_pages:
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## login.png",
                "这是登录页加载态。",
                "",
                "## home.png",
                "这是工作台首页加载态。",
                "",
                "## settings.png",
                "这是设置页成功态。",
                "",
                "## report.png",
                "这是报表列表空状态。",
                "",
                "## export.png",
                "这是导出中心成功态。",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=True, backend="tesseract"),
    )
    monkeypatch.setattr(
        core,
        "run_ocr",
        lambda path, preferred_backend=None: OCRResult(
            backend="tesseract",
            lines=tuple(OCRLine(text=text, confidence=0.93) for text in ocr_pages[path.name]),
            raw_text="\n".join(ocr_pages[path.name]),
        ),
    )

    plan = core.plan_required_evidence(
        modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}, {"name": "报表列表"}, {"name": "导出中心"}, {"name": "通知中心"}],
        key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}, {"name": "查看报表"}, {"name": "导出中心"}, {"name": "通知中心"}],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 导出中心\n- 通知中心",
        journey_stages=["登录", "进入工作台", "保存设置", "查看报表", "导出中心", "通知中心"],
        screenshots_dir=screens,
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 导出中心\n- 通知中心",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir,
        run_id="001-p2-missing",
        stage_id="screenshot-loading",
    )

    assert result.evidence_assessment.delivery_status == "final_delivery_ready"
    assert result.evidence_assessment.coverage_summary["planned_page_coverage_ratio"] == 0.833
    assert result.evidence_assessment.critical_path_coverage_summary is not None
    assert result.evidence_assessment.critical_path_coverage_summary.failing_final_paths == []
    assert result.evidence_assessment.coverage_summary["final_delivery_missing_critical_paths"] == []


def test_missing_p1_path_downgrades_to_fallback_with_path_level_explanation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    ocr_pages = {
        "login.png": ("登录",),
        "home.png": ("工作台首页",),
        "settings.png": ("设置页",),
        "notify.png": ("通知中心",),
    }
    for name in ocr_pages:
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## login.png",
                "这是登录页加载态。",
                "",
                "## home.png",
                "这是工作台首页加载态。",
                "",
                "## settings.png",
                "这是设置页成功态。",
                "",
                "## notify.png",
                "这是通知中心默认态。",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=True, backend="tesseract"),
    )
    monkeypatch.setattr(
        core,
        "run_ocr",
        lambda path, preferred_backend=None: OCRResult(
            backend="tesseract",
            lines=tuple(OCRLine(text=text, confidence=0.93) for text in ocr_pages[path.name]),
            raw_text="\n".join(ocr_pages[path.name]),
        ),
    )

    plan = core.plan_required_evidence(
        modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}, {"name": "报表列表"}, {"name": "通知中心"}],
        key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}, {"name": "查看报表"}, {"name": "通知中心"}],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        journey_stages=["登录", "进入工作台", "保存设置", "查看报表", "通知中心"],
        screenshots_dir=screens,
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir,
        run_id="001-p1-fallback",
        stage_id="screenshot-loading",
    )

    assert result.evidence_assessment.delivery_status == "fallback_safe"
    assert result.evidence_assessment.critical_path_coverage_summary is not None
    assert "[P1] 报表列表" in result.evidence_assessment.critical_path_coverage_summary.failing_final_paths
    assert result.evidence_assessment.critical_path_coverage_summary.failing_fallback_paths == []
    assert any("[P1] 报表列表" in item for item in result.evidence_assessment.verification_gaps)


def test_repeated_same_pre_run_gap_raises_planning_loop_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    _write_png(screens / "login-default.png", size=(1440, 900))

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    first = core.plan_required_evidence(
        modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}],
        key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页",
        journey_stages=["进入登录", "进入工作台", "保存设置"],
        screenshots_dir=screens,
        output_dir=output_dir,
        run_id="001-pre-run-loop",
        stage_id="evidence-planning",
    )
    assert first.evidence_input_guidance.pre_run_status == "supplement_required"

    with pytest.raises(core.PlanningLoopError):
        core.plan_required_evidence(
            modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}],
            key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}],
            task_checklist_lite="- 登录\n- 工作台首页\n- 设置页",
            journey_stages=["进入登录", "进入工作台", "保存设置"],
            screenshots_dir=screens,
            output_dir=output_dir,
            run_id="001-pre-run-loop",
            stage_id="evidence-planning",
        )


def test_ready_inputs_do_not_repeat_capture_mission_supplement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    for name in (
        "login-default.png",
        "login-loading.png",
        "login-error.png",
        "login-success.png",
        "dashboard-default.png",
        "dashboard-loading.png",
        "dashboard-empty.png",
        "settings-default.png",
        "settings-loading.png",
        "settings-error.png",
        "settings-success.png",
    ):
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## login-default.png",
                "这是登录页默认态。",
                "",
                "## login-loading.png",
                "这是登录页加载态。",
                "",
                "## login-error.png",
                "这是登录页错误态。",
                "",
                "## login-success.png",
                "这是登录页成功态。",
                "",
                "## dashboard-default.png",
                "这是工作台首页默认态。",
                "",
                "## dashboard-loading.png",
                "这是工作台首页加载态。",
                "",
                "## dashboard-empty.png",
                "这是工作台首页空状态。",
                "",
                "## settings-default.png",
                "这是设置页默认态。",
                "",
                "## settings-loading.png",
                "这是设置页加载态。",
                "",
                "## settings-error.png",
                "这是设置页错误态。",
                "",
                "## settings-success.png",
                "这是设置页成功态。",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    result = core.plan_required_evidence(
        modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}],
        key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页",
        journey_stages=["进入登录", "进入工作台", "保存设置"],
        screenshots_dir=screens,
    )

    assert result.evidence_input_guidance.pre_run_status == "ready"
    assert result.evidence_input_guidance.required_actions == []
    assert result.capture_mission.must_capture_pages


def test_auto_remediation_promotes_sectioned_descriptions_to_final_delivery_ready(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    filenames = [
        "screen-01.png",
        "screen-02.png",
        "screen-03.png",
        "screen-04.png",
        "screen-05.png",
    ]
    for name in filenames:
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## screen-01.png",
                "这是登录页，主按钮为登录。",
                "",
                "## screen-02.png",
                "这是工作台首页，顶部有首页导航。",
                "",
                "## screen-03.png",
                "这是设置页，包含设置项确认按钮。",
                "",
                "## screen-04.png",
                "这是报表列表页，可查看报表列表。",
                "",
                "## screen-05.png",
                "这是导出成功状态页，页面提示导出成功。",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 导出成功",
        output_dir=output_dir,
        run_id="001-remediate-final",
        stage_id="screenshot-loading",
    )

    summary = result.evidence_assessment.coverage_summary
    assert result.evidence_assessment.delivery_status == "final_delivery_ready"
    assert summary["delivery_status_before_remediation"] == "final_delivery_ready"
    assert summary["auto_remediation_attempted"] is False
    assert summary["auto_remediation_changed"] is False
    assert summary["auto_remediation_note_count"] == 0
    assert summary["auto_remediation_note_paths"] == []


def test_high_confidence_auto_mapping_continues_without_user_confirmation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    for name in (
        "IMG1001.png",
        "IMG1002.png",
        "IMG1003.png",
        "IMG1004.png",
        "IMG1005.png",
        "IMG1006.png",
        "IMG1007.png",
        "IMG1008.png",
        "IMG1009.png",
        "IMG1010.png",
    ):
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## IMG1001.png",
                "这是登录页加载态。",
                "",
                "## IMG1002.png",
                "这是登录页错误态。",
                "",
                "## IMG1003.png",
                "这是登录页成功态。",
                "",
                "## IMG1004.png",
                "这是工作台首页加载态。",
                "",
                "## IMG1005.png",
                "这是工作台首页空状态。",
                "",
                "## IMG1006.png",
                "这是设置页加载态。",
                "",
                "## IMG1007.png",
                "这是设置页成功态。",
                "",
                "## IMG1008.png",
                "这是设置页错误态。",
                "",
                "## IMG1009.png",
                "这是报表列表加载态。",
                "",
                "## IMG1010.png",
                "这是报表列表空状态。",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    plan = core.plan_required_evidence(
        modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}, {"name": "报表列表"}],
        key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}, {"name": "查看报表"}],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        journey_stages=["进入登录", "进入工作台", "保存设置", "查看报表"],
        screenshots_dir=screens,
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir,
        run_id="001-auto-map-ready",
        stage_id="screenshot-loading",
    )

    image_refs = [ref for ref in result.screenshots if ref.kind == "image"]
    assert result.evidence_assessment.delivery_status == "final_delivery_ready"
    assert result.evidence_assessment.clarification_items == []
    assert result.evidence_assessment.clarification_package_path is None
    assert result.evidence_assessment.coverage_summary["naming_issues"]
    assert result.evidence_assessment.coverage_summary["capture_order"] == plan.capture_mission.capture_order
    assert all(ref.draft_mapping is not None for ref in image_refs)
    assert all(
        ref.draft_mapping is not None and ref.draft_mapping.clarification_needed is False
        for ref in image_refs
    )


def test_auto_remediation_can_only_reach_fallback_safe_when_key_pages_are_insufficient(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    for name in ("screen-01.png", "screen-02.png"):
        _write_png(screens / name, size=(1440, 900))
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

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页",
        output_dir=output_dir,
        run_id="001-remediate-fallback",
        stage_id="screenshot-loading",
    )

    summary = result.evidence_assessment.coverage_summary
    assert summary["auto_remediation_attempted"] is True
    assert summary["auto_remediation_changed"] is True
    assert result.evidence_assessment.delivery_status == "fallback_safe"
    assert result.evidence_assessment.final_delivery_ready is False
    assert "关键页面截图数量不足" in "；".join(result.evidence_assessment.missing_coverage)
    first_pass = result.evidence_assessment.first_pass_success_breakdown
    assert isinstance(first_pass, dict)
    assert "missing_evidence" in first_pass["supplement_cause_classification"]
    assert first_pass["upstream_diagnosis"] == "input_truly_insufficient"
    metrics = result.evidence_assessment.client_mode_metrics
    benchmark = result.evidence_assessment.benchmark_summary
    assert metrics is not None
    assert benchmark is not None
    assert metrics.delivery_status == "fallback_safe"
    assert metrics.success_metrics.fallback_safe_rate == 1.0
    assert metrics.success_metrics.final_delivery_ready_rate == 0.0
    assert benchmark.delivery_status == "fallback_safe"
    assert benchmark.root_cause == "input_truly_insufficient"
    assert "trusted_mapping_rate<0.90" in benchmark.unmet_metrics
    assert benchmark.artifact_paths["benchmark_json_path"].endswith(
        "outputs/benchmark/client_mode_benchmark_summary.json"
    )
    assert Path(benchmark.artifact_paths["benchmark_json_path"]).exists()
    assert Path(benchmark.artifact_paths["benchmark_markdown_path"]).exists()


def test_targeted_acquisition_prioritizes_p0_missing_page_over_secondary_p1_gap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    _write_screen_bundle(
        screens,
        [
            ("dash-default.png", "工作台首页", "默认态", "这是工作台首页默认态。"),
            ("settings-default.png", "设置页", "默认态", "这是设置页默认态。"),
            ("report-empty.png", "报表列表", "空状态", "这是报表列表空状态。"),
            ("notice-default.png", "通知中心", "默认态", "这是通知中心默认态。"),
            ("profile-default.png", "个人中心", "默认态", "这是个人中心默认态。"),
        ],
    )

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    plan = core.plan_required_evidence(
        modules=[{"name": name} for name in ("登录", "工作台首页", "设置页", "报表列表", "通知中心", "个人中心")],
        key_features=[{"name": name} for name in ("登录", "查看工作台", "保存设置", "查看报表", "通知中心", "个人中心")],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心\n- 个人中心",
        journey_stages=["登录", "工作台首页", "设置页", "报表列表", "通知中心", "个人中心"],
        screenshots_dir=screens,
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心\n- 个人中心",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir,
        run_id="001-targeted-p0-first",
        stage_id="screenshot-loading",
    )

    assert result.evidence_assessment.delivery_status == "supplement_required"
    first_pass = result.evidence_assessment.first_pass_success_breakdown
    targeted_plan = result.evidence_assessment.targeted_acquisition_plan
    assert isinstance(first_pass, dict)
    assert targeted_plan is not None
    assert "missing_evidence" in targeted_plan.supplement_cause_classification
    assert targeted_plan.supplement_cause_classification == first_pass["supplement_cause_classification"]
    assert len(targeted_plan.must_acquire_now) <= 3
    top_item = targeted_plan.highest_value_next_captures[0]
    assert top_item.target_page == "登录"
    assert top_item.action_class == "must_acquire_now"
    assert top_item.suggested_input_form == "screenshot"
    assert "[P0] 登录" in top_item.affected_critical_paths
    assert any(
        lift.metric == "critical_path_page_hit_rate"
        for lift in top_item.expected_metric_lift
    )


def test_sectioned_markdown_remediation_improves_first_pass_success_without_lowering_final_gate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    for name in ("shot-01.png", "shot-02.png", "shot-03.png", "shot-04.png", "shot-05.png"):
        _write_png(screens / name, size=(1440, 900))
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

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=True, backend="tesseract"),
    )
    _patch_ocr_by_filename(
        monkeypatch,
        lines_by_file={
            "shot-01.png": ("登录",),
            "shot-02.png": ("首页",),
            "shot-03.png": ("保存成功",),
            "shot-04.png": ("暂无数据",),
            "shot-05.png": ("消息中心",),
        },
    )

    plan = core.plan_required_evidence(
        modules=[{"name": name} for name in ("登录", "工作台首页", "设置页", "报表列表", "通知中心")],
        key_features=[{"name": name} for name in ("登录", "查看工作台", "保存设置", "查看报表", "通知中心")],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        journey_stages=["登录", "工作台首页", "设置页", "报表列表", "通知中心"],
        screenshots_dir=screens,
    )

    files = core._collect_files(screens)
    baseline_refs = core._build_refs(files, root=screens, ocr_backend=None)
    baseline_refs, _ = core._apply_draft_mappings(
        baseline_refs,
        plan=plan.required_evidence_plan,
    )
    baseline_assessment = core._evidence_assessment(
        baseline_refs,
        ocr_available=True,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        required_evidence_plan=plan.required_evidence_plan,
    )
    assert baseline_assessment.delivery_status != "final_delivery_ready"

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir,
        run_id="001-first-pass-uplift",
        stage_id="screenshot-loading",
    )

    summary = result.evidence_assessment.coverage_summary
    first_pass = result.evidence_assessment.first_pass_success_breakdown
    assert result.evidence_assessment.delivery_status == "final_delivery_ready"
    assert isinstance(first_pass, dict)
    assert first_pass["first_pass_final_rate"] == 0.0
    assert first_pass["baseline_delivery_status"] == baseline_assessment.delivery_status
    assert first_pass["post_remediation_delivery_status"] == "final_delivery_ready"
    assert (
        first_pass["post_remediation_trusted_mapping"]["trusted_mapping_rate"]
        > first_pass["pre_remediation_trusted_mapping"]["trusted_mapping_rate"]
    )
    assert (
        first_pass["post_remediation_critical_path_coverage"]["final_pass_ratio"]
        >= first_pass["pre_remediation_critical_path_coverage"]["final_pass_ratio"]
    )
    assert first_pass["upstream_diagnosis"] == "existing_input_was_salvageable_but_needed_better_ingestion"
    assert summary["auto_remediation_markdown_section_uplift_count"] >= 1
    assert result.evidence_assessment.targeted_acquisition_plan is not None
    assert result.evidence_assessment.targeted_acquisition_plan.highest_value_next_captures == []
    metrics = result.evidence_assessment.client_mode_metrics
    benchmark = result.evidence_assessment.benchmark_summary
    assert metrics is not None
    assert benchmark is not None
    assert metrics.delivery_status == "final_delivery_ready"
    assert metrics.success_metrics.final_delivery_ready_rate == 1.0
    assert metrics.success_metrics.first_pass_final_rate == 0.0
    assert metrics.success_metrics.auto_remediation_lift > 0.0
    assert metrics.success_metrics.salvageable_input_rate == 1.0
    assert metrics.trust_metrics.trusted_mapping_rate >= 0.9
    assert benchmark.delivery_status == "final_delivery_ready"
    assert benchmark.root_cause == "system_ingestion_gap"
    assert "critical_path_page_hit_rate>=0.90" in benchmark.met_metrics
    assert "trusted_mapping_rate>=0.90" in benchmark.met_metrics
    assert benchmark.unmet_metrics == []
    benchmark_json = Path(benchmark.artifact_paths["benchmark_json_path"])
    benchmark_payload = json.loads(benchmark_json.read_text(encoding="utf-8"))
    assert benchmark_payload["delivery_status"] == "final_delivery_ready"
    assert benchmark_payload["metrics"]["success_metrics"]["auto_remediation_lift"] > 0.0


def test_ambiguous_auto_mapping_generates_minimal_clarification_package(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    for name in ("IMG2001.png", "IMG2002.png", "IMG2003.png", "IMG2004.png", "IMG2005.png"):
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## IMG2001.png",
                "这是登录页加载态。",
                "",
                "## IMG2002.png",
                "这是登录页错误态。",
                "",
                "## IMG2003.png",
                "这是工作台首页默认态。",
                "",
                "## IMG2004.png",
                "这个页面可能是设置页或报表列表，当前只看到列表区域和一个保存入口。",
                "",
                "## IMG2005.png",
                "这是设置页保存成功态。",
            ]
        ),
        encoding="utf-8",
    )

    _patch_ocr_by_filename(
        monkeypatch,
        lines_by_file={
            "IMG2001.png": ("登录", "加载中"),
            "IMG2002.png": ("登录", "登录失败"),
            "IMG2003.png": ("工作台首页", "首页"),
            "IMG2004.png": ("保存", "列表"),
            "IMG2005.png": ("设置页", "保存成功"),
        },
    )

    plan = core.plan_required_evidence(
        modules=[{"name": "登录"}, {"name": "工作台首页"}, {"name": "设置页"}, {"name": "报表列表"}],
        key_features=[{"name": "登录"}, {"name": "查看工作台"}, {"name": "保存设置"}, {"name": "查看报表"}],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        journey_stages=["进入登录", "进入工作台", "保存设置", "查看报表"],
        screenshots_dir=screens,
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir,
        run_id="001-auto-map-clarify",
        stage_id="screenshot-loading",
    )

    clarification_items = result.evidence_assessment.clarification_items
    assert len(clarification_items) == 1
    assert clarification_items[0].confidence == "low"
    assert clarification_items[0].relative_path == "IMG2004.png"
    assert clarification_items[0].screenshot_ref == "IMG2004.png"
    assert "设置页" in clarification_items[0].candidate_pages
    assert "报表列表" in clarification_items[0].candidate_pages
    assert clarification_items[0].affected_critical_paths
    assert clarification_items[0].confirmation_prompt
    assert result.evidence_assessment.clarification_package_path is not None
    assert "只确认其中列出的歧义截图" in "；".join(result.evidence_assessment.required_actions)

    package_dir = Path(result.evidence_assessment.clarification_package_path or "")
    clarification_markdown = package_dir / "clarification-needed.md"
    draft_map = package_dir / "draft-screens-map.md"
    assert clarification_markdown.exists()
    assert draft_map.exists()
    content = clarification_markdown.read_text(encoding="utf-8")
    assert "IMG2004.png" in content
    assert "affected_critical_paths" in content
    assert "confirmation_prompt" in content
    assert "IMG2001.png" not in content
    assert result.evidence_assessment.coverage_summary["clarification_needed_count"] == 1
    assert len(clarification_items) < len([ref for ref in result.screenshots if ref.kind == "image"])
    targeted_plan = result.evidence_assessment.targeted_acquisition_plan
    assert targeted_plan is not None
    assert targeted_plan.highest_value_next_captures
    top_item = targeted_plan.highest_value_next_captures[0]
    assert top_item.action_class == "clarify_existing_evidence"
    assert top_item.suggested_input_form == "clarification"
    assert top_item.screenshot_ref == "IMG2004.png"
    assert top_item.expected_unlocks_final_delivery is True


def test_same_run_surfaces_clarification_only_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    for name in ("IMG2101.png", "IMG2102.png", "IMG2103.png", "IMG2104.png", "IMG2105.png"):
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## IMG2101.png",
                "这是登录页成功态。",
                "",
                "## IMG2102.png",
                "这是工作台首页默认态。",
                "",
                "## IMG2103.png",
                "这个页面可能是设置页或报表列表，当前只看到列表区域和一个保存入口。",
                "",
                "## IMG2104.png",
                "这是报表列表空状态。",
                "",
                "## IMG2105.png",
                "这是通知中心默认态。",
            ]
        ),
        encoding="utf-8",
    )
    _patch_ocr_by_filename(
        monkeypatch,
        lines_by_file={
            "IMG2101.png": ("登录", "登录成功"),
            "IMG2102.png": ("工作台首页", "首页"),
            "IMG2103.png": ("保存", "列表"),
            "IMG2104.png": ("报表列表", "暂无数据"),
            "IMG2105.png": ("通知中心", "消息中心"),
        },
    )

    plan = core.plan_required_evidence(
        modules=[{"name": name} for name in ("登录", "工作台首页", "设置页", "报表列表", "通知中心")],
        key_features=[{"name": name} for name in ("登录", "查看工作台", "保存设置", "查看报表", "通知中心")],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        journey_stages=["登录", "工作台首页", "设置页", "报表列表", "通知中心"],
        screenshots_dir=screens,
        output_dir=output_dir,
        run_id="001-clarify-once",
        stage_id="evidence-planning",
    )

    assert plan.evidence_input_guidance.clarification_package_path is not None

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir,
        run_id="001-clarify-once",
        stage_id="screenshot-loading",
    )

    assert result.evidence_assessment.clarification_package_path is not None
    state_path = output_dir / "clarification" / "state.json"
    assert state_path.exists()
    assert '"surface_count": 1' in state_path.read_text(encoding="utf-8")
    assert not any(
        action.startswith("先查看 ")
        for action in result.evidence_assessment.required_actions
    )


def test_large_missing_evidence_does_not_surface_clarification_package(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    _write_png(screens / "IMG2201.png", size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## IMG2201.png",
                "这个页面可能是设置页或报表列表，当前只看到列表区域和一个保存入口。",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    plan = core.plan_required_evidence(
        modules=[{"name": name} for name in ("登录", "工作台首页", "设置页", "报表列表")],
        key_features=[{"name": name} for name in ("登录", "查看工作台", "保存设置", "查看报表")],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        journey_stages=["登录", "工作台首页", "设置页", "报表列表"],
        screenshots_dir=screens,
        output_dir=output_dir,
        run_id="001-no-clarify-large-gap",
        stage_id="evidence-planning",
    )

    assert plan.evidence_input_guidance.pre_run_status == "supplement_required"
    assert plan.evidence_input_guidance.clarification_items == []
    assert plan.evidence_input_guidance.clarification_package_path is None

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir,
        run_id="001-no-clarify-large-gap",
        stage_id="screenshot-loading",
    )

    assert result.evidence_assessment.delivery_status in {"supplement_required", "blocked"}
    assert result.evidence_assessment.clarification_items == []
    assert result.evidence_assessment.clarification_package_path is None


def test_clarification_mapping_file_promotes_trusted_mapping_and_final_readiness(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    for name in ("IMG2301.png", "IMG2302.png", "IMG2303.png", "IMG2304.png", "IMG2305.png"):
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## IMG2301.png",
                "这是登录页成功态。",
                "",
                "## IMG2302.png",
                "这是工作台首页默认态。",
                "",
                "## IMG2303.png",
                "这个页面可能是设置页或报表列表，当前只看到列表区域和一个保存入口。",
                "",
                "## IMG2304.png",
                "这是报表列表空状态。",
                "",
                "## IMG2305.png",
                "这是通知中心默认态。",
            ]
        ),
        encoding="utf-8",
    )
    _patch_ocr_by_filename(
        monkeypatch,
        lines_by_file={
            "IMG2301.png": ("登录", "登录成功"),
            "IMG2302.png": ("工作台首页", "首页"),
            "IMG2303.png": ("保存", "列表"),
            "IMG2304.png": ("报表列表", "暂无数据"),
            "IMG2305.png": ("通知中心", "消息中心"),
        },
    )

    plan = core.plan_required_evidence(
        modules=[{"name": name} for name in ("登录", "工作台首页", "设置页", "报表列表", "通知中心")],
        key_features=[{"name": name} for name in ("登录", "查看工作台", "保存设置", "查看报表", "通知中心")],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        journey_stages=["登录", "工作台首页", "设置页", "报表列表", "通知中心"],
        screenshots_dir=screens,
    )

    before = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir,
        run_id="001-clarify-to-final",
        stage_id="screenshot-loading",
    )

    assert before.evidence_assessment.delivery_status == "fallback_safe"
    assert before.evidence_assessment.clarification_items
    before_breakdown = before.evidence_assessment.delivery_readiness_breakdown
    assert isinstance(before_breakdown, dict)
    assert before_breakdown["final_gate_pass"] is False
    assert "clarification_residue" in before_breakdown["failing_final_gates"]
    assert "[P1] 设置页" in (
        before.evidence_assessment.critical_path_coverage_summary.failing_final_paths
        if before.evidence_assessment.critical_path_coverage_summary is not None
        else []
    )

    (screens / "screens-map.md").write_text(
        "- IMG2303.png -> page=设置页; states=success\n",
        encoding="utf-8",
    )

    after = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir,
        run_id="001-clarify-to-final",
        stage_id="screenshot-loading",
    )

    assert after.evidence_assessment.delivery_status == "final_delivery_ready"
    assert after.evidence_assessment.clarification_items == []
    assert after.evidence_assessment.coverage_summary["final_delivery_trusted_mapping_count"] > before.evidence_assessment.coverage_summary["final_delivery_trusted_mapping_count"]
    assert after.evidence_assessment.critical_path_coverage_summary is not None
    assert after.evidence_assessment.critical_path_coverage_summary.failing_final_paths == []
    after_breakdown = after.evidence_assessment.delivery_readiness_breakdown
    assert isinstance(after_breakdown, dict)
    assert after_breakdown["final_gate_pass"] is True
    assert after_breakdown["failing_final_gates"] == []
    after_metrics = after.evidence_assessment.client_mode_metrics
    before_metrics = before.evidence_assessment.client_mode_metrics
    assert before_metrics is not None
    assert after_metrics is not None
    assert before_metrics.human_burden_metrics.clarification_item_count == 1
    assert after_metrics.human_burden_metrics.clarification_item_count == 0
    assert after_metrics.trust_metrics.trusted_mapping_rate >= before_metrics.trust_metrics.trusted_mapping_rate


def test_state_specific_evidence_lifts_trusted_mapping_and_first_pass_final(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    for name in ("IMG5101.png", "IMG5102.png", "IMG5103.png", "IMG5104.png", "IMG5105.png"):
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## IMG5101.png",
                "这是登录页成功态。",
                "",
                "## IMG5102.png",
                "这是工作台首页默认态。",
                "",
                "## IMG5103.png",
                "这里只看到保存成功提示和确认反馈，没有直接写页面名。",
                "",
                "## IMG5104.png",
                "这里只看到暂无数据提示，用来说明空状态。",
                "",
                "## IMG5105.png",
                "这是通知中心默认态。",
            ]
        ),
        encoding="utf-8",
    )
    _patch_ocr_by_filename(
        monkeypatch,
        lines_by_file={
            "IMG5101.png": ("登录", "登录成功"),
            "IMG5102.png": ("工作台首页", "首页"),
            "IMG5103.png": ("保存成功",),
            "IMG5104.png": ("暂无数据",),
            "IMG5105.png": ("通知中心", "消息中心"),
        },
    )

    plan = core.plan_required_evidence(
        modules=[{"name": name} for name in ("登录", "工作台首页", "设置页", "报表列表", "通知中心")],
        key_features=[{"name": name} for name in ("登录", "查看工作台", "保存设置", "查看报表", "通知中心")],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        journey_stages=["登录", "工作台首页", "设置页", "报表列表", "通知中心"],
        screenshots_dir=screens,
    )

    files = core._collect_files(screens)
    refs = core._build_refs(files, root=screens, ocr_backend="tesseract")
    legacy_refs = [
        ref.model_copy(update={"state_text_candidates": []})
        if ref.kind == "image"
        else ref
        for ref in refs
    ]
    legacy_refs, _ = core._apply_draft_mappings(legacy_refs, plan=plan.required_evidence_plan)
    legacy_assessment = core._evidence_assessment(
        legacy_refs,
        ocr_available=True,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        required_evidence_plan=plan.required_evidence_plan,
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        required_evidence_plan=plan.required_evidence_plan,
        output_dir=output_dir,
        run_id="001-state-unique-lift",
        stage_id="screenshot-loading",
    )

    image_refs = {ref.relative_path: ref for ref in result.screenshots if ref.kind == "image"}
    assert image_refs["IMG5103.png"].draft_mapping is not None
    assert image_refs["IMG5103.png"].draft_mapping.page_name == "设置页"
    assert image_refs["IMG5103.png"].draft_mapping.final_delivery_eligible is True
    assert image_refs["IMG5104.png"].draft_mapping is not None
    assert image_refs["IMG5104.png"].draft_mapping.page_name == "报表列表"
    assert image_refs["IMG5104.png"].draft_mapping.final_delivery_eligible is True

    metrics = result.evidence_assessment.client_mode_metrics
    benchmark = result.evidence_assessment.benchmark_summary
    assert metrics is not None
    assert benchmark is not None
    assert result.evidence_assessment.delivery_status == "final_delivery_ready"
    assert metrics.success_metrics.first_pass_final_rate == 0.0
    assert metrics.success_metrics.auto_remediation_lift > 0.0
    assert metrics.human_burden_metrics.clarification_item_count == 0
    assert metrics.trust_metrics.trusted_mapping_rate > 0.9
    legacy_metrics = core._client_mode_metrics(legacy_assessment)
    assert metrics.trust_metrics.trusted_mapping_rate > legacy_metrics.trust_metrics.trusted_mapping_rate
    assert (
        metrics.coverage_metrics.critical_path_state_hit_rate
        > legacy_metrics.coverage_metrics.critical_path_state_hit_rate
    )
    assert "critical_path_state_hit_rate>=0.90" in benchmark.met_metrics


def test_conflicting_state_signals_do_not_promote_trusted_mapping(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    for name in ("IMG5201.png", "IMG5202.png", "IMG5203.png", "IMG5204.png", "IMG5205.png"):
        _write_png(screens / name, size=(1440, 900))
    (screens / "screens-description.md").write_text(
        "\n".join(
            [
                "# 关键页面说明",
                "",
                "## IMG5201.png",
                "这是登录页成功态。",
                "",
                "## IMG5202.png",
                "这是工作台首页默认态。",
                "",
                "## IMG5203.png",
                "这是报表列表空状态。",
                "",
                "## IMG5204.png",
                "这是通知中心默认态。",
                "",
                "## IMG5205.png",
                "这是个人中心默认态。",
            ]
        ),
        encoding="utf-8",
    )
    _patch_ocr_by_filename(
        monkeypatch,
        lines_by_file={
            "IMG5201.png": ("登录", "登录成功"),
            "IMG5202.png": ("工作台首页", "首页"),
            "IMG5203.png": ("保存成功",),
            "IMG5204.png": ("通知中心", "消息中心"),
            "IMG5205.png": ("个人中心", "我的"),
        },
    )

    plan = core.plan_required_evidence(
        modules=[{"name": name} for name in ("登录", "工作台首页", "设置页", "报表列表", "通知中心", "个人中心")],
        key_features=[{"name": name} for name in ("登录", "查看工作台", "保存设置", "查看报表", "通知中心", "个人中心")],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心\n- 个人中心",
        journey_stages=["登录", "工作台首页", "设置页", "报表列表", "通知中心", "个人中心"],
        screenshots_dir=screens,
    )

    result = core.load_and_analyze(
        screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心\n- 个人中心",
        required_evidence_plan=plan.required_evidence_plan,
        run_id="001-state-conflict",
        stage_id="screenshot-loading",
    )

    image_refs = {ref.relative_path: ref for ref in result.screenshots if ref.kind == "image"}
    assert image_refs["IMG5203.png"].draft_mapping is not None
    assert image_refs["IMG5203.png"].draft_mapping.final_delivery_eligible is False
    assert image_refs["IMG5203.png"].draft_mapping.mapping_verdict in {"conflicting", "ambiguous", "provisional"}
    assert result.evidence_assessment.delivery_status != "final_delivery_ready"


def test_benchmark_metrics_distinguish_salvageable_input_from_true_missing_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    salvageable_screens = tmp_path / "salvageable"
    salvageable_output = tmp_path / "salvageable-outputs"
    for name in ("shot-01.png", "shot-02.png", "shot-03.png", "shot-04.png", "shot-05.png"):
        _write_png(salvageable_screens / name, size=(1440, 900))
    (salvageable_screens / "screens-description.md").write_text(
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
    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=True, backend="tesseract"),
    )
    _patch_ocr_by_filename(
        monkeypatch,
        lines_by_file={
            "shot-01.png": ("登录",),
            "shot-02.png": ("首页",),
            "shot-03.png": ("保存成功",),
            "shot-04.png": ("暂无数据",),
            "shot-05.png": ("消息中心",),
        },
    )
    salvageable_plan = core.plan_required_evidence(
        modules=[{"name": name} for name in ("登录", "工作台首页", "设置页", "报表列表", "通知中心")],
        key_features=[{"name": name} for name in ("登录", "查看工作台", "保存设置", "查看报表", "通知中心")],
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        journey_stages=["登录", "工作台首页", "设置页", "报表列表", "通知中心"],
        screenshots_dir=salvageable_screens,
    )
    salvageable_result = core.load_and_analyze(
        salvageable_screens,
        task_checklist_lite="- 登录\n- 工作台首页\n- 设置页\n- 报表列表\n- 通知中心",
        required_evidence_plan=salvageable_plan.required_evidence_plan,
        output_dir=salvageable_output,
        run_id="001-benchmark-salvageable",
        stage_id="screenshot-loading",
    )

    missing_screens = tmp_path / "missing"
    missing_output = tmp_path / "missing-outputs"
    for name in ("screen-01.png", "screen-02.png"):
        _write_png(missing_screens / name, size=(1440, 900))
    (missing_screens / "screens-description.md").write_text(
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
    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )
    missing_result = core.load_and_analyze(
        missing_screens,
        task_checklist_lite="- 登录\n- 工作台首页",
        output_dir=missing_output,
        run_id="001-benchmark-missing",
        stage_id="screenshot-loading",
    )

    salvageable_metrics = salvageable_result.evidence_assessment.client_mode_metrics
    missing_metrics = missing_result.evidence_assessment.client_mode_metrics
    salvageable_benchmark = salvageable_result.evidence_assessment.benchmark_summary
    missing_benchmark = missing_result.evidence_assessment.benchmark_summary
    assert salvageable_metrics is not None
    assert missing_metrics is not None
    assert salvageable_benchmark is not None
    assert missing_benchmark is not None
    assert salvageable_metrics.success_metrics.salvageable_input_rate == 1.0
    assert missing_metrics.success_metrics.salvageable_input_rate == 0.0
    assert salvageable_metrics.success_metrics.auto_remediation_lift > missing_metrics.success_metrics.auto_remediation_lift
    assert salvageable_benchmark.root_cause == "system_ingestion_gap"
    assert missing_benchmark.root_cause == "input_truly_insufficient"


def test_repeated_unresolved_gap_raises_remediation_loop_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
    output_dir = tmp_path / "outputs"
    _write_png(screens / "mystery.png", size=(320, 200))

    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    first = core.load_and_analyze(
        screens,
        output_dir=output_dir,
        run_id="001-loop",
        stage_id="screenshot-loading",
    )
    assert first.evidence_assessment.delivery_status == "blocked"

    with pytest.raises(core.RemediationLoopError):
        core.load_and_analyze(
            screens,
            output_dir=output_dir,
            run_id="001-loop",
            stage_id="screenshot-loading",
        )


def test_golden_benchmark_sweep_generates_stable_case_compare(tmp_path: Path) -> None:
    sweep_dir = tmp_path / "golden-sweep"

    summary = benchmark_harness.run_golden_benchmark_sweep(sweep_dir)

    assert (sweep_dir / "golden_benchmark_sweep.json").exists()
    assert (sweep_dir / "golden_benchmark_sweep.md").exists()
    assert summary["run_mode"] == "client"
    assert len(summary["cases"]) == 5

    cases = {case["case_id"]: case for case in summary["cases"]}

    assert cases["case-final-mainline"]["delivery_status"] == "final_delivery_ready"
    assert cases["case-final-mainline"]["v1_5_target_met"] is True

    assert cases["case-hq-no-description"]["delivery_status"] in {"blocked", "supplement_required"}
    assert cases["case-hq-no-description"]["root_cause"] == "input_truly_insufficient"

    assert cases["case-salvageable"]["delivery_status"] == "final_delivery_ready"
    assert cases["case-salvageable"]["trusted_mapping_rate"] >= 0.9
    assert cases["case-salvageable"]["auto_remediation_lift"] > 0.0
    assert cases["case-salvageable"]["v1_5_target_met"] is True

    assert cases["case-missing-evidence"]["delivery_status"] in {"fallback_safe", "supplement_required"}
    assert cases["case-missing-evidence"]["root_cause"] == "input_truly_insufficient"

    assert cases["case-complex-multi-module"]["delivery_status"] == "final_delivery_ready"
    assert cases["case-complex-multi-module"]["critical_path_page_hit_rate"] >= 0.9
    assert cases["case-complex-multi-module"]["critical_path_state_hit_rate"] >= 0.9
    assert cases["case-complex-multi-module"]["trusted_mapping_rate"] >= 0.9
    assert cases["case-complex-multi-module"]["trusted_mapping_rate"] <= 1.0

    aggregate = summary["aggregate"]
    assert aggregate["case_count"] == 5
    assert aggregate["v1_5_target_met_rate"] == 1.0
    assert aggregate["final_capable_pass_rate"] == 1.0
    assert aggregate["bounded_safety_pass_rate"] == 1.0
    assert aggregate["final_delivery_ready_case_count"] >= 3
    assert aggregate["largest_remaining_bottleneck_metric"] == "objective_input_insufficiency"
    assert "Recommend Freeze" in aggregate["freeze_recommendation"]
    assert aggregate["largest_remaining_bottleneck_metric"]
    assert aggregate["strongest_case"]["case_id"]
    assert aggregate["weakest_case"]["case_id"]


def test_task_checklist_does_not_invent_task_or_module_attribution(
    fixtures_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    result = core.load_and_analyze(fixtures_path, task_checklist_lite="T-001 Login")

    for ref in result.screenshots:
        dumped = ref.model_dump()
        assert "matched_task_ids" not in dumped
        assert "matched_module_id" not in dumped
        assert "content_description" not in dumped


def test_empty_dir_returns_zero_counts(
    empty_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        core,
        "probe_ocr_backend",
        lambda: OCRProbeResult(available=False, backend=None, error="ocr unavailable"),
    )

    result = core.load_and_analyze(empty_dir)

    assert result.screenshots == []
    assert result.image_analysis.summary["total_files"] == 0
    assert result.image_analysis.summary["image_count"] == 0
    assert result.image_analysis.summary["description_count"] == 0
    assert result.evidence_assessment.verdict == "blocked"


def test_nonexistent_dir_raises_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        core.load_and_analyze(Path("/nonexistent/screenshots/dir"))


def test_file_path_raises_not_a_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "not_a_dir.txt"
    file_path.write_text("hello", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        core.load_and_analyze(file_path)
