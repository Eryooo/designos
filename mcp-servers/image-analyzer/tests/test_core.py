"""Unit tests for image-analyzer core logic."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))

import core
from ocr_runtime import OCRLine, OCRProbeResult, OCRResult
from schemas import DraftScreenshotMapping, EvidenceAssessment, ImageAnalysisSummary, LoadAnalyzeResult, ScreenshotRef


def _write_png(path: Path, *, size: tuple[int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, "white").save(path)


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
    assert any(
        "provisional mapping" in gap
        for gap in result.evidence_assessment.verification_gaps
    )


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
    assert all("重命名" not in action for action in result.evidence_input_guidance.required_actions)
    assert any(
        "screens-map.md" in suggestion
        for suggestion in result.evidence_input_guidance.optional_suggestions
    )


def test_plan_required_evidence_returns_structured_one_shot_gap_list(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screens = tmp_path / "screens"
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
    )

    assert result.evidence_input_guidance.pre_run_status == "supplement_required"
    assert "设置页" in "；".join(result.evidence_input_guidance.missing_pages)
    assert "报表列表" in "；".join(result.evidence_input_guidance.missing_pages)
    assert any("关键页面截图" in action or "关键页面" in action for action in result.evidence_input_guidance.required_actions)


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
    assert summary["required_evidence_plan_version"] == "2026-05-22"
    assert "报表列表" in "；".join(summary["missing_critical_pages"])
    assert "报表列表" in "；".join(result.evidence_assessment.missing_coverage)


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
    assert summary["delivery_status_before_remediation"] != "final_delivery_ready"
    assert result.evidence_assessment.delivery_status == "final_delivery_ready"
    assert summary["auto_remediation_attempted"] is True
    assert summary["auto_remediation_changed"] is True
    assert summary["auto_remediation_note_count"] == 5
    for raw_path in summary["auto_remediation_note_paths"]:
        assert Path(str(raw_path)).exists()


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
        run_id="001-auto-map-clarify",
        stage_id="screenshot-loading",
    )

    clarification_items = result.evidence_assessment.clarification_items
    assert len(clarification_items) == 1
    assert clarification_items[0].confidence == "low"
    assert clarification_items[0].relative_path == "IMG2004.png"
    assert "设置页" in clarification_items[0].candidate_pages
    assert "报表列表" in clarification_items[0].candidate_pages
    assert result.evidence_assessment.clarification_package_path is not None
    assert "只确认其中列出的歧义截图" in "；".join(result.evidence_assessment.required_actions)

    package_dir = Path(result.evidence_assessment.clarification_package_path or "")
    clarification_markdown = package_dir / "clarification-needed.md"
    assert clarification_markdown.exists()
    content = clarification_markdown.read_text(encoding="utf-8")
    assert "IMG2004.png" in content
    assert "IMG2001.png" not in content
    assert result.evidence_assessment.coverage_summary["clarification_needed_count"] == 1
    assert len(clarification_items) < len([ref for ref in result.screenshots if ref.kind == "image"])


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
