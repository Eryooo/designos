"""Core logic for image-analyzer (pure functions, no MCP dependencies).

This server provides real local screenshot-evidence processing:
- recursive screenshot and markdown discovery
- metadata extraction and readability assessment
- OCR text extraction when a local backend is available
- best-effort text cue classification (page title / button / nav / state)
- screenshot-to-description linking
- client-mode evidence sufficiency judgement

It still does not provide full semantic scene understanding, task attribution,
module attribution or intent inference.
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any, Iterable, cast

from ocr_runtime import OCRLine, probe_ocr_backend, run_ocr
from schemas import (
    BenchmarkSummary,
    CaptureMission,
    CapturePassPolicy,
    ClarificationItem,
    ClientModeMetrics,
    ConflictingEvidenceGroup,
    CoverageMetrics,
    CriticalPathCoverageRecord,
    CriticalPathCoverageSummary,
    CriticalPathDefinition,
    CriticalStateRequirement,
    DescriptionLink,
    DraftScreenshotMapping,
    EvidenceAssessment,
    EvidenceFusionSummary,
    EvidenceInputGuidance,
    EvidencePageRequirement,
    HumanBurdenMetrics,
    ImageAnalysisSummary,
    LoadAnalyzeResult,
    PageFusionRecord,
    PlanRequiredEvidenceResult,
    ReadabilityAssessment,
    RequiredEvidencePlan,
    ScreenshotRef,
    StateCategory,
    StateFusionRecord,
    SuccessThroughputMetrics,
    TargetedAcquisitionItem,
    TargetedAcquisitionPlan,
    TargetedMetricLift,
    TextCue,
    TrustMetrics,
)

_IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"})
_DESCRIPTION_EXTENSIONS = frozenset({".md"})
_DESCRIPTION_PREVIEW_CHARS = 200
_REMEDIATION_DIRNAME = "evidence-remediation"
_REMEDIATION_NOTES_DIRNAME = "generated-notes"
_REMEDIATION_STATE_FILENAME = "state.json"
_REMEDIATION_CLARIFICATION_DIRNAME = "clarification"
_PLANNING_DIRNAME = "evidence-planning"
_PLANNING_STATE_FILENAME = "state.json"
_PLANNING_CLARIFICATION_DIRNAME = "clarification"
_PLANNING_MISSION_FILENAME = "capture_mission.md"
_CLARIFICATION_DIRNAME = "clarification"
_CLARIFICATION_STATE_FILENAME = "state.json"
_TARGETED_ACQUISITION_DIRNAME = "targeted-acquisition"
_TARGETED_ACQUISITION_FILENAME = "targeted_acquisition_plan.md"
_BENCHMARK_DIRNAME = "benchmark"
_BENCHMARK_JSON_FILENAME = "client_mode_benchmark_summary.json"
_BENCHMARK_MD_FILENAME = "client_mode_benchmark_summary.md"
_MAX_CLARIFICATION_ITEMS = 3
_PLAN_VERSION = "2026-05-25"
_TARGETED_ACQUISITION_VERSION = "2026-05-26"
_BENCHMARK_CONTRACT_VERSION = "2026-05-27"
_LIGHTWEIGHT_MAPPING_FILES = ("screens-map.md", "screens-index.md")
_TOKEN_PATTERN = re.compile(r"[\u4e00-\u9fffA-Za-z0-9]+")
_STATE_PATTERNS = (
    re.compile(r"(加载中|正在加载|loading|please wait)", re.IGNORECASE),
    re.compile(r"(错误|失败|重试|error|failed|invalid|warning)", re.IGNORECASE),
    re.compile(r"(暂无|空状态|无数据|empty|no data|not found)", re.IGNORECASE),
    re.compile(r"(成功|已完成|success|completed)", re.IGNORECASE),
)
_BUTTON_HINTS = {
    "button",
    "login",
    "log in",
    "submit",
    "save",
    "confirm",
    "cancel",
    "delete",
    "next",
    "back",
    "retry",
    "search",
    "导出",
    "保存",
    "提交",
    "确认",
    "取消",
    "删除",
    "下一步",
    "返回",
    "重试",
    "搜索",
    "登录",
    "按钮",
}
_NAV_HINTS = {
    "home",
    "dashboard",
    "settings",
    "profile",
    "menu",
    "tab",
    "首页",
    "工作台",
    "设置",
    "我的",
    "消息",
    "返回",
    "导航",
}
_STATE_HINTS: dict[str, tuple[str, ...]] = {
    "default": ("首页", "home", "default", "overview", "登录", "login"),
    "success": ("成功", "success", "completed", "已完成"),
    "error": ("错误", "失败", "error", "failed", "invalid"),
    "loading": ("加载", "加载中", "正在加载", "loading", "please wait"),
    "empty": ("空", "暂无", "空状态", "empty", "no data", "not found"),
}
_SENSITIVE_SIGNAL_PATTERNS = (
    re.compile(r"\b(password|passwd|token|secret|credential|api[-_ ]?key)\b", re.IGNORECASE),
    re.compile(r"(身份证|手机号|邮箱|email|phone)", re.IGNORECASE),
)


class RemediationLoopError(RuntimeError):
    """Raised when resume hits the exact same unresolved evidence gap again."""


class PlanningLoopError(RuntimeError):
    """Raised when the same unresolved pre-run intake gap is surfaced again."""


def _make_id(index: int) -> str:
    return f"S-{index:03d}"


def _collect_files(screenshots_dir: Path) -> list[Path]:
    """Return all accepted files under *screenshots_dir*, recursively sorted."""
    if not screenshots_dir.exists():
        raise FileNotFoundError(f"screenshots_dir not found: {screenshots_dir}")
    if not screenshots_dir.is_dir():
        raise NotADirectoryError(f"screenshots_dir is not a directory: {screenshots_dir}")

    accepted = _IMAGE_EXTENSIONS | _DESCRIPTION_EXTENSIONS
    files = [
        path
        for path in screenshots_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in accepted
    ]
    return sorted(files, key=lambda p: p.relative_to(screenshots_dir).as_posix())


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _description_preview(path: Path) -> str | None:
    if path.suffix.lower() not in _DESCRIPTION_EXTENSIONS:
        return None
    raw = _read_text(path)
    return raw[:_DESCRIPTION_PREVIEW_CHARS] if raw else None


def _signal_warnings(relative_path: str, description_preview: str | None, ocr_text: str) -> list[str]:
    joined = "\n".join(filter(None, [relative_path, description_preview or "", ocr_text]))
    warnings: list[str] = []
    for pattern in _SENSITIVE_SIGNAL_PATTERNS:
        match = pattern.search(joined)
        if match:
            warnings.append(
                f"text signal matched '{match.group(0)}' via filename, markdown, or OCR"
            )
    return warnings


def _image_dimensions(path: Path) -> tuple[int | None, int | None]:
    suffix = path.suffix.lower()
    data = path.read_bytes()
    if suffix == ".png":
        return _png_dimensions(data)
    if suffix in {".jpg", ".jpeg"}:
        return _jpeg_dimensions(data)
    if suffix == ".gif":
        return _gif_dimensions(data)
    if suffix == ".bmp":
        return _bmp_dimensions(data)
    if suffix == ".webp":
        return _webp_dimensions(data)
    return (None, None)


def _png_dimensions(data: bytes) -> tuple[int | None, int | None]:
    if len(data) < 24 or not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return (None, None)
    return (struct.unpack(">I", data[16:20])[0], struct.unpack(">I", data[20:24])[0])


def _gif_dimensions(data: bytes) -> tuple[int | None, int | None]:
    if len(data) < 10 or not data.startswith((b"GIF87a", b"GIF89a")):
        return (None, None)
    return (struct.unpack("<H", data[6:8])[0], struct.unpack("<H", data[8:10])[0])


def _bmp_dimensions(data: bytes) -> tuple[int | None, int | None]:
    if len(data) < 26 or not data.startswith(b"BM"):
        return (None, None)
    return (struct.unpack("<I", data[18:22])[0], struct.unpack("<I", data[22:26])[0])


def _jpeg_dimensions(data: bytes) -> tuple[int | None, int | None]:
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return (None, None)
    idx = 2
    sof_markers = {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
    while idx + 9 < len(data):
        if data[idx] != 0xFF:
            idx += 1
            continue
        marker = data[idx + 1]
        idx += 2
        if marker in {0xD8, 0xD9}:
            continue
        if idx + 2 > len(data):
            break
        size = struct.unpack(">H", data[idx:idx + 2])[0]
        if size < 2 or idx + size > len(data):
            break
        if marker in sof_markers and idx + 7 < len(data):
            height = struct.unpack(">H", data[idx + 3:idx + 5])[0]
            width = struct.unpack(">H", data[idx + 5:idx + 7])[0]
            return (width, height)
        idx += size
    return (None, None)


def _webp_dimensions(data: bytes) -> tuple[int | None, int | None]:
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return (None, None)
    chunk = data[12:16]
    if chunk == b"VP8X" and len(data) >= 30:
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
        return (width, height)
    if chunk == b"VP8L" and len(data) >= 25:
        b0, b1, b2, b3 = data[21:25]
        width = 1 + (((b1 & 0x3F) << 8) | b0)
        height = 1 + (((b3 & 0x0F) << 10) | (b2 << 2) | ((b1 & 0xC0) >> 6))
        return (width, height)
    if chunk == b"VP8 " and len(data) >= 30:
        start = data.find(b"\x9d\x01\x2a")
        if start != -1 and start + 7 < len(data):
            width = struct.unpack("<H", data[start + 3:start + 5])[0] & 0x3FFF
            height = struct.unpack("<H", data[start + 5:start + 7])[0] & 0x3FFF
            return (width, height)
    return (None, None)


def _resolution(width: int | None, height: int | None) -> str | None:
    if width is None or height is None:
        return None
    return f"{width}x{height}"


def _quality_tier(width: int | None, height: int | None, *, kind: str) -> str:
    if kind == "description":
        return "not_applicable"
    if width is None or height is None:
        return "unknown"
    if width >= 1280 and height >= 720:
        return "high"
    if width >= 720 and height >= 480:
        return "medium"
    return "low"


def _normalized_tokens(text: str | None) -> list[str]:
    if not text:
        return []
    return [token.lower() for token in _TOKEN_PATTERN.findall(text)]


_NON_DEFAULT_STATE_HINT_TOKENS = {
    token
    for state, hints in _STATE_HINTS.items()
    if state != "default"
    for hint in hints
    for token in _normalized_tokens(hint)
}


def _token_overlap(left: Iterable[str], right: Iterable[str]) -> set[str]:
    return set(left) & set(right)


def _parse_task_checklist(task_checklist_lite: str | None) -> list[str]:
    if not task_checklist_lite:
        return []
    tasks: list[str] = []
    for raw_line in task_checklist_lite.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r"^[-*]\s*", "", line)
        line = re.sub(r"^\d+[\.\)]\s*", "", line)
        if len(line) < 2:
            continue
        tasks.append(line)
    return tasks


def _dedupe_preserve(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        cleaned = value.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        ordered.append(cleaned)
    return ordered


def _coerce_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []
    return []


def _coerce_int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return 0
        try:
            return int(float(cleaned))
        except ValueError:
            return 0
    return 0


def _coerce_float(value: Any) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return 0.0
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    return 0.0


def _mapping_guidance_actions() -> list[str]:
    return [
        "补 screens-description.md，说明页面名称、关键按钮、状态与流程",
        "如不想批量改文件名，可在 inputs/screens/ 补 screens-map.md 或 screens-index.md，写最小截图映射",
    ]


def _rename_accelerator_suggestion(paths: list[str]) -> str:
    preview = "；".join(paths[:4])
    return (
        "如你方便，可只为这些关键截图补更清晰命名以加速自动匹配："
        f"{preview}"
    )


def _extract_line_labels(text: str) -> list[str]:
    labels: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^#+\s*", "", line)
        line = re.sub(r"^[-*]\s*", "", line)
        line = re.sub(r"^\d+[\.\)]\s*", "", line)
        if 2 <= len(line) <= 40:
            labels.append(line)
    return labels


def _flatten_named_values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return _extract_line_labels(value)
    if isinstance(value, dict):
        labels: list[str] = []
        for key in ("name", "title", "label", "module", "feature", "stage"):
            raw = value.get(key)
            if isinstance(raw, str):
                labels.extend(_extract_line_labels(raw))
        for nested in value.values():
            labels.extend(_flatten_named_values(nested))
        return _dedupe_preserve(labels)
    if isinstance(value, list):
        labels: list[str] = []
        for item in value:
            labels.extend(_flatten_named_values(item))
        return _dedupe_preserve(labels)
    return []


def _page_key(label: str) -> str:
    tokens = _normalized_tokens(label)
    if tokens:
        return "-".join(tokens[:6])
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-") or "page"


def _infer_required_states(label: str) -> list[StateCategory]:
    lowered = label.lower()
    states: list[StateCategory] = ["default"]
    if any(token in lowered for token in ("登录", "login", "提交", "submit", "表单", "form", "保存", "save", "创建", "create", "导出", "export", "设置", "setting")):
        states.extend(["loading", "error", "success"])
    if any(token in lowered for token in ("首页", "home", "dashboard", "列表", "list", "报表", "report", "搜索", "search", "工作台")):
        states.extend(["loading", "empty"])
    return [state for state in ("default", "loading", "empty", "error", "success") if state in states]


def _requires_description(label: str, required_states: list[StateCategory]) -> bool:
    token_count = len(_normalized_tokens(label))
    return len(required_states) >= 3 or token_count <= 2


def _critical_path_priority(index: int, total: int) -> str:
    if total <= 1:
        return "P0"
    if total == 2:
        return "P0" if index == 0 else "P1"
    if index < min(2, total):
        return "P0"
    if index < min(4, total):
        return "P1"
    return "P2"


def _critical_path_match_score(
    label: str,
    page: EvidencePageRequirement,
) -> int:
    label_tokens = set(_normalized_tokens(label))
    if not label_tokens:
        return 0

    score = 0
    if label in page.task_refs:
        score += 8
    if label in page.journey_stage_refs:
        score += 6
    if label in page.module_refs:
        score += 5
    if label in page.feature_refs:
        score += 5

    page_tokens = set(page.match_tokens)
    score += len(label_tokens & page_tokens) * 3
    for refs in (page.task_refs, page.module_refs, page.feature_refs, page.journey_stage_refs):
        ref_tokens = {
            token
            for ref in refs
            for token in _normalized_tokens(ref)
        }
        score += len(label_tokens & ref_tokens)
    return score


def _build_critical_paths(
    *,
    tasks: list[str],
    journey_labels: list[str],
    page_requirements: list[EvidencePageRequirement],
) -> list[CriticalPathDefinition]:
    path_labels = _dedupe_preserve(tasks or journey_labels or [page.page_name for page in page_requirements])
    critical_paths: list[CriticalPathDefinition] = []

    for index, label in enumerate(path_labels):
        scored_pages = [
            (_critical_path_match_score(label, page), page)
            for page in page_requirements
        ]
        scored_pages = [
            (score, page)
            for score, page in scored_pages
            if score > 0
        ]
        scored_pages.sort(
            key=lambda item: (
                -item[0],
                page_requirements.index(item[1]),
                item[1].page_name,
            )
        )

        matched_pages = [page for _, page in scored_pages[:2]]
        if not matched_pages and page_requirements:
            fallback_index = min(index, len(page_requirements) - 1)
            matched_pages = [page_requirements[fallback_index]]

        required_pages = [page.page_name for page in matched_pages]
        required_states = _dedupe_preserve(
            f"{page.page_name}:{state}"
            for page in matched_pages
            for state in page.required_states
        )
        priority = _critical_path_priority(index, len(path_labels))
        critical_paths.append(
            CriticalPathDefinition(
                path_name=label,
                business_goal=label,
                priority=priority,  # type: ignore[arg-type]
                required_pages=required_pages,
                required_states=required_states,
                confidence="high" if priority in {"P0", "P1"} else "medium",
                source_channel="mixed",
                evidence_basis=[
                    f"matched_page_count={len(required_pages)}",
                    f"matched_state_count={len(required_states)}",
                    f"priority={priority}",
                ],
            )
        )
    return critical_paths


def _build_capture_mission(
    *,
    tasks: list[str],
    module_labels: list[str],
    feature_labels: list[str],
    journey_labels: list[str],
    page_requirements: list[EvidencePageRequirement],
) -> CaptureMission:
    critical_paths = _build_critical_paths(
        tasks=tasks,
        journey_labels=journey_labels,
        page_requirements=page_requirements,
    )
    critical_flows = _dedupe_preserve(tasks or journey_labels or [page.page_name for page in page_requirements])
    must_capture_pages = [page.page_name for page in page_requirements if page.requirement_level == "hard"]
    must_capture_states = _dedupe_preserve(
        f"{page.page_name}:{state}"
        for page in page_requirements
        for state in page.required_states
    )
    nice_to_have_pages = _dedupe_preserve(
        page.page_name
        for page in page_requirements
        if not page.task_refs and page.requirement_level != "hard"
    )
    if not nice_to_have_pages:
        mission_tokens = {token for page in must_capture_pages for token in _normalized_tokens(page)}
        nice_to_have_pages = [
            label
            for label in _dedupe_preserve(module_labels + feature_labels + journey_labels)
            if not set(_normalized_tokens(label)).issubset(mission_tokens)
        ][:4]

    capture_order = _dedupe_preserve([*must_capture_pages, *nice_to_have_pages])
    evidence_rationale: list[str] = []
    for page in page_requirements:
        drivers: list[str] = []
        if page.task_refs:
            drivers.append("任务: " + " / ".join(page.task_refs[:2]))
        if page.module_refs:
            drivers.append("模块: " + " / ".join(page.module_refs[:2]))
        if page.feature_refs:
            drivers.append("功能: " + " / ".join(page.feature_refs[:2]))
        if page.required_states:
            drivers.append("状态: " + ", ".join(page.required_states))
        evidence_rationale.append(f"{page.page_name}: {'；'.join(drivers)}")

    final_policy = CapturePassPolicy(
        min_image_count=5,
        min_readable_ratio=0.8,
        min_text_evidence_ratio=0.8,
        min_page_coverage_ratio=0.8,
        min_state_coverage_ratio=0.8,
        min_description_ratio_without_ocr=0.8,
        require_any_description_without_ocr=True,
        require_trusted_mapping=True,
    )
    fallback_policy = CapturePassPolicy(
        min_image_count=1,
        min_readable_ratio=0.6,
        min_text_evidence_ratio=0.6,
        min_page_coverage_ratio=0.5,
        min_state_coverage_ratio=0.4,
        min_description_ratio_without_ocr=0.0,
        require_any_description_without_ocr=True,
        require_trusted_mapping=False,
    )

    final_delivery_pass_line = [
        "至少 5 张可读截图，优先覆盖 must_capture_pages。",
        "must_capture_pages 覆盖率 >= 80%，must_capture_states 覆盖率 >= 80%。",
        "所有 P0/P1 critical path 必须过线；次要页面不能掩盖主链路缺口。",
        "无 OCR 时，关键页面说明覆盖率 >= 80%。",
        "关键 screenshot -> page/state 映射必须是 trusted（high confidence 或二次验证通过）。",
        "最终只在这条线满足时放行 final_delivery_ready。",
    ]
    fallback_pass_line = [
        "至少 1 张可读截图，并具备 OCR 或 markdown 说明支撑。",
        "must_capture_pages 覆盖率 >= 50%，must_capture_states 覆盖率 >= 40%。",
        "所有 P0 critical path 至少要过 fallback 线，否则只能 supplement_required / blocked。",
        "允许 provisional mapping 参与 bounded fallback，但不得抬高 final_delivery_ready。",
        "这条线只允许输出 bounded fallback package，不允许最终报告。",
    ]

    return CaptureMission(
        mission_version=_PLAN_VERSION,
        critical_flows=critical_flows,
        must_capture_pages=must_capture_pages,
        must_capture_states=must_capture_states,
        nice_to_have_pages=nice_to_have_pages,
        capture_order=capture_order,
        final_delivery_pass_line=final_delivery_pass_line,
        fallback_pass_line=fallback_pass_line,
        evidence_rationale=evidence_rationale,
        final_delivery_policy=final_policy,
        fallback_policy=fallback_policy,
        critical_paths=critical_paths,
        confidence="high",
        source_channel="mixed",
        evidence_basis=[
            f"critical_flow_count={len(critical_flows)}",
            f"must_capture_page_count={len(must_capture_pages)}",
            f"must_capture_state_count={len(must_capture_states)}",
            f"critical_path_count={len(critical_paths)}",
        ],
    )


def _render_capture_mission_markdown(
    *,
    mission: CaptureMission,
    guidance: EvidenceInputGuidance,
) -> str:
    lines = [
        "# Capture Mission",
        "",
        "这不是让你补一堆图，而是让你优先补最少量、最高价值的关键证据。",
        "",
        "## Critical flows",
    ]
    if mission.critical_flows:
        lines.extend(f"- {flow}" for flow in mission.critical_flows)
    else:
        lines.append("- 核心主流程")

    lines.extend(["", "## Must capture pages"])
    if mission.must_capture_pages:
        lines.extend(f"- {page}" for page in mission.must_capture_pages)
    else:
        lines.append("- 无")

    lines.extend(["", "## Must capture states"])
    if mission.must_capture_states:
        lines.extend(f"- {state}" for state in mission.must_capture_states)
    else:
        lines.append("- 无")

    lines.extend(["", "## Nice to have pages"])
    if mission.nice_to_have_pages:
        lines.extend(f"- {page}" for page in mission.nice_to_have_pages)
    else:
        lines.append("- 当前没有额外的 nice-to-have 页面。")

    lines.extend(["", "## Capture order"])
    if mission.capture_order:
        lines.extend(f"{idx}. {page}" for idx, page in enumerate(mission.capture_order, start=1))
    else:
        lines.append("1. 主流程关键页面")

    lines.extend(["", "## Critical paths"])
    if mission.critical_paths:
        for path in mission.critical_paths:
            pages = " / ".join(path.required_pages) if path.required_pages else "无"
            states = " / ".join(path.required_states[:6]) if path.required_states else "无"
            lines.append(f"- [{path.priority}] {path.path_name}: goal={path.business_goal}")
            lines.append(f"  - pages: {pages}")
            lines.append(f"  - states: {states}")
    else:
        lines.append("- 当前未生成 critical path。")

    lines.extend(["", "## Final delivery pass line"])
    lines.extend(f"- {line}" for line in mission.final_delivery_pass_line)

    lines.extend(["", "## Fallback pass line"])
    lines.extend(f"- {line}" for line in mission.fallback_pass_line)

    lines.extend(["", "## Evidence rationale"])
    lines.extend(f"- {line}" for line in mission.evidence_rationale)

    lines.extend(["", "## Current run status"])
    lines.append(f"- pre_run_status: {guidance.pre_run_status}")
    lines.append(f"- status_reason: {guidance.status_reason}")
    if guidance.required_actions:
        lines.append("- next actions:")
        lines.extend(f"  - {action}" for action in guidance.required_actions)
    else:
        lines.append("- next actions: 当前输入已满足 mission，不需要重复补料。")

    return "\n".join(lines).strip() + "\n"


def _build_required_evidence_plan(
    *,
    modules: Any,
    key_features: Any,
    task_checklist_lite: str | None,
    journey_map: Any,
    journey_stages: Any,
) -> RequiredEvidencePlan:
    tasks = _parse_task_checklist(task_checklist_lite)
    module_labels = _flatten_named_values(modules)
    feature_labels = _flatten_named_values(key_features)
    journey_labels = _flatten_named_values(journey_stages) + _flatten_named_values(journey_map)

    candidate_map: dict[str, dict[str, Any]] = {}

    def add_candidate(label: str, source: str, *, allow_new: bool = True) -> None:
        cleaned = label.strip()
        if len(cleaned) < 2:
            return
        key = _page_key(cleaned)
        if not allow_new and candidate_map:
            candidate_tokens = set(_normalized_tokens(cleaned))
            best_key: str | None = None
            best_score = 0
            for existing_key, existing in candidate_map.items():
                existing_tokens = set(_normalized_tokens(str(existing["page_name"])))
                score = len(candidate_tokens & existing_tokens)
                if score > best_score:
                    best_key = existing_key
                    best_score = score
            if best_key is not None and best_score >= 1:
                key = best_key
            else:
                return

        entry = candidate_map.setdefault(
            key,
            {
                "page_name": cleaned,
                "task_refs": [],
                "module_refs": [],
                "feature_refs": [],
                "journey_stage_refs": [],
            },
        )
        if source == "task":
            entry["task_refs"].append(cleaned)
        elif source == "module":
            entry["module_refs"].append(cleaned)
        elif source == "feature":
            entry["feature_refs"].append(cleaned)
        elif source == "journey":
            entry["journey_stage_refs"].append(cleaned)
        if len(cleaned) > len(str(entry["page_name"])):
            entry["page_name"] = cleaned

    for task in tasks:
        add_candidate(task, "task", allow_new=True)
    for module in module_labels:
        add_candidate(module, "module", allow_new=True)
    for feature in feature_labels:
        add_candidate(feature, "feature", allow_new=not candidate_map)
    for stage in journey_labels:
        add_candidate(stage, "journey", allow_new=not candidate_map)

    ordered_keys = list(candidate_map)
    if not ordered_keys:
        ordered_keys = [_page_key("核心主流程")]
        candidate_map[ordered_keys[0]] = {
            "page_name": "核心主流程",
            "task_refs": ["核心主流程"],
            "module_refs": [],
            "feature_refs": [],
            "journey_stage_refs": [],
        }

    page_requirements: list[EvidencePageRequirement] = []
    state_index: dict[str, dict[str, Any]] = {}
    for idx, key in enumerate(ordered_keys, start=1):
        meta = candidate_map[key]
        page_name = str(meta["page_name"])
        required_states = _infer_required_states(page_name)
        page_requirement = EvidencePageRequirement(
            page_key=f"PAGE-{idx:03d}",
            page_name=page_name,
            match_tokens=_dedupe_preserve(_normalized_tokens(page_name)),
            task_refs=_dedupe_preserve(meta["task_refs"]),
            module_refs=_dedupe_preserve(meta["module_refs"]),
            feature_refs=_dedupe_preserve(meta["feature_refs"]),
            journey_stage_refs=_dedupe_preserve(meta["journey_stage_refs"]),
            required_states=required_states,
            description_required=_requires_description(page_name, required_states),
            naming_hint=f"{page_name}-{{state}}.png",
            requirement_level="hard",
            rationale=(
                "Derived from task checklist / module / journey coverage and treated as critical for "
                "first-pass client evidence readiness."
            ),
            confidence="high" if meta["task_refs"] else "medium",
            source_channel="mixed",
            evidence_basis=[
                f"task_refs={len(meta['task_refs'])}",
                f"module_refs={len(meta['module_refs'])}",
                f"feature_refs={len(meta['feature_refs'])}",
                f"journey_stage_refs={len(meta['journey_stage_refs'])}",
            ],
        )
        page_requirements.append(page_requirement)
        for state in required_states:
            state_meta = state_index.setdefault(
                state,
                {"pages": [], "evidence_basis": [], "confidence": "medium"},
            )
            state_meta["pages"].append(page_requirement.page_key)
            state_meta["evidence_basis"].append(
                f"{page_requirement.page_name} requires state '{state}'"
            )
            if state in {"error", "success", "loading"}:
                state_meta["confidence"] = "high"

    state_requirements = [
        CriticalStateRequirement(
            state=state,  # type: ignore[arg-type]
            applies_to_pages=_dedupe_preserve(meta["pages"]),
            requirement_level="hard",
            rationale="Critical UI state coverage is required to avoid false final-delivery readiness.",
            confidence=meta["confidence"],  # type: ignore[arg-type]
            source_channel="mixed",
            evidence_basis=_dedupe_preserve(meta["evidence_basis"]),
        )
        for state, meta in state_index.items()
    ]
    capture_mission = _build_capture_mission(
        tasks=tasks,
        module_labels=module_labels,
        feature_labels=feature_labels,
        journey_labels=journey_labels,
        page_requirements=page_requirements,
    )

    return RequiredEvidencePlan(
        plan_version=_PLAN_VERSION,
        critical_page_count=len(page_requirements),
        critical_state_count=len(state_requirements),
        critical_pages=page_requirements,
        critical_states=state_requirements,
        hard_requirements=[
            "关键页面截图需覆盖任务清单对应的核心页面",
            "关键状态至少覆盖 default / loading / error / success / empty 中与页面相关的部分",
        ],
        recommended_descriptions=[
            page.page_name
            for page in page_requirements
            if page.description_required
        ],
        preferred_mapping_files=list(_LIGHTWEIGHT_MAPPING_FILES),
        naming_convention="Recommended accelerator only: {模块}-{页面}-{状态}.png",
        quality_targets={
            "final_delivery_ready": "99%-100%",
            "fallback_safe": "85%+",
        },
        capture_mission=capture_mission,
        confidence="high",
        source_channel="mixed",
        evidence_basis=[
            f"task_count={len(tasks)}",
            f"module_count={len(module_labels)}",
            f"feature_count={len(feature_labels)}",
            f"journey_label_count={len(journey_labels)}",
        ],
    )


def _ref_text_evidence(ref: ScreenshotRef) -> str:
    parts: list[str] = [ref.relative_path]
    if ref.description_preview:
        parts.append(ref.description_preview)
    if ref.ocr_text_preview:
        parts.append(ref.ocr_text_preview)
    cue_groups = (
        ref.page_title_candidates,
        ref.button_text_candidates,
        ref.navigation_text_candidates,
        ref.state_text_candidates,
    )
    for group in cue_groups:
        parts.extend(cue.value for cue in group)
    return "\n".join(part for part in parts if part)


def _task_coverage_summary(
    image_refs: list[ScreenshotRef],
    task_checklist_lite: str | None,
) -> dict[str, Any]:
    tasks = _parse_task_checklist(task_checklist_lite)
    if not tasks:
        return {
            "task_count": 0,
            "matched_task_count": 0,
            "key_task_coverage_ratio": None,
            "matched_tasks": [],
            "missing_tasks": [],
        }

    evidence_blob = "\n".join(_ref_text_evidence(ref).lower() for ref in image_refs)
    evidence_tokens = set(_normalized_tokens(evidence_blob))
    matched_tasks: list[str] = []
    missing_tasks: list[str] = []
    for task in tasks:
        task_tokens = [token for token in _normalized_tokens(task) if len(token) >= 2]
        matched = False
        if task_tokens:
            matched = any(token in evidence_blob or token in evidence_tokens for token in task_tokens)
        else:
            matched = task.lower() in evidence_blob
        if matched:
            matched_tasks.append(task)
        else:
            missing_tasks.append(task)

    coverage_ratio = len(matched_tasks) / len(tasks) if tasks else None
    return {
        "task_count": len(tasks),
        "matched_task_count": len(matched_tasks),
        "key_task_coverage_ratio": coverage_ratio,
        "matched_tasks": matched_tasks,
        "missing_tasks": missing_tasks,
    }


def _match_tasks_for_ref(ref: ScreenshotRef, task_checklist_lite: str | None) -> list[str]:
    tasks = _parse_task_checklist(task_checklist_lite)
    if not tasks:
        return []

    evidence_blob = _ref_text_evidence(ref).lower()
    evidence_tokens = set(_normalized_tokens(evidence_blob))
    matched: list[str] = []
    for task in tasks:
        task_tokens = [token for token in _normalized_tokens(task) if len(token) >= 2]
        if task_tokens:
            if any(token in evidence_blob or token in evidence_tokens for token in task_tokens):
                matched.append(task)
        elif task.lower() in evidence_blob:
            matched.append(task)
    return matched


def _markdown_sections(text: str, source_path: str) -> list[dict[str, str]]:
    stripped = text.strip()
    if not stripped:
        return []

    sections: list[dict[str, str]] = []
    current_title = Path(source_path).stem.replace("_", " ").replace("-", " ").strip() or source_path
    current_lines: list[str] = []

    def flush() -> None:
        body = "\n".join(line for line in current_lines if line.strip()).strip()
        if body:
            sections.append({"title": current_title, "body": body, "source_path": source_path})

    for raw_line in stripped.splitlines():
        line = raw_line.rstrip()
        if line.lstrip().startswith("#"):
            flush()
            current_title = line.lstrip().lstrip("#").strip() or current_title
            current_lines = []
            continue
        current_lines.append(line)
    flush()
    if sections:
        return sections
    return [{"title": current_title, "body": stripped, "source_path": source_path}]


def _section_cue_text(section: dict[str, str]) -> str:
    title = section["title"].strip()
    body = section["body"].strip()
    title_suffix = Path(title).suffix.lower()
    title_looks_like_file = title_suffix in (_IMAGE_EXTENSIONS | _DESCRIPTION_EXTENSIONS)
    title_looks_like_generated_id = title.lower().startswith("img") and any(ch.isdigit() for ch in title)
    if title_looks_like_file or title_looks_like_generated_id:
        return body or title
    return "\n".join(part for part in (title, body) if part).strip()


def _ref_tokens(ref: ScreenshotRef) -> set[str]:
    tokens: set[str] = set(_normalized_tokens(ref.relative_path))
    if ref.ocr_text_preview:
        tokens.update(_normalized_tokens(ref.ocr_text_preview))
    cue_groups = (
        ref.page_title_candidates,
        ref.button_text_candidates,
        ref.navigation_text_candidates,
        ref.state_text_candidates,
    )
    for group in cue_groups:
        for cue in group:
            tokens.update(_normalized_tokens(cue.value))
    return tokens


def _coerce_required_evidence_plan(
    required_evidence_plan: RequiredEvidencePlan | dict[str, Any] | None,
) -> RequiredEvidencePlan | None:
    if required_evidence_plan is None:
        return None
    if isinstance(required_evidence_plan, RequiredEvidencePlan):
        return required_evidence_plan
    try:
        return RequiredEvidencePlan.model_validate(required_evidence_plan)
    except Exception:
        return None


def _page_requirement_by_key(
    plan: RequiredEvidencePlan,
    page_key: str,
) -> EvidencePageRequirement | None:
    for requirement in plan.critical_pages:
        if requirement.page_key == page_key:
            return requirement
    return None


def _page_requirement_by_name(
    plan: RequiredEvidencePlan,
    page_name: str,
) -> EvidencePageRequirement | None:
    normalized_key = _page_key(page_name)
    for requirement in plan.critical_pages:
        if requirement.page_name == page_name or requirement.page_key == normalized_key:
            return requirement
    best_match: EvidencePageRequirement | None = None
    best_score = 0
    target_tokens = set(_normalized_tokens(page_name))
    for requirement in plan.critical_pages:
        score = len(target_tokens & set(requirement.match_tokens))
        if score > best_score:
            best_match = requirement
            best_score = score
    return best_match if best_score >= 1 else None


def _normalize_state_label(raw: str) -> StateCategory | None:
    normalized = raw.strip().lower()
    if not normalized:
        return None
    aliases: dict[str, StateCategory] = {
        "default": "default",
        "默认": "default",
        "默认态": "default",
        "success": "success",
        "成功": "success",
        "成功态": "success",
        "error": "error",
        "错误": "error",
        "错误态": "error",
        "loading": "loading",
        "加载": "loading",
        "加载态": "loading",
        "loading state": "loading",
        "empty": "empty",
        "空": "empty",
        "空状态": "empty",
        "empty state": "empty",
    }
    if normalized in aliases:
        return aliases[normalized]
    for state, hints in _STATE_HINTS.items():
        if normalized == state or any(hint.lower() == normalized for hint in hints):
            return state  # type: ignore[return-value]
    return None


def _mapping_override_key(relative_path: str) -> str:
    return relative_path.replace("\\", "/").strip().lower()


def _parse_mapping_overrides(
    refs: list[ScreenshotRef],
    *,
    plan: RequiredEvidencePlan,
) -> dict[str, dict[str, Any]]:
    overrides: dict[str, dict[str, Any]] = {}
    pattern = re.compile(
        r"^\s*[-*]\s*(?P<ref>[^-].*?)\s*->\s*page\s*=\s*(?P<page>[^;]+?)"
        r"(?:\s*;\s*states\s*=\s*(?P<states>.+))?\s*$"
    )
    for ref in refs:
        if ref.kind != "description":
            continue
        if Path(ref.relative_path).name not in _LIGHTWEIGHT_MAPPING_FILES:
            continue
        text = _read_text(Path(ref.path))
        for line in text.splitlines():
            match = pattern.match(line)
            if match is None:
                continue
            page_name = match.group("page").strip()
            requirement = _page_requirement_by_name(plan, page_name)
            if requirement is None:
                continue
            states_blob = match.group("states") or ""
            parsed_states = _dedupe_preserve(
                state
                for state in (
                    _normalize_state_label(part)
                    for part in re.split(r"[,/|]", states_blob)
                )
                if state is not None
            )
            relative_path = match.group("ref").strip().strip("`")
            override = {
                "page_key": requirement.page_key,
                "page_name": requirement.page_name,
                "states": parsed_states,
                "source_path": ref.relative_path,
                "evidence_basis": [
                    f"manual clarification mapping from {ref.relative_path}",
                    f"confirmed page={requirement.page_name}",
                    *([f"confirmed states={','.join(parsed_states)}"] if parsed_states else []),
                ],
            }
            overrides[_mapping_override_key(relative_path)] = override
            overrides[_mapping_override_key(Path(relative_path).name)] = override
    return overrides


def _clarification_priority_rank(label: str) -> int:
    if label.startswith("[P0]"):
        return 0
    if label.startswith("[P1]"):
        return 1
    if label.startswith("[P2]"):
        return 2
    return 3


def _clarification_confirmation_prompt(
    *,
    relative_path: str,
    candidate_pages: list[str],
    candidate_states: list[StateCategory],
) -> str:
    pages = " / ".join(candidate_pages[:3]) if candidate_pages else "正确页面"
    states = " / ".join(candidate_states[:3]) if candidate_states else "当前状态"
    return f"请只确认 `{relative_path}` 更接近哪个页面与状态：页面候选 `{pages}`；状态候选 `{states}`。"


def _clarification_signature(items: list[ClarificationItem]) -> str:
    payload = [
        {
            "screenshot_ref": item.screenshot_ref,
            "candidate_pages": item.candidate_pages,
            "candidate_states": item.candidate_states,
            "affected_critical_paths": item.affected_critical_paths,
            "unlocks_final_delivery": item.unlocks_final_delivery,
        }
        for item in items
    ]
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _clarification_sort_key(item: ClarificationItem) -> tuple[int, int, int, str]:
    priority_rank = min(
        (_clarification_priority_rank(label) for label in item.affected_critical_paths),
        default=3,
    )
    return (
        0 if item.unlocks_final_delivery else 1,
        priority_rank,
        len(item.candidate_pages),
        item.relative_path,
    )


def _select_clarification_items(
    *,
    clarification_items: list[ClarificationItem],
    missing_pages: list[str],
    missing_states: list[str],
    missing_descriptions: list[str],
    blocking_reasons: list[str] | None = None,
) -> tuple[list[ClarificationItem], str | None]:
    if not clarification_items:
        return [], None

    sorted_items = sorted(clarification_items, key=_clarification_sort_key)
    relevant_items = [
        item
        for item in sorted_items
        if item.unlocks_final_delivery or item.affected_critical_paths
    ] or sorted_items

    candidate_pages = {
        page
        for item in relevant_items
        for page in item.candidate_pages
    }
    candidate_states = {
        f"{page}:{state}"
        for item in relevant_items
        for page in item.candidate_pages
        for state in item.candidate_states
    }
    unresolved_pages = [page for page in missing_pages if page not in candidate_pages]
    unresolved_descriptions = [page for page in missing_descriptions if page not in candidate_pages]
    unresolved_states = [
        state
        for state in missing_states
        if state not in candidate_states and state.rsplit(":", 1)[0] not in candidate_pages
    ]

    if blocking_reasons:
        return [], "clarification suppressed because the run is still blocked by broader evidence gaps"
    if unresolved_pages:
        return [], "clarification suppressed because some critical pages are still entirely missing"
    if unresolved_descriptions:
        return [], "clarification suppressed because some critical pages still lack description evidence"
    if len(unresolved_states) > 2:
        return [], "clarification suppressed because too many state-level gaps remain"
    if len(relevant_items) > _MAX_CLARIFICATION_ITEMS:
        return [], "clarification suppressed because ambiguity is too widespread for a bounded package"

    return relevant_items[:_MAX_CLARIFICATION_ITEMS], None


def _channel_token_groups(ref: ScreenshotRef) -> dict[str, set[str]]:
    cue_groups = (
        ref.page_title_candidates,
        ref.button_text_candidates,
        ref.navigation_text_candidates,
        ref.state_text_candidates,
    )
    grouped = {
        "ocr": set(_normalized_tokens(ref.ocr_text_preview)),
        "markdown": set(),
        "metadata": set(Path(ref.relative_path).parent.as_posix().replace("/", " ").split()),
        "filename": set(_normalized_tokens(Path(ref.relative_path).stem)),
    }
    for group in cue_groups:
        for cue in group:
            grouped.setdefault(cue.source_channel, set()).update(_normalized_tokens(cue.value))
    return grouped


def _mapping_candidate_details(
    requirement: EvidencePageRequirement,
    ref: ScreenshotRef,
) -> dict[str, Any]:
    page_tokens = set(requirement.match_tokens)
    channel_tokens = _channel_token_groups(ref)
    weights = {"ocr": 7, "markdown": 5, "mixed": 4, "metadata": 3, "filename": 2}
    source_scores: dict[str, int] = {key: 0 for key in weights}
    basis: list[str] = []
    observed_states = _state_categories_for_ref(ref)
    matched_required_states: list[StateCategory] = [
        state
        for state in requirement.required_states
        if state in observed_states and state != "default"
    ]
    state_signal_channels = _state_signal_channels_for_ref(ref)
    state_categories_by_channel = _state_categories_by_channel_for_ref(ref)

    supporting_channels: list[str] = []
    exact_channels: list[str] = []

    for channel in ("ocr", "markdown", "mixed", "metadata", "filename"):
        overlap = page_tokens & channel_tokens.get(channel, set())
        if not overlap:
            continue
        score = weights[channel] + len(overlap)
        source_scores[channel] += score
        supporting_channels.append(channel)
        basis.append(f"{channel} overlap with page '{requirement.page_name}': {sorted(overlap)}")

    exact_channel_blobs = {
        "ocr": " ".join(cue.value for cue in ref.ocr_text_lines).lower(),
        "markdown": " ".join(
            cue.value
            for group in (
                ref.page_title_candidates,
                ref.button_text_candidates,
                ref.navigation_text_candidates,
                ref.state_text_candidates,
            )
            for cue in group
            if cue.source_channel == "markdown"
        ).lower(),
        "mixed": " ".join(
            cue.value
            for group in (
                ref.page_title_candidates,
                ref.button_text_candidates,
                ref.navigation_text_candidates,
                ref.state_text_candidates,
            )
            for cue in group
            if cue.source_channel == "mixed"
        ).lower(),
        "metadata": Path(ref.relative_path).parent.as_posix().lower(),
        "filename": Path(ref.relative_path).stem.lower(),
    }
    for channel, blob in exact_channel_blobs.items():
        if requirement.page_name.lower() and requirement.page_name.lower() in blob:
            source_scores[channel] += weights[channel] + 2
            exact_channels.append(channel)
            if channel not in supporting_channels:
                supporting_channels.append(channel)
            basis.append(f"{channel} explicitly mentions page name '{requirement.page_name}'")
        elif requirement.page_key.lower() in blob:
            source_scores[channel] += weights[channel]
            if channel not in supporting_channels:
                supporting_channels.append(channel)
            basis.append(f"{channel} explicitly mentions page key '{requirement.page_key}'")

    if "ocr" in supporting_channels and "markdown" in supporting_channels:
        source_scores["ocr"] += 2
        source_scores["markdown"] += 2
        basis.append("ocr + markdown agree on the same planned page")
    if any(link.confidence == "high" for link in ref.description_links) and "markdown" in supporting_channels:
        source_scores["markdown"] += 2
        basis.append("high-confidence markdown description link reinforces the page mapping")
    if "metadata" in supporting_channels and "filename" in supporting_channels:
        source_scores["metadata"] += 1
        source_scores["filename"] += 1
        basis.append("directory structure and filename jointly support the page mapping")

    matched_state_channels: list[str] = []
    for state in matched_required_states:
        channels = sorted(state_signal_channels.get(state, set()))
        if not channels:
            continue
        matched_state_channels.extend(channels)
        for channel in channels:
            normalized_channel = channel if channel in weights else "metadata"
            bonus = {"ocr": 4, "markdown": 4, "mixed": 3, "filename": 2, "metadata": 1}.get(
                normalized_channel,
                1,
            )
            source_scores[normalized_channel] += bonus
        if len(channels) >= 2:
            for channel in channels:
                normalized_channel = channel if channel in weights else "metadata"
                source_scores[normalized_channel] += 1
        basis.append(
            "state-specific evidence matches required state "
            f"'{state}' for page '{requirement.page_name}' via {', '.join(channels)}"
        )
        if state in {"success", "error", "empty", "loading"}:
            basis.append(
                f"critical non-default state '{state}' adds page-disambiguation value"
            )

    total_score = sum(source_scores.values())
    dominant_channel = max(
        source_scores.items(),
        key=lambda item: (item[1], {"ocr": 5, "markdown": 4, "mixed": 3, "metadata": 2, "filename": 1}[item[0]]),
    )[0]
    return {
        "requirement": requirement,
        "score": total_score,
        "source_scores": source_scores,
        "source_channel": dominant_channel,
        "supporting_channels": _dedupe_preserve(supporting_channels),
        "exact_channels": _dedupe_preserve(exact_channels),
        "matched_required_states": matched_required_states,
        "state_signal_channels": _dedupe_preserve(matched_state_channels),
        "state_categories_by_channel": {
            channel: sorted(states)
            for channel, states in state_categories_by_channel.items()
        },
        "evidence_basis": basis,
    }


def _channel_leaders(
    candidates: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    leaders: dict[str, dict[str, Any]] = {}
    minimum_scores = {"ocr": 7, "markdown": 6, "metadata": 4, "filename": 3}
    for channel in ("ocr", "markdown", "metadata", "filename"):
        ranked = [
            candidate
            for candidate in candidates
            if int(candidate["source_scores"].get(channel, 0)) >= minimum_scores[channel]
        ]
        if not ranked:
            continue
        ranked.sort(
            key=lambda item: (
                -int(item["source_scores"].get(channel, 0)),
                -int(item["score"]),
                item["requirement"].page_key,
            )
        )
        leaders[channel] = ranked[0]
    return leaders


def _fusion_verdict_for_candidate(
    *,
    best: dict[str, Any],
    runner_up: dict[str, Any] | None,
    channel_leaders: dict[str, dict[str, Any]],
) -> tuple[str, bool, str | None, str | None, list[str], list[str], int]:
    best_page = str(best["requirement"].page_name)
    best_score = int(best["score"])
    runner_score = int(runner_up["score"]) if runner_up is not None else 0
    delta = best_score - runner_score if runner_up is not None else best_score
    supporting_channels = [str(channel) for channel in best.get("supporting_channels", [])]
    exact_channels = [str(channel) for channel in best.get("exact_channels", [])]
    conflict_pages: list[str] = []
    dominant_channels: list[str] = []

    ocr_leader = channel_leaders.get("ocr")
    markdown_leader = channel_leaders.get("markdown")
    if (
        ocr_leader is not None
        and markdown_leader is not None
        and ocr_leader["requirement"].page_key != markdown_leader["requirement"].page_key
    ):
        conflict_pages = _dedupe_preserve(
            [
                str(ocr_leader["requirement"].page_name),
                str(markdown_leader["requirement"].page_name),
            ]
        )
        dominant_channels = ["ocr", "markdown"]
        return (
            "conflicting",
            True,
            "OCR 和 markdown 分别强指向不同页面，当前不能视为 trusted mapping",
            "conflicting semantic evidence blocks final delivery eligibility",
            conflict_pages,
            dominant_channels,
            delta,
        )

    if runner_up is not None:
        runner_channels = [str(channel) for channel in runner_up.get("supporting_channels", [])]
        if (
            delta <= 2
            and (
                "ocr" in supporting_channels
                or "markdown" in supporting_channels
                or "ocr" in runner_channels
                or "markdown" in runner_channels
            )
        ):
            conflict_pages = _dedupe_preserve(
                [
                    best_page,
                    str(runner_up["requirement"].page_name),
                ]
            )
            dominant_channels = _dedupe_preserve(
                [
                    *[channel for channel in supporting_channels if channel in {"ocr", "markdown"}],
                    *[channel for channel in runner_channels if channel in {"ocr", "markdown"}],
                ]
            )
            return (
                "conflicting" if dominant_channels else "ambiguous",
                True,
                "多个候选页面在高价值证据上仍然过于接近，需要最小确认",
                "competing page candidates remain too close to count as trusted",
                conflict_pages,
                dominant_channels,
                delta,
            )

    semantic_support = [channel for channel in supporting_channels if channel in {"ocr", "markdown"}]
    independent_support_count = len(supporting_channels)
    exact_support_count = len(exact_channels)
    best_state_matches = [str(state) for state in best.get("matched_required_states", [])]
    runner_state_matches = (
        [str(state) for state in runner_up.get("matched_required_states", [])]
        if runner_up is not None
        else []
    )
    state_signal_channels = [
        str(channel)
        for channel in best.get("state_signal_channels", [])
        if str(channel) in {"ocr", "markdown", "filename", "metadata"}
    ]
    state_categories_by_channel = {
        str(channel): {
            str(state)
            for state in states
            if str(state) != "default"
        }
        for channel, states in dict(best.get("state_categories_by_channel", {})).items()
    }
    ocr_states = state_categories_by_channel.get("ocr", set())
    markdown_states = state_categories_by_channel.get("markdown", set())
    semantic_state_support = [
        channel for channel in state_signal_channels if channel in {"ocr", "markdown"}
    ]

    if (
        ocr_states
        and markdown_states
        and ocr_states.isdisjoint(markdown_states)
    ):
        return (
            "conflicting",
            True,
            "OCR 和 markdown 在同一截图上指向了不同关键状态，当前不能视为 trusted mapping",
            "conflicting state evidence blocks final delivery eligibility",
            conflict_pages or [best_page],
            _dedupe_preserve([*supporting_channels, "ocr", "markdown"]),
            delta,
        )

    runner_exact_channels = (
        [str(channel) for channel in runner_up.get("exact_channels", [])]
        if runner_up is not None
        else []
    )
    if (
        runner_up is not None
        and set(exact_channels) & {"markdown", "mixed"}
        and set(runner_exact_channels) & {"markdown", "mixed"}
        and delta <= 6
    ):
        return (
            "ambiguous",
            True,
            "同一张截图里的 markdown/derived cues 仍同时指向多个候选页面，先做一次最小确认更安全",
            "multiple page candidates remain explicitly named in the current evidence bundle",
            _dedupe_preserve([best_page, str(runner_up["requirement"].page_name)]),
            _dedupe_preserve([*supporting_channels, *runner_exact_channels]),
            delta,
        )

    if (
        best_state_matches
        and len(best_state_matches) > len(runner_state_matches)
        and semantic_state_support
        and best_score >= 8
        and delta >= 1
        and (independent_support_count >= 1 or exact_support_count >= 1)
    ):
        return (
            "trusted",
            False,
            None,
            "state-specific OCR/markdown evidence uniquely matches this critical page, so the mapping can count toward trusted final coverage",
            [],
            _dedupe_preserve([*supporting_channels, *semantic_state_support]),
            delta,
        )

    if (
        best_state_matches
        and semantic_state_support
        and "mixed" in exact_channels
        and best_score >= 10
        and delta >= 4
    ):
        return (
            "trusted",
            False,
            None,
            "OCR/markdown state evidence plus remediation-verified page cues are strong enough to count toward trusted final coverage",
            [],
            _dedupe_preserve([*supporting_channels, "mixed", *semantic_state_support]),
            delta,
        )

    if (
        "ocr" in semantic_support
        and "markdown" in semantic_support
        and best_score >= 12
        and delta >= 2
    ):
        return (
            "trusted",
            False,
            None,
            "OCR 和 markdown 一致支持同一页面，可计入 trusted mapping",
            [],
            semantic_support,
            delta,
        )
    if (
        semantic_support
        and independent_support_count >= 3
        and exact_support_count >= 1
        and best_score >= 12
        and delta >= 2
    ):
        return (
            "trusted",
            False,
            None,
            "强语义证据叠加独立辅助信号，可计入 trusted mapping",
            [],
            supporting_channels,
            delta,
        )
    if (
        semantic_support
        and independent_support_count >= 2
        and best_score >= 10
        and delta >= 3
    ):
        return (
            "trusted",
            False,
            None,
            "高价值语义证据与独立辅助信号一致，可计入 trusted mapping",
            [],
            supporting_channels,
            delta,
        )
    if (
        "markdown" in semantic_support
        and best_score >= 9
        and exact_support_count >= 1
        and delta >= 3
    ):
        return (
            "trusted",
            False,
            None,
            "高质量 markdown 说明已强指向同一页面，可计入 trusted mapping",
            [],
            supporting_channels,
            delta,
        )
    if best_score >= 5:
        return (
            "provisional",
            False,
            None,
            "现有证据足以服务 fallback/remediation，但还不能视为 trusted mapping",
            [],
            supporting_channels,
            delta,
        )
    return (
        "ambiguous",
        True,
        "当前 page/state 线索仍然偏弱，只建议做最小澄清",
        "weak evidence cannot yet establish a trusted mapping",
        [],
        supporting_channels,
        delta,
    )


def _draft_mapping_for_ref(
    ref: ScreenshotRef,
    *,
    plan: RequiredEvidencePlan | None,
    manual_overrides: dict[str, dict[str, Any]] | None = None,
) -> DraftScreenshotMapping | None:
    if plan is None:
        return None

    override = None
    if manual_overrides:
        override = manual_overrides.get(_mapping_override_key(ref.relative_path)) or manual_overrides.get(
            _mapping_override_key(Path(ref.relative_path).name)
        )
    if override is not None:
        matched_states = sorted(
            _dedupe_preserve(
                override.get("states")
                or _state_categories_for_ref(ref)
                or ["default"]
            )
        )
        return DraftScreenshotMapping(
            page_key=str(override["page_key"]),
            page_name=str(override["page_name"]),
            matched_states=matched_states,  # type: ignore[arg-type]
            candidate_pages=[str(override["page_name"])],
            clarification_needed=False,
            confidence="high",
            source_channel="markdown",
            evidence_basis=list(override.get("evidence_basis", [])),
            unsupported=["no full semantic scene understanding"],
            verification_gaps=[],
            mapping_verdict="trusted",
            fusion_score=99,
            supporting_channels=["markdown"],
            conflicting_candidates=[],
            final_delivery_eligible=True,
            final_delivery_reason="user-confirmed clarification mapping can count toward trusted final coverage",
        )

    candidates = [
        _mapping_candidate_details(requirement, ref)
        for requirement in plan.critical_pages
    ]
    candidates = [candidate for candidate in candidates if candidate["score"] > 0]
    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (
            -int(item["score"]),
            -int(item["source_scores"].get("ocr", 0)),
            -int(item["source_scores"].get("markdown", 0)),
            item["requirement"].page_key,
        )
    )
    best = candidates[0]
    runner_up = candidates[1] if len(candidates) > 1 else None
    dominant_channel = str(best["source_channel"])
    candidate_pages = [str(item["requirement"].page_name) for item in candidates[:3]]
    matched_states = sorted(_state_categories_for_ref(ref))
    channel_leaders = _channel_leaders(candidates)
    (
        mapping_verdict,
        clarification_needed,
        clarification_reason,
        final_delivery_reason,
        conflicting_candidates,
        dominant_channels,
        delta,
    ) = _fusion_verdict_for_candidate(
        best=best,
        runner_up=runner_up,
        channel_leaders=channel_leaders,
    )
    verification_gaps: list[str] = []
    if clarification_needed:
        verification_gaps.append("confirm page/state mapping only for this ambiguous screenshot")
    if mapping_verdict == "provisional":
        verification_gaps.append("mapping is currently provisional and cannot count toward final delivery")
    if mapping_verdict == "conflicting":
        verification_gaps.append("multi-source conflict detected; do not count this mapping as trusted")

    confidence = "low"
    if mapping_verdict in {"ambiguous", "conflicting"}:
        confidence = "low"
    elif mapping_verdict == "trusted":
        confidence = "high"
    elif mapping_verdict == "provisional":
        confidence = "medium"
    elif int(best["score"]) >= 5:
        confidence = "medium"

    draft_mapping = DraftScreenshotMapping(
        page_key=best["requirement"].page_key,
        page_name=best["requirement"].page_name,
        matched_states=matched_states,
        candidate_pages=candidate_pages,
        clarification_needed=clarification_needed,
        clarification_reason=clarification_reason,
        confidence=confidence,  # type: ignore[arg-type]
        source_channel=(
            "mixed"
            if len(dominant_channels or best.get("supporting_channels", [])) >= 2
            else dominant_channel
        ),  # type: ignore[arg-type]
        evidence_basis=list(best["evidence_basis"]),
        unsupported=["no full semantic scene understanding"],
        unknown=[] if not clarification_needed else ["exact page mapping still needs light confirmation"],
        verification_gaps=verification_gaps,
        mapping_verdict=mapping_verdict,  # type: ignore[arg-type]
        fusion_score=int(best["score"]),
        supporting_channels=[
            channel  # type: ignore[list-item]
            for channel in _dedupe_preserve(
                [*dominant_channels, *[str(channel) for channel in best.get("supporting_channels", [])]]
            )
        ],
        conflicting_candidates=_dedupe_preserve(conflicting_candidates),
    )
    return draft_mapping.model_copy(
        update={
            "final_delivery_eligible": mapping_verdict == "trusted",
            "final_delivery_reason": final_delivery_reason,
        }
    )


def _apply_draft_mappings(
    refs: list[ScreenshotRef],
    *,
    plan: RequiredEvidencePlan | None,
) -> tuple[list[ScreenshotRef], list[ClarificationItem]]:
    if plan is None:
        return refs, []

    manual_overrides = _parse_mapping_overrides(refs, plan=plan)
    updated_refs: list[ScreenshotRef] = list(refs)
    clarification_items: list[ClarificationItem] = []
    for idx, ref in enumerate(updated_refs):
        if ref.kind != "image":
            continue
        draft_mapping = _draft_mapping_for_ref(
            ref,
            plan=plan,
            manual_overrides=manual_overrides,
        )
        if draft_mapping is None:
            continue
        updated_refs[idx] = ref.model_copy(update={"draft_mapping": draft_mapping})
        if draft_mapping.clarification_needed:
            clarification_item = _clarification_from_ref(
                ref.model_copy(update={"draft_mapping": draft_mapping}),
                plan=plan,
            )
            if clarification_item is not None:
                clarification_items.append(clarification_item)
    return updated_refs, clarification_items


def _clarification_from_ref(
    ref: ScreenshotRef,
    *,
    plan: RequiredEvidencePlan | None,
) -> ClarificationItem | None:
    draft_mapping = ref.draft_mapping
    if draft_mapping is None or not draft_mapping.clarification_needed:
        return None
    candidate_pages = draft_mapping.candidate_pages[:3]
    affected_critical_paths: list[str] = []
    unlocks_final_delivery = False
    if plan is not None:
        for path in plan.capture_mission.critical_paths:
            if any(page in path.required_pages for page in candidate_pages):
                label = f"[{path.priority}] {path.path_name}"
                affected_critical_paths.append(label)
                if path.priority in {"P0", "P1"}:
                    unlocks_final_delivery = True
    return ClarificationItem(
        screenshot_id=ref.id,
        screenshot_ref=ref.relative_path,
        relative_path=ref.relative_path,
        candidate_pages=candidate_pages,
        candidate_states=draft_mapping.matched_states,
        ambiguity_reason=draft_mapping.clarification_reason
        or "mapping confidence is still too low to auto-confirm",
        affected_critical_paths=_dedupe_preserve(affected_critical_paths),
        unlocks_final_delivery=unlocks_final_delivery,
        confirmation_prompt=_clarification_confirmation_prompt(
            relative_path=ref.relative_path,
            candidate_pages=candidate_pages,
            candidate_states=draft_mapping.matched_states,
        ),
        confidence=draft_mapping.confidence,
        source_channel=draft_mapping.source_channel,
        evidence_basis=draft_mapping.evidence_basis,
        unsupported=draft_mapping.unsupported,
        unknown=draft_mapping.unknown,
        verification_gaps=draft_mapping.verification_gaps,
    )


def _build_evidence_fusion_summary(
    image_refs: list[ScreenshotRef],
) -> EvidenceFusionSummary:
    trusted_page_mappings: list[PageFusionRecord] = []
    trusted_state_mappings: list[StateFusionRecord] = []
    provisional_mappings: list[PageFusionRecord] = []
    conflicting_groups: list[ConflictingEvidenceGroup] = []
    unresolved_ambiguities: list[ClarificationItem] = []

    for ref in image_refs:
        draft_mapping = ref.draft_mapping
        if draft_mapping is None:
            continue
        record = PageFusionRecord(
            screenshot_id=ref.id,
            relative_path=ref.relative_path,
            page_key=draft_mapping.page_key,
            page_name=draft_mapping.page_name,
            matched_states=draft_mapping.matched_states,
            mapping_verdict=draft_mapping.mapping_verdict,
            fusion_score=draft_mapping.fusion_score,
            supporting_channels=draft_mapping.supporting_channels,
            candidate_pages=draft_mapping.candidate_pages,
            final_delivery_eligible=draft_mapping.final_delivery_eligible,
            confidence=draft_mapping.confidence,
            source_channel=draft_mapping.source_channel,
            evidence_basis=draft_mapping.evidence_basis,
            unsupported=draft_mapping.unsupported,
            unknown=draft_mapping.unknown,
            verification_gaps=draft_mapping.verification_gaps,
        )
        if draft_mapping.final_delivery_eligible:
            trusted_page_mappings.append(record)
            for state in draft_mapping.matched_states:
                trusted_state_mappings.append(
                    StateFusionRecord(
                        screenshot_id=ref.id,
                        relative_path=ref.relative_path,
                        page_key=draft_mapping.page_key,
                        page_name=draft_mapping.page_name,
                        state=state,
                        mapping_verdict=draft_mapping.mapping_verdict,
                        confidence=draft_mapping.confidence,
                        source_channel=draft_mapping.source_channel,
                        evidence_basis=draft_mapping.evidence_basis,
                        unsupported=draft_mapping.unsupported,
                        unknown=draft_mapping.unknown,
                        verification_gaps=draft_mapping.verification_gaps,
                    )
                )
        else:
            provisional_mappings.append(record)

        if draft_mapping.mapping_verdict == "conflicting":
            conflicting_groups.append(
                ConflictingEvidenceGroup(
                    screenshot_id=ref.id,
                    relative_path=ref.relative_path,
                    candidate_pages=_dedupe_preserve(
                        [
                            *draft_mapping.candidate_pages,
                            *draft_mapping.conflicting_candidates,
                        ]
                    ),
                    conflict_reason=draft_mapping.clarification_reason
                    or "multi-source evidence still points to competing pages",
                    dominant_channels=draft_mapping.supporting_channels,
                    confidence=draft_mapping.confidence,
                    source_channel=draft_mapping.source_channel,
                    evidence_basis=draft_mapping.evidence_basis,
                    unsupported=draft_mapping.unsupported,
                    unknown=draft_mapping.unknown,
                    verification_gaps=draft_mapping.verification_gaps,
                )
            )

        clarification_item = _clarification_from_ref(ref, plan=None)
        if clarification_item is not None:
            unresolved_ambiguities.append(clarification_item)

    return EvidenceFusionSummary(
        trusted_page_mappings=trusted_page_mappings,
        trusted_state_mappings=trusted_state_mappings,
        provisional_mappings=provisional_mappings,
        conflicting_evidence_groups=conflicting_groups,
        unresolved_ambiguities=unresolved_ambiguities,
        confidence=(
            "high"
            if trusted_page_mappings and not conflicting_groups and not unresolved_ambiguities
            else "medium"
            if trusted_page_mappings or provisional_mappings
            else "low"
        ),
        source_channel="mixed",
        evidence_basis=[
            f"trusted_page_mapping_count={len(trusted_page_mappings)}",
            f"trusted_state_mapping_count={len(trusted_state_mappings)}",
            f"provisional_mapping_count={len(provisional_mappings)}",
            f"conflict_count={len(conflicting_groups)}",
            f"unresolved_ambiguity_count={len(unresolved_ambiguities)}",
        ],
        unsupported=["no full visual semantic understanding"],
        unknown=(
            ["exact page mapping for unresolved ambiguities"]
            if unresolved_ambiguities
            else []
        ),
        verification_gaps=_dedupe_preserve(
            [
                *[
                    f"{group.relative_path}: {group.conflict_reason}"
                    for group in conflicting_groups
                ],
                *[
                    f"{item.relative_path}: {item.ambiguity_reason}"
                    for item in unresolved_ambiguities
                ],
            ]
        ),
    )


def _matched_page_requirements_for_ref(
    ref: ScreenshotRef,
    *,
    plan: RequiredEvidencePlan | None,
    final_delivery_only: bool = False,
) -> list[EvidencePageRequirement]:
    if plan is None:
        return []
    draft_mapping = ref.draft_mapping or _draft_mapping_for_ref(ref, plan=plan)
    if (
        draft_mapping is None
        or draft_mapping.clarification_needed
        or draft_mapping.page_key is None
    ):
        return []
    if final_delivery_only and not draft_mapping.final_delivery_eligible:
        return []
    matched = _page_requirement_by_key(plan, draft_mapping.page_key)
    return [matched] if matched is not None else []


def _state_categories_for_ref(ref: ScreenshotRef) -> set[StateCategory]:
    categories: set[StateCategory] = {"default"}
    evidence_blob = _ref_text_evidence(ref).lower()
    for state, hints in _STATE_HINTS.items():
        if state == "default":
            continue
        if any(hint.lower() in evidence_blob for hint in hints):
            categories.add(state)  # type: ignore[arg-type]
    return categories


def _state_signal_channels_for_ref(
    ref: ScreenshotRef,
) -> dict[StateCategory, set[str]]:
    state_channels: dict[StateCategory, set[str]] = {}
    for cue in ref.state_text_candidates:
        lowered = cue.value.lower()
        for state, hints in _STATE_HINTS.items():
            if state == "default":
                continue
            if any(hint.lower() in lowered for hint in hints):
                state_key = cast(StateCategory, state)
                state_channels.setdefault(state_key, set()).add(str(cue.source_channel))
    return state_channels


def _state_categories_by_channel_for_ref(
    ref: ScreenshotRef,
) -> dict[str, set[StateCategory]]:
    state_categories_by_channel: dict[str, set[StateCategory]] = {}
    for cue in ref.state_text_candidates:
        lowered = cue.value.lower()
        for state, hints in _STATE_HINTS.items():
            if state == "default":
                continue
            if any(hint.lower() in lowered for hint in hints):
                state_key = cast(StateCategory, state)
                state_categories_by_channel.setdefault(str(cue.source_channel), set()).add(state_key)
    return state_categories_by_channel


def _naming_issue(relative_path: str) -> bool:
    name = Path(relative_path).name
    lowered = name.lower()
    return "-" not in lowered and "_" not in lowered and not any(
        hint.lower() in lowered
        for state_hints in _STATE_HINTS.values()
        for hint in state_hints
    )


def _plan_coverage_summary(
    image_refs: list[ScreenshotRef],
    *,
    plan: RequiredEvidencePlan | None,
    ocr_available: bool,
) -> dict[str, Any]:
    if plan is None:
        return {
            "capture_mission_version": None,
            "capture_mission_path": None,
            "critical_flows": [],
            "critical_path_count": 0,
            "p0_critical_path_count": 0,
            "p1_critical_path_count": 0,
            "p2_critical_path_count": 0,
            "missing_p0_pages": [],
            "missing_p0_states": [],
            "missing_p1_pages": [],
            "missing_p1_states": [],
            "must_capture_pages": [],
            "must_capture_states": [],
            "nice_to_have_pages": [],
            "capture_order": [],
            "final_delivery_pass_line": [],
            "fallback_pass_line": [],
            "evidence_rationale": [],
            "critical_path_coverage_summary": None,
            "final_delivery_missing_critical_paths": [],
            "fallback_missing_critical_paths": [],
            "planned_page_count": 0,
            "matched_planned_page_count": 0,
            "planned_page_coverage_ratio": None,
            "missing_critical_pages": [],
            "planned_state_count": 0,
            "covered_planned_state_count": 0,
            "planned_state_coverage_ratio": None,
            "missing_planned_states": [],
            "missing_required_description_pages": [],
            "final_delivery_matched_planned_page_count": 0,
            "final_delivery_page_coverage_ratio": None,
            "final_delivery_missing_critical_pages": [],
            "final_delivery_covered_planned_state_count": 0,
            "final_delivery_state_coverage_ratio": None,
            "final_delivery_missing_planned_states": [],
            "final_delivery_missing_required_description_pages": [],
            "naming_issues": [],
            "final_delivery_trusted_mapping_count": 0,
        }

    mission = plan.capture_mission

    provisional_refs_by_page: dict[str, list[ScreenshotRef]] = {
        requirement.page_key: []
        for requirement in plan.critical_pages
    }
    final_delivery_refs_by_page: dict[str, list[ScreenshotRef]] = {
        requirement.page_key: []
        for requirement in plan.critical_pages
    }
    for ref in image_refs:
        for requirement in _matched_page_requirements_for_ref(ref, plan=plan):
            provisional_refs_by_page[requirement.page_key].append(ref)
        for requirement in _matched_page_requirements_for_ref(
            ref,
            plan=plan,
            final_delivery_only=True,
        ):
            final_delivery_refs_by_page[requirement.page_key].append(ref)

    def _coverage_from_refs(
        refs_by_page: dict[str, list[ScreenshotRef]],
    ) -> dict[str, Any]:
        missing_pages: list[str] = []
        missing_descriptions: list[str] = []
        missing_states: list[str] = []
        covered_state_count = 0
        total_state_count = 0

        for requirement in plan.critical_pages:
            matched_refs = refs_by_page.get(requirement.page_key, [])
            if not matched_refs:
                missing_pages.append(requirement.page_name)
                total_state_count += len(requirement.required_states)
                continue

            if requirement.description_required and not any(ref.description_links for ref in matched_refs):
                missing_descriptions.append(requirement.page_name)

            covered_states: set[StateCategory] = set()
            for ref in matched_refs:
                covered_states.update(_state_categories_for_ref(ref))

            for state in requirement.required_states:
                total_state_count += 1
                if state in covered_states:
                    covered_state_count += 1
                    continue
                if ocr_available and state != "default":
                    covered_state_count += 1
                    continue
                missing_states.append(f"{requirement.page_name}:{state}")

        matched_page_count = len([refs for refs in refs_by_page.values() if refs])
        page_ratio = (
            matched_page_count / len(plan.critical_pages)
            if plan.critical_pages
            else None
        )
        state_ratio = (
            covered_state_count / total_state_count
            if total_state_count
            else None
        )
        return {
            "matched_page_count": matched_page_count,
            "page_ratio": round(page_ratio, 3) if isinstance(page_ratio, float) else None,
            "missing_pages": missing_pages,
            "covered_state_count": covered_state_count,
            "state_ratio": round(state_ratio, 3) if isinstance(state_ratio, float) else None,
            "missing_states": missing_states,
            "missing_descriptions": missing_descriptions,
            "total_state_count": total_state_count,
        }

    provisional_coverage = _coverage_from_refs(provisional_refs_by_page)
    final_delivery_coverage = _coverage_from_refs(final_delivery_refs_by_page)
    requirement_by_name = {
        requirement.page_name: requirement
        for requirement in plan.critical_pages
    }

    def _critical_path_snapshot(
        path: CriticalPathDefinition,
        refs_by_page: dict[str, list[ScreenshotRef]],
    ) -> dict[str, Any]:
        matched_pages: list[str] = []
        missing_pages: list[str] = []
        covered_states: list[str] = []
        missing_states: list[str] = []

        for page_name in path.required_pages:
            requirement = requirement_by_name.get(page_name)
            if requirement is None:
                continue
            matched_refs = refs_by_page.get(requirement.page_key, [])
            if matched_refs:
                matched_pages.append(page_name)
            else:
                missing_pages.append(page_name)

        for state_label in path.required_states:
            page_name, _, raw_state = state_label.rpartition(":")
            requirement = requirement_by_name.get(page_name)
            matched_refs = refs_by_page.get(requirement.page_key, []) if requirement is not None else []
            if not matched_refs:
                missing_states.append(state_label)
                continue
            covered_state_categories: set[StateCategory] = set()
            for ref in matched_refs:
                covered_state_categories.update(_state_categories_for_ref(ref))
            if raw_state == "default" or raw_state in covered_state_categories:
                covered_states.append(state_label)
                continue
            if ocr_available and raw_state != "default":
                covered_states.append(state_label)
                continue
            missing_states.append(state_label)

        page_ratio = (
            len(matched_pages) / len(path.required_pages)
            if path.required_pages
            else None
        )
        state_ratio = (
            len(covered_states) / len(path.required_states)
            if path.required_states
            else None
        )
        return {
            "matched_pages": matched_pages,
            "missing_pages": missing_pages,
            "covered_states": covered_states,
            "missing_states": missing_states,
            "page_ratio": round(page_ratio, 3) if isinstance(page_ratio, float) else None,
            "state_ratio": round(state_ratio, 3) if isinstance(state_ratio, float) else None,
        }

    def _critical_path_gate(
        path: CriticalPathDefinition,
        *,
        snapshot: dict[str, Any],
        delivery_mode: str,
    ) -> bool:
        if not path.required_pages:
            return True
        if delivery_mode == "final":
            page_threshold = 1.0 if path.priority == "P0" else mission.final_delivery_policy.min_page_coverage_ratio
            state_threshold = mission.final_delivery_policy.min_state_coverage_ratio
        else:
            page_threshold = 1.0 if path.priority == "P0" else mission.fallback_policy.min_page_coverage_ratio
            state_threshold = mission.fallback_policy.min_state_coverage_ratio

        page_ratio = snapshot["page_ratio"]
        state_ratio = snapshot["state_ratio"]
        page_pass = page_ratio is None or page_ratio >= page_threshold
        state_pass = state_ratio is None or state_ratio >= state_threshold
        return page_pass and state_pass

    critical_path_records: list[CriticalPathCoverageRecord] = []
    failing_final_paths: list[str] = []
    failing_fallback_paths: list[str] = []
    for path in mission.critical_paths:
        provisional_snapshot = _critical_path_snapshot(path, provisional_refs_by_page)
        final_snapshot = _critical_path_snapshot(path, final_delivery_refs_by_page)
        gates_final_delivery = path.priority in {"P0", "P1"}
        gates_fallback_delivery = path.priority == "P0"
        final_delivery_pass = _critical_path_gate(
            path,
            snapshot=final_snapshot,
            delivery_mode="final",
        )
        fallback_pass = _critical_path_gate(
            path,
            snapshot=provisional_snapshot,
            delivery_mode="fallback",
        )
        path_label = f"[{path.priority}] {path.path_name}"
        if gates_final_delivery and not final_delivery_pass:
            failing_final_paths.append(path_label)
        if gates_fallback_delivery and not fallback_pass:
            failing_fallback_paths.append(path_label)
        critical_path_records.append(
            CriticalPathCoverageRecord(
                path_name=path.path_name,
                business_goal=path.business_goal,
                priority=path.priority,
                required_pages=path.required_pages,
                required_states=path.required_states,
                matched_pages=provisional_snapshot["matched_pages"],
                missing_pages=provisional_snapshot["missing_pages"],
                covered_states=provisional_snapshot["covered_states"],
                missing_states=provisional_snapshot["missing_states"],
                page_coverage_ratio=provisional_snapshot["page_ratio"],
                state_coverage_ratio=provisional_snapshot["state_ratio"],
                final_delivery_matched_pages=final_snapshot["matched_pages"],
                final_delivery_missing_pages=final_snapshot["missing_pages"],
                final_delivery_covered_states=final_snapshot["covered_states"],
                final_delivery_missing_states=final_snapshot["missing_states"],
                final_delivery_page_coverage_ratio=final_snapshot["page_ratio"],
                final_delivery_state_coverage_ratio=final_snapshot["state_ratio"],
                gates_final_delivery=gates_final_delivery,
                gates_fallback_delivery=gates_fallback_delivery,
                final_delivery_pass=final_delivery_pass,
                fallback_pass=fallback_pass,
                confidence=(
                    "high"
                    if final_delivery_pass
                    else "medium"
                    if fallback_pass
                    else "low"
                ),
                source_channel="mixed",
                evidence_basis=[
                    f"priority={path.priority}",
                    f"matched_pages={len(provisional_snapshot['matched_pages'])}/{len(path.required_pages)}",
                    f"matched_states={len(provisional_snapshot['covered_states'])}/{len(path.required_states)}",
                    f"final_delivery_matched_pages={len(final_snapshot['matched_pages'])}/{len(path.required_pages)}",
                    f"final_delivery_matched_states={len(final_snapshot['covered_states'])}/{len(path.required_states)}",
                ],
                verification_gaps=[
                    *(["does not yet pass final critical-path gate"] if gates_final_delivery and not final_delivery_pass else []),
                    *(["does not yet pass fallback critical-path gate"] if gates_fallback_delivery and not fallback_pass else []),
                ],
            )
        )

    critical_path_coverage_summary = CriticalPathCoverageSummary(
        critical_paths=critical_path_records,
        failing_final_paths=failing_final_paths,
        failing_fallback_paths=failing_fallback_paths,
        confidence=(
            "high"
            if not failing_final_paths and critical_path_records
            else "medium"
            if critical_path_records
            else "low"
        ),
        source_channel="mixed",
        evidence_basis=[
            f"critical_path_count={len(critical_path_records)}",
            f"failing_final_path_count={len(failing_final_paths)}",
            f"failing_fallback_path_count={len(failing_fallback_paths)}",
        ],
        verification_gaps=[
            *[f"{path}: final gate not met" for path in failing_final_paths],
            *[f"{path}: fallback gate not met" for path in failing_fallback_paths],
        ],
    )

    missing_p0_pages = _dedupe_preserve(
        page
        for record in critical_path_records
        if record.priority == "P0"
        for page in record.final_delivery_missing_pages
    )
    missing_p0_states = _dedupe_preserve(
        state
        for record in critical_path_records
        if record.priority == "P0"
        for state in record.final_delivery_missing_states
    )
    missing_p1_pages = _dedupe_preserve(
        page
        for record in critical_path_records
        if record.priority == "P1"
        for page in record.final_delivery_missing_pages
    )
    missing_p1_states = _dedupe_preserve(
        state
        for record in critical_path_records
        if record.priority == "P1"
        for state in record.final_delivery_missing_states
    )

    return {
        "capture_mission_version": mission.mission_version,
        "capture_mission_path": mission.mission_doc_path,
        "critical_flows": mission.critical_flows,
        "critical_path_count": len(mission.critical_paths),
        "p0_critical_path_count": len([path for path in mission.critical_paths if path.priority == "P0"]),
        "p1_critical_path_count": len([path for path in mission.critical_paths if path.priority == "P1"]),
        "p2_critical_path_count": len([path for path in mission.critical_paths if path.priority == "P2"]),
        "missing_p0_pages": missing_p0_pages,
        "missing_p0_states": missing_p0_states,
        "missing_p1_pages": missing_p1_pages,
        "missing_p1_states": missing_p1_states,
        "must_capture_pages": mission.must_capture_pages,
        "must_capture_states": mission.must_capture_states,
        "nice_to_have_pages": mission.nice_to_have_pages,
        "capture_order": mission.capture_order,
        "final_delivery_pass_line": mission.final_delivery_pass_line,
        "fallback_pass_line": mission.fallback_pass_line,
        "evidence_rationale": mission.evidence_rationale,
        "critical_path_coverage_summary": critical_path_coverage_summary,
        "final_delivery_missing_critical_paths": failing_final_paths,
        "fallback_missing_critical_paths": failing_fallback_paths,
        "planned_page_count": len(plan.critical_pages),
        "matched_planned_page_count": provisional_coverage["matched_page_count"],
        "planned_page_coverage_ratio": provisional_coverage["page_ratio"],
        "missing_critical_pages": provisional_coverage["missing_pages"],
        "planned_state_count": provisional_coverage["total_state_count"],
        "covered_planned_state_count": provisional_coverage["covered_state_count"],
        "planned_state_coverage_ratio": provisional_coverage["state_ratio"],
        "missing_planned_states": provisional_coverage["missing_states"],
        "missing_required_description_pages": provisional_coverage["missing_descriptions"],
        "final_delivery_matched_planned_page_count": final_delivery_coverage["matched_page_count"],
        "final_delivery_page_coverage_ratio": final_delivery_coverage["page_ratio"],
        "final_delivery_missing_critical_pages": final_delivery_coverage["missing_pages"],
        "final_delivery_covered_planned_state_count": final_delivery_coverage["covered_state_count"],
        "final_delivery_state_coverage_ratio": final_delivery_coverage["state_ratio"],
        "final_delivery_missing_planned_states": final_delivery_coverage["missing_states"],
        "final_delivery_missing_required_description_pages": final_delivery_coverage["missing_descriptions"],
        "naming_issues": [ref.relative_path for ref in image_refs if _naming_issue(ref.relative_path)],
        "final_delivery_trusted_mapping_count": len(
            [
                ref
                for ref in image_refs
                if ref.draft_mapping is not None and ref.draft_mapping.final_delivery_eligible
            ]
        ),
    }


def _select_description_sections(
    ref: ScreenshotRef,
    sections: list[dict[str, str]],
    *,
    matched_pages: list[EvidencePageRequirement] | None = None,
) -> list[dict[str, str]]:
    image_tokens = set(_normalized_tokens(Path(ref.relative_path).stem))
    image_tokens.update(_normalized_tokens(ref.ocr_text_preview))
    raw_snippets = [Path(ref.relative_path).stem]
    raw_snippets.extend(line.value.strip() for line in ref.ocr_text_lines if line.value.strip())
    if matched_pages:
        for page in matched_pages:
            image_tokens.update(page.match_tokens)
            image_tokens.update(_normalized_tokens(page.page_name))
            raw_snippets.append(page.page_name)
    for group in (
        ref.page_title_candidates,
        ref.button_text_candidates,
        ref.navigation_text_candidates,
        ref.state_text_candidates,
    ):
        for cue in group:
            if cue.source_channel == "markdown":
                continue
            image_tokens.update(_normalized_tokens(cue.value))
            if cue.value.strip():
                raw_snippets.append(cue.value.strip())
    image_parent = Path(ref.relative_path).parent.as_posix()
    stem = Path(ref.relative_path).stem.lower()
    scored: list[tuple[int, dict[str, str]]] = []
    exact_matches: list[tuple[int, dict[str, str]]] = []

    for section in sections:
        raw_text = f"{section['title']}\n{section['body']}"
        lowered = raw_text.lower()
        lowered_title = section["title"].lower()
        lowered_body = section["body"].lower()
        title_tokens = set(_normalized_tokens(section["title"]))
        body_tokens = set(_normalized_tokens(section["body"]))
        fuzzy_title_overlap = {
            image_token
            for image_token in image_tokens
            for title_token in title_tokens
            if image_token in title_token or title_token in image_token
        }
        overlap_title = _token_overlap(image_tokens, title_tokens)
        overlap_body = _token_overlap(image_tokens, body_tokens)
        informative_body_overlap = {
            token
            for token in overlap_body
            if token not in _NON_DEFAULT_STATE_HINT_TOKENS
        }
        score = len(overlap_body) + (len(overlap_title) * 4) + (len(fuzzy_title_overlap) * 2)
        exact_filename_match = bool(stem and stem in lowered)
        if exact_filename_match:
            score += 6
        elif len(overlap_title) >= 1:
            score += 2
        elif fuzzy_title_overlap:
            score += 1
        title_substring_hits = {
            snippet.strip()
            for snippet in raw_snippets
            if snippet
            and len(snippet.strip()) >= 3
            and snippet.lower() in lowered_title
        }
        body_substring_hits = {
            snippet.strip()
            for snippet in raw_snippets
            if snippet
            and len(snippet.strip()) >= 3
            and snippet.lower() in lowered_body
        }
        if title_substring_hits:
            score += 3 + len(title_substring_hits)
        if body_substring_hits:
            score += 2 + len(body_substring_hits)
        substring_hit = any(
            snippet
            and len(snippet) >= 2
            and (
                snippet.lower() in lowered
                or lowered in snippet.lower()
            )
            for snippet in raw_snippets
        )
        if substring_hit:
            score += 1 if overlap_title else 0
        if image_parent == Path(section["source_path"]).parent.as_posix() and (
            exact_filename_match or overlap_title or fuzzy_title_overlap
        ):
            score += 1
        if len(overlap_title) >= 2:
            score += 2
        if score >= 2 and (
            exact_filename_match
            or len(overlap_title) >= 1
            or bool(fuzzy_title_overlap)
            or bool(title_substring_hits)
            or bool(body_substring_hits)
            or (matched_pages and len(overlap_body) >= 2)
            or bool(informative_body_overlap)
        ):
            if exact_filename_match:
                exact_matches.append((score, section))
            else:
                scored.append((score, section))

    if exact_matches:
        exact_matches.sort(
            key=lambda item: (
                -item[0],
                item[1]["source_path"],
                item[1]["title"],
            )
        )
        return [section for _, section in exact_matches[:2]]

    scored.sort(
        key=lambda item: (
            -item[0],
            item[1]["source_path"],
            item[1]["title"],
        )
    )
    return [section for _, section in scored[:2]]


def _summarize_text(values: Iterable[str], *, limit: int = 4) -> list[str]:
    seen: set[str] = set()
    summary: list[str] = []
    for value in values:
        cleaned = value.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        summary.append(cleaned)
        if len(summary) >= limit:
            break
    return summary


def _render_auto_note(
    ref: ScreenshotRef,
    *,
    matched_sections: list[dict[str, str]],
    matched_tasks: list[str],
    matched_pages: list[EvidencePageRequirement],
) -> str | None:
    title = Path(ref.relative_path).stem.replace("_", " ").replace("-", " ")
    if len(matched_pages) == 1:
        title = matched_pages[0].page_name
    if matched_sections:
        first_body_line = next(
            (line.strip() for line in matched_sections[0]["body"].splitlines() if line.strip()),
            "",
        )
        if first_body_line:
            if len(matched_pages) != 1:
                title = first_body_line

    basis_lines: list[str] = [f"# {title}", "", f"- screenshot: {ref.relative_path}"]

    if matched_sections:
        basis_lines.extend(["", "## Existing description evidence"])
        for section in matched_sections:
            basis_lines.append(f"### {section['title']}")
            basis_lines.append(section["body"].strip())

    if ref.ocr_text_lines:
        basis_lines.extend(["", "## OCR text cues"])
        for cue in _summarize_text((line.value for line in ref.ocr_text_lines), limit=8):
            basis_lines.append(f"- {cue}")

    for heading, cues in (
        ("Page title candidates", ref.page_title_candidates),
        ("Button candidates", ref.button_text_candidates),
        ("Navigation candidates", ref.navigation_text_candidates),
        ("State candidates", ref.state_text_candidates),
    ):
        values = _summarize_text((cue.value for cue in cues), limit=5)
        if values:
            basis_lines.extend(["", f"## {heading}"])
            basis_lines.extend(f"- {value}" for value in values)

    if matched_tasks:
        basis_lines.extend(["", "## Related task checklist items"])
        basis_lines.extend(f"- {task}" for task in matched_tasks[:6])

    if matched_pages:
        basis_lines.extend(["", "## Planned critical page matches"])
        for page in matched_pages[:4]:
            state_text = ", ".join(page.required_states)
            basis_lines.append(f"- {page.page_name} (required_states: {state_text})")

    text = "\n".join(basis_lines).strip()
    if not matched_sections and not ref.ocr_text_lines:
        return None
    if len(text) < 40:
        return None
    return text


def _remediation_priority_page_names(
    required_evidence_plan: RequiredEvidencePlan | None,
    *,
    refs: list[ScreenshotRef],
) -> list[str]:
    if required_evidence_plan is None:
        return []
    plan_coverage = _plan_coverage_summary(
        [ref for ref in refs if ref.kind == "image"],
        plan=required_evidence_plan,
        ocr_available=any(ref.kind == "image" and bool(ref.ocr_text_lines) for ref in refs),
    )
    priority_pages: list[str] = []
    critical_summary = plan_coverage.get("critical_path_coverage_summary")
    if isinstance(critical_summary, CriticalPathCoverageSummary):
        for record in critical_summary.critical_paths:
            if record.priority in {"P0", "P1"} and (
                not record.final_delivery_pass or not record.fallback_pass
            ):
                priority_pages.extend(record.required_pages)
    priority_pages.extend(list(plan_coverage.get("final_delivery_missing_critical_pages", [])))
    priority_pages.extend(list(plan_coverage.get("missing_critical_pages", [])))
    return _dedupe_preserve(priority_pages)


def _matched_pages_for_remediation(
    ref: ScreenshotRef,
    *,
    required_evidence_plan: RequiredEvidencePlan | None,
    priority_page_names: list[str],
) -> list[EvidencePageRequirement]:
    if required_evidence_plan is None:
        return []
    if (
        ref.draft_mapping is not None
        and ref.draft_mapping.final_delivery_eligible
        and ref.draft_mapping.page_key is not None
    ):
        matched = _page_requirement_by_key(required_evidence_plan, ref.draft_mapping.page_key)
        return [matched] if matched is not None else []
    candidates = [
        _mapping_candidate_details(requirement, ref)
        for requirement in required_evidence_plan.critical_pages
    ]
    candidates = [candidate for candidate in candidates if int(candidate["score"]) > 0]
    if not candidates:
        return []
    candidates.sort(
        key=lambda item: (
            0
            if str(item["requirement"].page_name) in priority_page_names
            else 1,
            -int(item["score"]),
            item["requirement"].page_key,
        )
    )
    priority_candidates = [
        candidate
        for candidate in candidates
        if str(candidate["requirement"].page_name) in priority_page_names
    ]
    if priority_candidates:
        candidates = priority_candidates
    matched_pages: list[EvidencePageRequirement] = []
    for candidate in candidates:
        requirement = candidate["requirement"]
        if requirement in matched_pages:
            continue
        matched_pages.append(requirement)
        if len(matched_pages) >= 2:
            break
    return matched_pages


def _max_confidence(left: str, right: str) -> str:
    order = {"low": 0, "medium": 1, "high": 2}
    return left if order.get(left, 0) >= order.get(right, 0) else right


def _missing_state_categories(image_refs: list[ScreenshotRef]) -> list[str]:
    evidence_blob = "\n".join(
        cue.value.lower()
        for ref in image_refs
        for cue in ref.state_text_candidates
    )
    if not evidence_blob:
        evidence_blob = "\n".join(ref.relative_path.lower() for ref in image_refs)
    missing: list[str] = []
    for label, hints in _STATE_HINTS.items():
        if label == "default":
            continue
        if not any(hint.lower() in evidence_blob for hint in hints):
            missing.append(label)
    return missing


def _line_to_cue(line: OCRLine, *, cue_type: str, basis_prefix: str) -> TextCue:
    confidence = "high" if line.confidence >= 0.85 else "medium" if line.confidence >= 0.6 else "low"
    return TextCue(
        cue_type=cue_type,  # type: ignore[arg-type]
        value=line.text,
        confidence=confidence,
        source_channel="ocr",
        evidence_basis=[f"{basis_prefix}: '{line.text}' (ocr_confidence={line.confidence:.2f})"],
    )


def _classify_text_cues(lines: list[OCRLine]) -> tuple[list[TextCue], list[TextCue], list[TextCue], list[TextCue], list[TextCue]]:
    ocr_lines = [_line_to_cue(line, cue_type="ocr_text", basis_prefix="ocr line") for line in lines]
    page_titles: list[TextCue] = []
    buttons: list[TextCue] = []
    navs: list[TextCue] = []
    states: list[TextCue] = []

    for idx, line in enumerate(lines):
        stripped = line.text.strip()
        lowered = stripped.lower()
        word_count = len(_normalized_tokens(stripped))

        if idx == 0 and 1 <= word_count <= 8:
            page_titles.append(_line_to_cue(line, cue_type="page_title", basis_prefix="ocr title candidate"))
        if any(keyword in lowered for keyword in _BUTTON_HINTS) and word_count <= 5:
            buttons.append(_line_to_cue(line, cue_type="button_text", basis_prefix="ocr button candidate"))
        if any(keyword in lowered for keyword in _NAV_HINTS) and word_count <= 6:
            navs.append(_line_to_cue(line, cue_type="navigation_text", basis_prefix="ocr navigation candidate"))
        if any(pattern.search(stripped) for pattern in _STATE_PATTERNS):
            states.append(_line_to_cue(line, cue_type="state_text", basis_prefix="ocr state candidate"))

    return ocr_lines, page_titles, buttons, navs, states


def _filename_cues(relative_path: str) -> tuple[list[TextCue], list[TextCue], list[TextCue], list[TextCue]]:
    stem = Path(relative_path).stem.replace("_", " ").replace("-", " ")
    if not stem:
        return [], [], [], []

    basis = [f"filename hint from '{relative_path}'"]
    title = [
        TextCue(
            cue_type="page_title",
            value=stem,
            confidence="low",
            source_channel="filename",
            evidence_basis=basis,
            verification_gaps=["filename hint only; needs OCR or markdown confirmation"],
        )
    ]
    buttons: list[TextCue] = []
    navs: list[TextCue] = []
    states: list[TextCue] = []
    lowered = stem.lower()
    if any(keyword in lowered for keyword in _BUTTON_HINTS):
        buttons.append(
            TextCue(
                cue_type="button_text",
                value=stem,
                confidence="low",
                source_channel="filename",
                evidence_basis=basis,
                verification_gaps=["filename hint only; needs OCR or markdown confirmation"],
            )
        )
    if any(keyword in lowered for keyword in _NAV_HINTS):
        navs.append(
            TextCue(
                cue_type="navigation_text",
                value=stem,
                confidence="low",
                source_channel="filename",
                evidence_basis=basis,
                verification_gaps=["filename hint only; needs OCR or markdown confirmation"],
            )
        )
    if any(pattern.search(stem) for pattern in _STATE_PATTERNS):
        states.append(
            TextCue(
                cue_type="state_text",
                value=stem,
                confidence="medium",
                source_channel="filename",
                evidence_basis=basis,
            )
        )
    return title, buttons, navs, states


def _markdown_cues(description_text: str, description_path: str) -> tuple[list[TextCue], list[TextCue], list[TextCue], list[TextCue]]:
    text = description_text.strip()
    if not text:
        return [], [], [], []
    lines = [line.strip(" #-\t") for line in text.splitlines() if line.strip()]
    if not lines:
        return [], [], [], []

    title = [
        TextCue(
            cue_type="page_title",
            value=lines[0],
            confidence="medium",
            source_channel="markdown",
            evidence_basis=[f"markdown heading or first line from '{description_path}'"],
        )
    ]
    buttons: list[TextCue] = []
    navs: list[TextCue] = []
    states: list[TextCue] = []
    for line in lines[1:8]:
        lowered = line.lower()
        if any(keyword in lowered for keyword in _BUTTON_HINTS):
            buttons.append(
                TextCue(
                    cue_type="button_text",
                    value=line,
                    confidence="medium",
                    source_channel="markdown",
                    evidence_basis=[f"markdown description from '{description_path}'"],
                )
            )
        if any(keyword in lowered for keyword in _NAV_HINTS):
            navs.append(
                TextCue(
                    cue_type="navigation_text",
                    value=line,
                    confidence="medium",
                    source_channel="markdown",
                    evidence_basis=[f"markdown description from '{description_path}'"],
                )
            )
        if any(pattern.search(line) for pattern in _STATE_PATTERNS):
            states.append(
                TextCue(
                    cue_type="state_text",
                    value=line,
                    confidence="medium",
                    source_channel="markdown",
                    evidence_basis=[f"markdown description from '{description_path}'"],
                )
            )
    return title, buttons, navs, states


def _readability_assessment(
    *,
    width: int | None,
    height: int | None,
    quality_tier: str,
    file_size_bytes: int,
    ocr_lines: list[OCRLine],
    has_description_links: bool,
) -> ReadabilityAssessment:
    reasons: list[str] = []
    verification_gaps: list[str] = []

    if width is None or height is None:
        reasons.append("missing image dimensions")
        return ReadabilityAssessment(
            level="unreadable",
            confidence="high",
            source_channel="metadata",
            evidence_basis=["image dimensions unavailable"],
            reasons=reasons,
            unknown=["pixel resolution"],
            verification_gaps=["replace screenshot with a valid image export"],
        )

    if width < 480 or height < 320 or file_size_bytes < 5_000:
        level = "low"
        reasons.append("image resolution is too small for reliable UI text review")
        verification_gaps.append("provide higher-resolution screenshots")
    elif quality_tier == "medium":
        level = "medium"
        reasons.append("image resolution is acceptable but may miss smaller UI text")
    else:
        level = "high"
        reasons.append("image resolution is suitable for text-oriented evidence review")

    if ocr_lines:
        avg_conf = sum(line.confidence for line in ocr_lines) / len(ocr_lines)
        if avg_conf < 0.55 and level != "low":
            level = "medium"
            reasons.append("OCR confidence is limited; some text may require manual confirmation")
            verification_gaps.append("verify smaller labels manually")
    else:
        if not has_description_links:
            verification_gaps.append("no OCR text or linked description available for this screenshot")
        reasons.append("no OCR text extracted from this screenshot")

    confidence = "high" if level in {"high", "low"} else "medium"
    return ReadabilityAssessment(
        level=level,  # type: ignore[arg-type]
        confidence=confidence,
        source_channel="mixed" if ocr_lines else "metadata",
        evidence_basis=[
            f"resolution={width}x{height}",
            f"file_size_bytes={file_size_bytes}",
        ] + (
            [f"ocr_lines={len(ocr_lines)}"] if ocr_lines else []
        ),
        reasons=reasons,
        verification_gaps=verification_gaps,
    )


def _description_links(
    *,
    image_relative_path: str,
    image_tokens: list[str],
    description_refs: list[ScreenshotRef],
    description_texts: dict[str, str],
) -> list[DescriptionLink]:
    links: list[DescriptionLink] = []
    image_parent = Path(image_relative_path).parent.as_posix()
    for ref in description_refs:
        desc_text = description_texts.get(ref.id, "")
        desc_tokens = _normalized_tokens(desc_text)
        overlap = _token_overlap(image_tokens, desc_tokens)
        desc_parent = Path(ref.relative_path).parent.as_posix()
        confidence = "low"
        basis: list[str] = []
        verification_gaps: list[str] = []

        if Path(image_relative_path).stem.lower() in desc_text.lower():
            confidence = "high"
            basis.append(f"markdown explicitly mentions filename '{Path(image_relative_path).name}'")
        elif len(overlap) >= 2:
            confidence = "medium"
            basis.append(f"markdown shares tokens {sorted(overlap)} with filename")
        elif image_parent == desc_parent:
            confidence = "medium"
            basis.append("description file is colocated with the screenshot")
        elif Path(ref.relative_path).name in {"screens-description.md", *_LIGHTWEIGHT_MAPPING_FILES}:
            confidence = "low"
            basis.append(f"global {Path(ref.relative_path).name} may apply to this screenshot")
            verification_gaps.append("link inferred from shared evidence bundle; verify exact screenshot mapping")
        else:
            continue

        links.append(
            DescriptionLink(
                description_id=ref.id,
                description_path=ref.relative_path,
                confidence=confidence,  # type: ignore[arg-type]
                source_channel="markdown",
                evidence_basis=basis,
                verification_gaps=verification_gaps,
            )
        )
    return links


def _merge_unique(cues: Iterable[TextCue]) -> list[TextCue]:
    seen: set[tuple[str, str, str]] = set()
    merged: list[TextCue] = []
    for cue in cues:
        key = (cue.cue_type, cue.value, cue.source_channel)
        if key in seen:
            continue
        seen.add(key)
        merged.append(cue)
    return merged


def _retag_cues(
    cues: Iterable[TextCue],
    *,
    source_channel: str,
    evidence_note: str | None = None,
) -> list[TextCue]:
    retagged: list[TextCue] = []
    for cue in cues:
        evidence_basis = list(cue.evidence_basis)
        if evidence_note is not None:
            evidence_basis.append(evidence_note)
        retagged.append(
            cue.model_copy(
                update={
                    "source_channel": source_channel,
                    "evidence_basis": evidence_basis,
                }
            )
        )
    return retagged


def _build_refs(
    files: list[Path],
    *,
    root: Path,
    ocr_backend: str | None,
) -> list[ScreenshotRef]:
    refs: list[ScreenshotRef] = []
    description_refs: list[ScreenshotRef] = []
    description_texts: dict[str, str] = {}

    for index, path in enumerate(files, start=1):
        relative_path = path.relative_to(root).as_posix()
        kind = "description" if path.suffix.lower() in _DESCRIPTION_EXTENSIONS else "image"
        description_preview = _description_preview(path)
        width: int | None = None
        height: int | None = None
        ocr_text_preview: str | None = None

        if kind == "image":
            width, height = _image_dimensions(path)
            if ocr_backend is not None:
                ocr_result = run_ocr(path, preferred_backend=ocr_backend)
                if ocr_result.raw_text.strip():
                    ocr_text_preview = ocr_result.raw_text[:_DESCRIPTION_PREVIEW_CHARS]

        ref = ScreenshotRef(
            id=_make_id(index),
            path=str(path.resolve()),
            relative_path=relative_path,
            kind=kind,  # type: ignore[arg-type]
            format=path.suffix.lower().lstrip("."),
            file_size_bytes=path.stat().st_size,
            width=width,
            height=height,
            resolution=_resolution(width, height),
            quality_tier=_quality_tier(width, height, kind=kind),  # type: ignore[arg-type]
            description_preview=description_preview,
            signal_warnings=_signal_warnings(relative_path, description_preview, ""),
            readability=ReadabilityAssessment(
                level="unreadable" if kind == "description" else "medium",
                confidence="high",
                source_channel="metadata",
                evidence_basis=["description files do not require readability checks"]
                if kind == "description"
                else [],
                reasons=["not applicable for markdown description files"]
                if kind == "description"
                else [],
                unsupported=["readability assessment not applicable"]
                if kind == "description"
                else [],
            ),
            ocr_text_preview=ocr_text_preview,
            ocr_text_lines=[],
            page_title_candidates=[],
            button_text_candidates=[],
            navigation_text_candidates=[],
            state_text_candidates=[],
            description_links=[],
            confidence="high" if kind == "description" else "medium",
            source_channel="markdown" if kind == "description" else "mixed",
            evidence_basis=(
                [f"markdown preview extracted from '{relative_path}'"]
                if kind == "description"
                else [f"metadata extracted from '{relative_path}'"]
            ),
        )
        refs.append(ref)
        if kind == "description":
            description_refs.append(ref)
            description_texts[ref.id] = _read_text(path)

    for idx, ref in enumerate(refs):
        if ref.kind != "image":
            continue

        filename_tokens = _normalized_tokens(ref.relative_path)
        description_links = _description_links(
            image_relative_path=ref.relative_path,
            image_tokens=filename_tokens,
            description_refs=description_refs,
            description_texts=description_texts,
        )
        ocr_lines_raw: list[OCRLine] = []
        if ocr_backend is not None:
            ocr_result = run_ocr(Path(ref.path), preferred_backend=ocr_backend)
            ocr_lines_raw = list(ocr_result.lines)

        ocr_cues, ocr_titles, ocr_buttons, ocr_navs, ocr_states = _classify_text_cues(ocr_lines_raw)
        filename_titles, filename_buttons, filename_navs, filename_states = _filename_cues(ref.relative_path)

        markdown_titles: list[TextCue] = []
        markdown_buttons: list[TextCue] = []
        markdown_navs: list[TextCue] = []
        markdown_states: list[TextCue] = []
        for link in description_links:
            if Path(link.description_path).name in _LIGHTWEIGHT_MAPPING_FILES:
                continue
            description_text = description_texts.get(link.description_id, "")
            description_sections = _markdown_sections(description_text, link.description_path)
            selected_sections = _select_description_sections(ref, description_sections)
            if not selected_sections and len(description_sections) == 1:
                selected_sections = description_sections[:1]
            for section in selected_sections:
                cue_text = _section_cue_text(section)
                if not cue_text:
                    continue
                desc_titles, desc_buttons, desc_navs, desc_states = _markdown_cues(
                    cue_text,
                    section["source_path"],
                )
                markdown_titles.extend(desc_titles)
                markdown_buttons.extend(desc_buttons)
                markdown_navs.extend(desc_navs)
                markdown_states.extend(desc_states)

        readability = _readability_assessment(
            width=ref.width,
            height=ref.height,
            quality_tier=ref.quality_tier,
            file_size_bytes=ref.file_size_bytes,
            ocr_lines=ocr_lines_raw,
            has_description_links=bool(description_links),
        )
        warnings = _signal_warnings(
            ref.relative_path,
            ref.description_preview,
            "\n".join(line.text for line in ocr_lines_raw),
        )

        verification_gaps = list(readability.verification_gaps)
        if not ocr_lines_raw:
            verification_gaps.append("no OCR-derived text cues extracted from this screenshot")
        if not description_links:
            verification_gaps.append("no linked markdown description for this screenshot")

        refs[idx] = ref.model_copy(
            update={
                "signal_warnings": warnings,
                "readability": readability,
                "ocr_text_preview": "\n".join(line.text for line in ocr_lines_raw)[:_DESCRIPTION_PREVIEW_CHARS]
                if ocr_lines_raw
                else None,
                "ocr_text_lines": ocr_cues,
                "page_title_candidates": _merge_unique(ocr_titles + markdown_titles + filename_titles),
                "button_text_candidates": _merge_unique(ocr_buttons + markdown_buttons + filename_buttons),
                "navigation_text_candidates": _merge_unique(ocr_navs + markdown_navs + filename_navs),
                "state_text_candidates": _merge_unique(ocr_states + markdown_states + filename_states),
                "description_links": description_links,
                "confidence": (
                    "high"
                    if ocr_lines_raw or description_links
                    else "medium"
                ),
                "source_channel": (
                    "mixed"
                    if ocr_lines_raw and description_links
                    else "ocr"
                    if ocr_lines_raw
                    else "markdown"
                    if description_links
                    else "metadata"
                ),
                "evidence_basis": [f"relative_path={ref.relative_path}"]
                + ([f"ocr_lines={len(ocr_lines_raw)}"] if ocr_lines_raw else [])
                + ([f"description_links={len(description_links)}"] if description_links else []),
                "unsupported": [
                    "no semantic scene understanding",
                    "no automatic task_id attribution",
                    "no automatic module_id attribution",
                    "no scenario-intent inference without explicit evidence",
                ],
                "unknown": [
                    "full page semantic summary",
                ],
                "verification_gaps": sorted(set(verification_gaps)),
            }
        )

    return refs


def _evidence_assessment(
    refs: list[ScreenshotRef],
    *,
    ocr_available: bool,
    task_checklist_lite: str | None,
    required_evidence_plan: RequiredEvidencePlan | dict[str, Any] | None = None,
) -> EvidenceAssessment:
    required_plan = _coerce_required_evidence_plan(required_evidence_plan)
    mission = required_plan.capture_mission if required_plan is not None else None
    image_refs = [ref for ref in refs if ref.kind == "image"]
    description_refs = [ref for ref in refs if ref.kind == "description"]
    readable_refs = [ref for ref in image_refs if ref.readability.level in {"high", "medium"}]
    text_rich_refs = [
        ref
        for ref in image_refs
        if ref.ocr_text_lines or ref.description_links or ref.page_title_candidates or ref.state_text_candidates
    ]
    described_refs = [ref for ref in image_refs if ref.description_links]
    ocr_refs = [ref for ref in image_refs if ref.ocr_text_lines]

    blocking_reasons: list[str] = []
    required_actions: list[str] = []
    verification_gaps: list[str] = []
    missing_coverage: list[str] = []
    task_coverage = _task_coverage_summary(image_refs, task_checklist_lite)
    plan_coverage = _plan_coverage_summary(
        image_refs,
        plan=required_plan,
        ocr_available=ocr_available,
    )
    fusion_summary = _build_evidence_fusion_summary(image_refs)
    image_count = len(image_refs)
    readable_ratio = len(readable_refs) / image_count if image_count else 0.0
    text_rich_ratio = len(text_rich_refs) / image_count if image_count else 0.0
    description_link_ratio = len(described_refs) / image_count if image_count else 0.0
    ocr_text_ratio = len(ocr_refs) / image_count if image_count else 0.0
    low_readability_paths = [
        ref.relative_path
        for ref in image_refs
        if ref.readability.level in {"low", "unreadable"}
    ]
    missing_description_paths = [
        ref.relative_path
        for ref in image_refs
        if not ref.description_links
    ]
    missing_ocr_paths = [
        ref.relative_path
        for ref in image_refs
        if not ref.ocr_text_lines
    ]
    generic_missing_state_categories = _missing_state_categories(image_refs)
    plan_missing_pages = list(plan_coverage.get("missing_critical_pages", []))
    plan_missing_states = list(plan_coverage.get("missing_planned_states", []))
    plan_missing_descriptions = list(plan_coverage.get("missing_required_description_pages", []))
    plan_naming_issues = list(plan_coverage.get("naming_issues", []))
    final_plan_missing_pages = list(plan_coverage.get("final_delivery_missing_critical_pages", []))
    final_plan_missing_states = list(plan_coverage.get("final_delivery_missing_planned_states", []))
    final_plan_missing_descriptions = list(
        plan_coverage.get("final_delivery_missing_required_description_pages", [])
    )
    critical_path_coverage_summary = plan_coverage.get("critical_path_coverage_summary")
    final_critical_path_failures = list(plan_coverage.get("final_delivery_missing_critical_paths", []))
    fallback_critical_path_failures = list(plan_coverage.get("fallback_missing_critical_paths", []))
    critical_path_records = (
        critical_path_coverage_summary.critical_paths
        if isinstance(critical_path_coverage_summary, CriticalPathCoverageSummary)
        else []
    )
    final_gate_pages = _dedupe_preserve(
        page
        for record in critical_path_records
        if record.gates_final_delivery
        for page in record.required_pages
    )
    fallback_gate_pages = _dedupe_preserve(
        page
        for record in critical_path_records
        if record.gates_fallback_delivery
        for page in record.required_pages
    )
    final_gate_missing_pages = _dedupe_preserve(
        page
        for record in critical_path_records
        if record.gates_final_delivery
        for page in record.final_delivery_missing_pages
    )
    fallback_gate_missing_pages = _dedupe_preserve(
        page
        for record in critical_path_records
        if record.gates_fallback_delivery
        for page in record.missing_pages
    )
    final_gate_missing_states = _dedupe_preserve(
        state
        for record in critical_path_records
        if record.gates_final_delivery
        for state in record.final_delivery_missing_states
    )
    fallback_gate_missing_states = _dedupe_preserve(
        state
        for record in critical_path_records
        if record.gates_fallback_delivery
        for state in record.missing_states
    )
    final_gate_missing_descriptions = [
        page
        for page in final_plan_missing_descriptions
        if page in final_gate_pages
    ]
    fallback_gate_missing_descriptions = [
        page
        for page in plan_missing_descriptions
        if page in fallback_gate_pages
    ]
    raw_clarification_items = [
        _clarification_from_ref(ref, plan=required_plan)
        for ref in image_refs
        if ref.draft_mapping is not None and ref.draft_mapping.clarification_needed
    ]
    clarification_items: list[ClarificationItem] = []
    clarification_suppressed_reason: str | None = None
    conflicting_groups = fusion_summary.conflicting_evidence_groups
    missing_state_categories = (
        _dedupe_preserve(
            state.rsplit(":", 1)[-1]
            for state in (
                final_gate_missing_states
                or fallback_gate_missing_states
                or plan_missing_states
            )
        )
        if (final_gate_missing_states or fallback_gate_missing_states or plan_missing_states)
        else generic_missing_state_categories
    )
    text_evidence_missing_paths = [
        ref.relative_path
        for ref in image_refs
        if not (
            ref.ocr_text_lines
            or ref.description_links
            or ref.page_title_candidates
            or ref.button_text_candidates
            or ref.navigation_text_candidates
            or ref.state_text_candidates
        )
    ]
    basis = [
        f"image_count={image_count}",
        f"description_count={len(description_refs)}",
        f"readable_image_count={len(readable_refs)}",
        f"text_rich_image_count={len(text_rich_refs)}",
        f"ocr_available={ocr_available}",
    ]
    if required_plan is not None:
        basis.append(f"planned_page_count={required_plan.critical_page_count}")
        if mission is not None:
            basis.append(f"capture_mission_version={mission.mission_version}")
    basis.extend(fusion_summary.evidence_basis)

    if not image_refs:
        blocking_reasons.append("no screenshots were provided")
        required_actions.append("补至少 5 张关键页面截图到 inputs/screens/")

    if image_count and image_count < 5:
        missing_coverage.append(f"关键页面截图数量不足，当前仅 {image_count} 张，建议至少补到 5 张")
        required_actions.append("补足至少 5 张关键页面截图，覆盖核心主流程和关键状态")

    if not ocr_available and not description_refs:
        blocking_reasons.append("no local OCR capability and no markdown description evidence")
        required_actions.extend(
            [
                "安装本地 OCR 依赖，或启用支持的本地 OCR 后端",
                "补充 inputs/screens-description.md 或每页说明文件",
                "如不想批量改文件名，可在 inputs/screens/ 补 screens-map.md 或 screens-index.md，写最小截图映射",
            ]
        )

    if image_refs and not readable_refs and not description_refs:
        blocking_reasons.append("all screenshots are low readability or unreadable")
        required_actions.append("补高分辨率截图，建议宽度 >= 1280 像素")
    elif image_refs and not readable_refs:
        verification_gaps.append("截图可读性偏低，当前主要依赖 markdown 说明补足证据")
        required_actions.append("补高分辨率截图，建议宽度 >= 1280 像素")

    if image_refs and readable_ratio < 0.8:
        missing_coverage.append(
            f"可读截图覆盖不足：当前可读比例 {readable_ratio:.0%}，最终交付建议达到 80% 以上"
        )
        if low_readability_paths:
            preview = "；".join(low_readability_paths[:4])
            required_actions.append(f"这些截图分辨率不足，建议优先补高清版本：{preview}")

    if image_refs and not text_rich_refs:
        verification_gaps.append("current screenshots do not provide enough trustworthy text evidence")
        required_actions.extend(_mapping_guidance_actions())
    elif image_refs and text_rich_ratio < 0.8:
        missing_coverage.append(
            f"文字线索覆盖不足：当前仅 {text_rich_ratio:.0%} 的截图具备 OCR 或说明文件支撑"
        )
        required_actions.extend(
            [
                "为关键页面补充 OCR 可读截图或每页说明文件",
                "如页面较多，可在 inputs/screens/ 补 screens-map.md 或 screens-index.md，写最小截图映射",
            ]
        )

    if image_refs and not ocr_available and description_link_ratio < 0.8:
        missing_coverage.append(
            f"说明文件覆盖不足：当前仅 {description_link_ratio:.0%} 的截图能关联到 markdown 说明"
        )
        required_actions.extend(
            [
                "为未说明的关键页面补充 screens-description.md 或同目录说明文件",
                "如页面较多，可在 inputs/screens/ 用 screens-map.md 或 screens-index.md 先补最小映射",
            ]
        )
        if missing_description_paths:
            preview = "；".join(missing_description_paths[:4])
            required_actions.append(f"这些页面缺说明文件，请补页面说明：{preview}")

    if image_refs and ocr_available and ocr_text_ratio < 0.6:
        missing_coverage.append(
            f"OCR 文本覆盖不足：当前仅 {ocr_text_ratio:.0%} 的截图提取到可信 OCR 文字"
        )
        required_actions.append("补更清晰的高分辨率截图，确保关键文字可被 OCR 提取")
        if missing_ocr_paths:
            preview = "；".join(missing_ocr_paths[:4])
            required_actions.append(f"这些截图目前没有可用 OCR 文字，请补更清晰版本：{preview}")

    gate_missing_pages = final_gate_missing_pages or fallback_gate_missing_pages
    gate_missing_states = final_gate_missing_states or fallback_gate_missing_states
    gate_missing_descriptions = (
        final_gate_missing_descriptions
        or fallback_gate_missing_descriptions
    )

    if gate_missing_pages:
        preview = "；".join(gate_missing_pages[:6])
        missing_coverage.append(f"Capture Mission 缺少关键页面：{preview}")
        required_actions.append(f"先补这些 must_capture_pages：{preview}")

    if gate_missing_states:
        preview = "；".join(gate_missing_states[:6])
        missing_coverage.append(f"Capture Mission 缺少关键状态：{preview}")
        required_actions.append(f"先补这些 must_capture_states 的截图或说明：{preview}")

    if gate_missing_descriptions and not ocr_available:
        preview = "；".join(gate_missing_descriptions[:6])
        missing_coverage.append(f"Capture Mission 缺少关键页面说明：{preview}")
        required_actions.extend(
            [
                f"这些关键页面缺说明，请补 markdown 说明：{preview}",
                "如页面较多，可先在 inputs/screens/ 补 screens-map.md 或 screens-index.md，写关键截图 -> 页面/状态 映射",
            ]
        )

    if final_critical_path_failures:
        preview = "；".join(final_critical_path_failures[:4])
        missing_coverage.append(f"关键业务主链路未过 final line：{preview}")
        required_actions.append(f"优先补这些 critical path 的关键页面/状态：{preview}")

    if fallback_critical_path_failures:
        preview = "；".join(fallback_critical_path_failures[:4])
        missing_coverage.append(f"P0 主链路连 fallback 线都没过：{preview}")
        required_actions.append(f"先补这些 P0 critical path，否则不能安全输出 bounded fallback：{preview}")

    if plan_naming_issues:
        verification_gaps.append("当前部分截图命名不规范，自动匹配更多依赖 OCR / markdown / 轻量映射补充")
        if missing_coverage or blocking_reasons:
            verification_gaps.append(_rename_accelerator_suggestion(plan_naming_issues))

    clarification_items, clarification_suppressed_reason = _select_clarification_items(
        clarification_items=[item for item in raw_clarification_items if item is not None],
        missing_pages=final_plan_missing_pages or plan_missing_pages,
        missing_states=final_plan_missing_states or plan_missing_states,
        missing_descriptions=final_plan_missing_descriptions or plan_missing_descriptions,
        blocking_reasons=blocking_reasons,
    )

    if clarification_items and (missing_coverage or blocking_reasons):
        required_actions.append(
            f"先确认这 {len(clarification_items)} 张歧义截图的页面/状态，其余截图映射已自动起草"
        )
        verification_gaps.append("少量截图仍需轻量确认；系统已自动起草其余 screenshot -> page/state 映射")
    elif clarification_suppressed_reason and raw_clarification_items:
        verification_gaps.append(clarification_suppressed_reason)

    if conflicting_groups:
        conflict_preview = "；".join(group.relative_path for group in conflicting_groups[:4])
        verification_gaps.append("当前仍有多来源证据冲突，相关截图不能计入 trusted mapping")
        required_actions.append(f"优先处理这些多来源冲突截图：{conflict_preview}")

    key_task_coverage_ratio = task_coverage["key_task_coverage_ratio"]
    if isinstance(key_task_coverage_ratio, float) and key_task_coverage_ratio < 0.8:
        missing_tasks = task_coverage["missing_tasks"]
        if isinstance(missing_tasks, list) and missing_tasks:
            preview = "；".join(str(item) for item in missing_tasks[:4])
            missing_coverage.append(
                f"关键页面/任务覆盖不足：当前覆盖率 {key_task_coverage_ratio:.0%}，缺少 {preview}"
            )
            required_actions.append(f"补充这些关键页面或状态的截图/说明：{preview}")

    verdict = "sufficient"
    delivery_status = "final_delivery_ready"
    confidence = "high"
    final_policy = mission.final_delivery_policy if mission is not None else None
    fallback_policy = mission.fallback_policy if mission is not None else None
    if blocking_reasons:
        verdict = "blocked"
        delivery_status = "blocked"
        confidence = "high"
    else:
        planned_page_ratio = plan_coverage.get("planned_page_coverage_ratio")
        planned_state_ratio = plan_coverage.get("planned_state_coverage_ratio")
        final_delivery_page_ratio = plan_coverage.get("final_delivery_page_coverage_ratio")
        final_delivery_state_ratio = plan_coverage.get("final_delivery_state_coverage_ratio")
        plan_final_ready = (
            required_plan is None
            or (
                not final_critical_path_failures
                and not final_gate_missing_pages
                and not final_gate_missing_states
                and (ocr_available or not final_gate_missing_descriptions)
                and (
                    not isinstance(final_delivery_page_ratio, float)
                    or final_policy is None
                    or final_delivery_page_ratio >= final_policy.min_page_coverage_ratio
                )
                and (
                    not isinstance(final_delivery_state_ratio, float)
                    or final_policy is None
                    or final_delivery_state_ratio >= final_policy.min_state_coverage_ratio
                )
            )
        )
        plan_fallback_ready = (
            required_plan is None
            or (
                not fallback_critical_path_failures
                and not fallback_gate_missing_pages
                and (ocr_available or not fallback_gate_missing_descriptions)
                and (
                    not isinstance(planned_page_ratio, float)
                    or fallback_policy is None
                    or planned_page_ratio >= fallback_policy.min_page_coverage_ratio
                )
                and (
                    not isinstance(planned_state_ratio, float)
                    or fallback_policy is None
                    or planned_state_ratio >= fallback_policy.min_state_coverage_ratio
                )
                and not fallback_gate_missing_states
            )
        )
        final_delivery_ready = (
            image_count >= (final_policy.min_image_count if final_policy is not None else 5)
            and readable_ratio >= (final_policy.min_readable_ratio if final_policy is not None else 0.8)
            and text_rich_ratio >= (final_policy.min_text_evidence_ratio if final_policy is not None else 0.8)
            and (
                ocr_available
                or description_link_ratio
                >= (
                    final_policy.min_description_ratio_without_ocr
                    if final_policy is not None
                    else 0.8
                )
            )
            and (
                key_task_coverage_ratio is None
                or (
                    isinstance(key_task_coverage_ratio, float)
                    and key_task_coverage_ratio >= 0.8
                )
            )
            and plan_final_ready
            and not clarification_items
        )
        fallback_safe = (
            image_count >= (fallback_policy.min_image_count if fallback_policy is not None else 1)
            and readable_ratio >= (fallback_policy.min_readable_ratio if fallback_policy is not None else 0.6)
            and text_rich_ratio
            >= (fallback_policy.min_text_evidence_ratio if fallback_policy is not None else 0.6)
            and (
                ocr_available
                or bool(description_refs)
                or (
                    fallback_policy is not None
                    and not fallback_policy.require_any_description_without_ocr
                )
            )
            and plan_fallback_ready
        )
        if final_delivery_ready:
            verdict = "sufficient"
            delivery_status = "final_delivery_ready"
            confidence = "high"
        elif fallback_safe:
            verdict = "sufficient"
            delivery_status = "fallback_safe"
            confidence = "medium"
            if required_plan is not None and (
                final_gate_missing_pages
                or final_gate_missing_states
                or final_gate_missing_descriptions
                or final_critical_path_failures
            ):
                if final_critical_path_failures:
                    verification_gaps.append(
                        "这些 critical path 仍未达到 final_delivery_ready："
                        + "；".join(final_critical_path_failures[:6])
                    )
                if final_gate_missing_pages:
                    verification_gaps.append(
                        "这些 must_capture_pages 当前仅有 provisional mapping，尚不能计入 final_delivery_ready："
                        + "；".join(final_gate_missing_pages[:6])
                    )
                if final_gate_missing_states:
                    verification_gaps.append(
                        "这些 must_capture_states 当前只被 provisional mapping 覆盖，尚不能计入 final_delivery_ready："
                        + "；".join(final_gate_missing_states[:6])
                    )
                if final_gate_missing_descriptions and not ocr_available:
                    verification_gaps.append(
                        "这些关键页面说明缺少足够强的二次验证，尚不能计入 final_delivery_ready："
                        + "；".join(final_gate_missing_descriptions[:6])
                    )
                if clarification_items:
                    verification_gaps.append(
                        "仍有少量 clarification residue 未清零，当前不能放行 final_delivery_ready："
                        + "；".join(item.relative_path for item in clarification_items[:6])
                    )
        else:
            verdict = "supplement_needed"
            delivery_status = "supplement_required"
            confidence = "medium" if image_refs else "low"

    if delivery_status == "supplement_required":
        verdict = "supplement_needed"
    if image_refs and missing_state_categories and delivery_status != "final_delivery_ready":
        required_actions.append(
            f"补充这些关键状态的截图或说明：{', '.join(missing_state_categories)}"
        )
    if delivery_status in {"fallback_safe", "supplement_required"} and not required_actions:
        required_actions.append("补关键页面截图、页面说明或 OCR 能力，以提升最终交付准确度")

    trusted_evidence_final_failures: list[str] = []
    if image_count < (final_policy.min_image_count if final_policy is not None else 5):
        trusted_evidence_final_failures.append("image_count below final threshold")
    if readable_ratio < (final_policy.min_readable_ratio if final_policy is not None else 0.8):
        trusted_evidence_final_failures.append("readable_ratio below final threshold")
    if text_rich_ratio < (final_policy.min_text_evidence_ratio if final_policy is not None else 0.8):
        trusted_evidence_final_failures.append("text_rich_ratio below final threshold")
    if (
        not ocr_available
        and description_link_ratio
        < (
            final_policy.min_description_ratio_without_ocr
            if final_policy is not None
            else 0.8
        )
    ):
        trusted_evidence_final_failures.append("description coverage below final threshold without OCR")
    if isinstance(key_task_coverage_ratio, float) and key_task_coverage_ratio < 0.8:
        trusted_evidence_final_failures.append("key_task_coverage_ratio below final threshold")
    if final_gate_missing_pages:
        trusted_evidence_final_failures.append("trusted critical page coverage still missing")
    if final_gate_missing_states:
        trusted_evidence_final_failures.append("trusted critical state coverage still missing")
    if final_gate_missing_descriptions and not ocr_available:
        trusted_evidence_final_failures.append("required descriptions still missing for final delivery")

    trusted_evidence_fallback_failures: list[str] = []
    if image_count < (fallback_policy.min_image_count if fallback_policy is not None else 1):
        trusted_evidence_fallback_failures.append("image_count below fallback threshold")
    if readable_ratio < (fallback_policy.min_readable_ratio if fallback_policy is not None else 0.6):
        trusted_evidence_fallback_failures.append("readable_ratio below fallback threshold")
    if text_rich_ratio < (fallback_policy.min_text_evidence_ratio if fallback_policy is not None else 0.6):
        trusted_evidence_fallback_failures.append("text_rich_ratio below fallback threshold")
    if (
        not ocr_available
        and not bool(description_refs)
        and (fallback_policy is None or fallback_policy.require_any_description_without_ocr)
    ):
        trusted_evidence_fallback_failures.append("no OCR and no fallback-safe description support")
    if fallback_gate_missing_pages:
        trusted_evidence_fallback_failures.append("fallback page coverage still missing")
    if fallback_gate_missing_states:
        trusted_evidence_fallback_failures.append("fallback state coverage still missing")
    if fallback_gate_missing_descriptions and not ocr_available:
        trusted_evidence_fallback_failures.append("fallback descriptions still missing without OCR")

    clarification_final_failures: list[str] = []
    if clarification_items:
        clarification_final_failures.append(
            f"{len(clarification_items)} clarification item(s) still need confirmation"
        )

    delivery_readiness_breakdown = {
        "contract_version": "2026-05-26",
        "overall_status": delivery_status,
        "final_gate_pass": delivery_status == "final_delivery_ready",
        "fallback_gate_pass": delivery_status in {"final_delivery_ready", "fallback_safe"},
        "normal_mode_target": "90%+ critical coverage with 99%-100% confidence",
        "fallback_target": "85%+ bounded confidence without pretending to be final",
        "failing_final_gates": [
            gate
            for gate, failed in (
                ("critical_path_coverage", bool(final_critical_path_failures)),
                ("trusted_evidence_sufficiency", bool(trusted_evidence_final_failures)),
                ("clarification_residue", bool(clarification_final_failures)),
            )
            if failed
        ],
        "failing_fallback_gates": [
            gate
            for gate, failed in (
                ("critical_path_coverage", bool(fallback_critical_path_failures)),
                ("trusted_evidence_sufficiency", bool(trusted_evidence_fallback_failures)),
            )
            if failed
        ],
        "next_best_action": required_actions[0] if required_actions else "",
        "gates": [
            {
                "gate": "critical_path_coverage",
                "label": "P0/P1 critical path coverage",
                "required_for_final": True,
                "required_for_fallback": True,
                "final_status": "fail" if final_critical_path_failures else "pass",
                "fallback_status": "fail" if fallback_critical_path_failures else "pass",
                "failure_reasons": _dedupe_preserve(
                    [
                        *(
                            [
                                "critical paths still block final delivery: "
                                + "；".join(final_critical_path_failures[:6])
                            ]
                            if final_critical_path_failures
                            else []
                        ),
                        *(
                            [
                                "P0 critical paths still block bounded fallback: "
                                + "；".join(fallback_critical_path_failures[:6])
                            ]
                            if fallback_critical_path_failures
                            else []
                        ),
                    ]
                ),
                "next_actions": [
                    action
                    for action in required_actions
                    if "critical path" in action or "P0" in action
                ][:3],
                "metrics": {
                    "failing_final_paths": final_critical_path_failures,
                    "failing_fallback_paths": fallback_critical_path_failures,
                    "critical_path_count": plan_coverage["critical_path_count"],
                    "p0_critical_path_count": plan_coverage["p0_critical_path_count"],
                    "p1_critical_path_count": plan_coverage["p1_critical_path_count"],
                },
            },
            {
                "gate": "trusted_evidence_sufficiency",
                "label": "Trusted evidence sufficiency",
                "required_for_final": True,
                "required_for_fallback": True,
                "final_status": "fail" if trusted_evidence_final_failures else "pass",
                "fallback_status": "fail" if trusted_evidence_fallback_failures else "pass",
                "failure_reasons": _dedupe_preserve(
                    [*trusted_evidence_final_failures, *trusted_evidence_fallback_failures]
                ),
                "next_actions": [
                    action
                    for action in required_actions
                    if "截图" in action or "说明" in action or "状态" in action or "页面" in action
                ][:4],
                "metrics": {
                    "image_count": image_count,
                    "readable_ratio": round(readable_ratio, 3),
                    "text_rich_ratio": round(text_rich_ratio, 3),
                    "description_link_ratio": round(description_link_ratio, 3),
                    "planned_page_coverage_ratio": plan_coverage["planned_page_coverage_ratio"],
                    "planned_state_coverage_ratio": plan_coverage["planned_state_coverage_ratio"],
                    "final_delivery_page_coverage_ratio": plan_coverage["final_delivery_page_coverage_ratio"],
                    "final_delivery_state_coverage_ratio": plan_coverage["final_delivery_state_coverage_ratio"],
                    "final_delivery_trusted_mapping_count": plan_coverage["final_delivery_trusted_mapping_count"],
                },
            },
            {
                "gate": "clarification_residue",
                "label": "Clarification residue",
                "required_for_final": True,
                "required_for_fallback": False,
                "final_status": "fail" if clarification_final_failures else "pass",
                "fallback_status": "pass",
                "failure_reasons": clarification_final_failures,
                "next_actions": [
                    action
                    for action in required_actions
                    if "歧义截图" in action or "确认" in action
                ][:2],
                "metrics": {
                    "clarification_needed_count": len(clarification_items),
                    "clarification_unlocks_final_count": len(
                        [item for item in clarification_items if item.unlocks_final_delivery]
                    ),
                    "clarification_relative_paths": [item.relative_path for item in clarification_items],
                },
            },
            {
                "gate": "issue_qualification",
                "label": "Issue-level qualification",
                "required_for_final": False,
                "required_for_fallback": False,
                "final_status": "pending",
                "fallback_status": "pending",
                "failure_reasons": [],
                "next_actions": [],
                "metrics": {
                    "status": "resolved downstream by delivery audit",
                },
            },
        ],
    }

    coverage_summary = {
        "image_count": image_count,
        "description_count": len(description_refs),
        "readable_image_count": len(readable_refs),
        "text_rich_image_count": len(text_rich_refs),
        "readable_ratio": round(readable_ratio, 3),
        "text_rich_ratio": round(text_rich_ratio, 3),
        "description_link_ratio": round(description_link_ratio, 3),
        "ocr_text_ratio": round(ocr_text_ratio, 3),
        "task_count": task_coverage["task_count"],
        "matched_task_count": task_coverage["matched_task_count"],
        "key_task_coverage_ratio": (
            round(plan_coverage["planned_page_coverage_ratio"], 3)
            if required_plan is not None and isinstance(plan_coverage["planned_page_coverage_ratio"], float)
            else round(task_coverage["key_task_coverage_ratio"], 3)
            if isinstance(task_coverage["key_task_coverage_ratio"], float)
            else None
        ),
        "matched_tasks": (
            [
                requirement.page_name
                for requirement in required_plan.critical_pages
                if requirement.page_name not in plan_missing_pages
            ]
            if required_plan is not None
            else task_coverage["matched_tasks"]
        ),
        "missing_tasks": plan_missing_pages if required_plan is not None else task_coverage["missing_tasks"],
        "low_readability_paths": low_readability_paths,
        "missing_description_paths": missing_description_paths,
        "missing_ocr_paths": missing_ocr_paths,
        "missing_state_categories": missing_state_categories,
        "text_evidence_missing_paths": text_evidence_missing_paths,
        "required_evidence_plan_version": required_plan.plan_version if required_plan is not None else None,
        "capture_mission_version": plan_coverage["capture_mission_version"],
        "capture_mission_path": plan_coverage["capture_mission_path"],
        "critical_flows": plan_coverage["critical_flows"],
        "critical_path_count": plan_coverage["critical_path_count"],
        "p0_critical_path_count": plan_coverage["p0_critical_path_count"],
        "p1_critical_path_count": plan_coverage["p1_critical_path_count"],
        "p2_critical_path_count": plan_coverage["p2_critical_path_count"],
        "missing_p0_pages": plan_coverage["missing_p0_pages"],
        "missing_p0_states": plan_coverage["missing_p0_states"],
        "missing_p1_pages": plan_coverage["missing_p1_pages"],
        "missing_p1_states": plan_coverage["missing_p1_states"],
        "must_capture_pages": plan_coverage["must_capture_pages"],
        "must_capture_states": plan_coverage["must_capture_states"],
        "nice_to_have_pages": plan_coverage["nice_to_have_pages"],
        "capture_order": plan_coverage["capture_order"],
        "final_delivery_pass_line": plan_coverage["final_delivery_pass_line"],
        "fallback_pass_line": plan_coverage["fallback_pass_line"],
        "evidence_rationale": plan_coverage["evidence_rationale"],
        "final_delivery_missing_critical_paths": final_critical_path_failures,
        "fallback_missing_critical_paths": fallback_critical_path_failures,
        "planned_page_count": plan_coverage["planned_page_count"],
        "matched_planned_page_count": plan_coverage["matched_planned_page_count"],
        "planned_page_coverage_ratio": plan_coverage["planned_page_coverage_ratio"],
        "missing_critical_pages": plan_missing_pages,
        "planned_state_count": plan_coverage["planned_state_count"],
        "covered_planned_state_count": plan_coverage["covered_planned_state_count"],
        "planned_state_coverage_ratio": plan_coverage["planned_state_coverage_ratio"],
        "missing_planned_states": plan_missing_states,
        "missing_required_description_pages": plan_missing_descriptions,
        "final_delivery_matched_planned_page_count": plan_coverage["final_delivery_matched_planned_page_count"],
        "final_delivery_page_coverage_ratio": plan_coverage["final_delivery_page_coverage_ratio"],
        "final_delivery_missing_critical_pages": final_plan_missing_pages,
        "final_delivery_covered_planned_state_count": plan_coverage["final_delivery_covered_planned_state_count"],
        "final_delivery_state_coverage_ratio": plan_coverage["final_delivery_state_coverage_ratio"],
        "final_delivery_missing_planned_states": final_plan_missing_states,
        "final_delivery_missing_required_description_pages": final_plan_missing_descriptions,
        "naming_issues": plan_naming_issues,
        "draft_mapping_count": len([ref for ref in image_refs if ref.draft_mapping is not None]),
        "final_delivery_trusted_mapping_count": plan_coverage["final_delivery_trusted_mapping_count"],
        "fusion_trusted_page_mapping_count": len(fusion_summary.trusted_page_mappings),
        "fusion_trusted_state_mapping_count": len(fusion_summary.trusted_state_mappings),
        "fusion_provisional_mapping_count": len(fusion_summary.provisional_mappings),
        "fusion_conflict_count": len(conflicting_groups),
        "fusion_unresolved_ambiguity_count": len(clarification_items),
        "fusion_conflicting_paths": [group.relative_path for group in conflicting_groups],
        "fusion_unresolved_paths": [item.relative_path for item in clarification_items],
        "clarification_needed_count": len(clarification_items),
        "clarification_relative_paths": [item.relative_path for item in clarification_items],
        "clarification_unlocks_final_count": len(
            [item for item in clarification_items if item.unlocks_final_delivery]
        ),
        "clarification_suppressed_reason": clarification_suppressed_reason,
        "task_checklist_missing_tasks": task_coverage["missing_tasks"],
        "generic_missing_state_categories": generic_missing_state_categories,
        "normal_mode_quality_target": "99%-100%",
        "fallback_quality_target": "85%+",
    }

    return EvidenceAssessment(
        verdict=verdict,  # type: ignore[arg-type]
        delivery_status=delivery_status,  # type: ignore[arg-type]
        final_delivery_ready=delivery_status == "final_delivery_ready",
        fallback_safe=delivery_status == "fallback_safe",
        confidence=confidence,  # type: ignore[arg-type]
        source_channel="mixed" if ocr_available or description_refs else "metadata",
        evidence_basis=basis,
        blocking_reasons=_dedupe_preserve(blocking_reasons),
        required_actions=_dedupe_preserve(required_actions),
        missing_coverage=_dedupe_preserve(missing_coverage),
        coverage_summary=coverage_summary,
        unsupported=[
            "full page semantic summary",
            "automatic task_id attribution",
            "automatic module_id attribution",
            "automatic scenario intent inference",
        ],
        unknown=["unseen interaction states not covered by screenshots"] if image_refs else [],
        verification_gaps=_dedupe_preserve(
            [
                *verification_gaps,
                *(
                    []
                    if mission is None or delivery_status == "final_delivery_ready"
                    else [f"final pass line: {line}" for line in mission.final_delivery_pass_line]
                ),
                *(
                    []
                    if mission is None or delivery_status == "blocked"
                    else [f"fallback pass line: {line}" for line in mission.fallback_pass_line]
                ),
            ]
        ),
        clarification_items=clarification_items,
        critical_path_coverage_summary=critical_path_coverage_summary,
        fusion_summary=fusion_summary,
        delivery_readiness_breakdown=delivery_readiness_breakdown,
    )


def _analysis_summary(
    refs: list[ScreenshotRef],
    *,
    ocr_available: bool,
    ocr_backend: str | None,
    evidence_assessment: EvidenceAssessment,
    remediation_summary: dict[str, Any] | None = None,
) -> ImageAnalysisSummary:
    fusion_summary = evidence_assessment.fusion_summary
    low_readability_ids = [
        ref.id
        for ref in refs
        if ref.kind == "image" and ref.readability.level in {"low", "unreadable"}
    ]
    signal_warning_ids = [ref.id for ref in refs if ref.signal_warnings]
    linked_description_ids = [ref.id for ref in refs if ref.kind == "image" and ref.description_links]
    ocr_text_ids = [ref.id for ref in refs if ref.kind == "image" and ref.ocr_text_lines]
    return ImageAnalysisSummary(
        capabilities=[
            "recursive screenshot and markdown description discovery",
            "stable ids with relative and absolute paths",
            "image format, file size, and pixel-dimension extraction",
            "resolution-based readability and quality assessment",
            "markdown description preview extraction",
            "OCR text extraction when a local backend is available",
            "best-effort page-title, button, navigation and state-text cue extraction",
            "best-effort screenshot-to-description linking",
            "draft screenshot-to-page/state auto-mapping with traceable confidence",
            "minimal clarification package generation for only ambiguous screenshots",
            "input sufficiency assessment for client-mode evidence",
            "targeted evidence acquisition planning that ranks the next highest-value supplement actions",
        ],
        limitations=[
            "no full semantic scene understanding or page summarization",
            "no automatic task_id attribution from screenshots",
            "no automatic module_id attribution from screenshots",
            "no scenario-intent inference unless explicitly evidenced in OCR or markdown",
            "no pixel-level sensitive-content redaction; flagged items still require manual review",
        ],
        confidence="high" if ocr_available else "medium",
        source_channel="mixed" if ocr_available else "metadata",
        evidence_basis=evidence_assessment.evidence_basis,
        semantic_analysis_available=False,
        ocr_available=ocr_available,
        ocr_backend=ocr_backend,
        unsupported=evidence_assessment.unsupported,
        unknown=evidence_assessment.unknown,
        verification_gaps=evidence_assessment.verification_gaps,
        summary={
            "total_files": len(refs),
            "image_count": len([ref for ref in refs if ref.kind == "image"]),
            "description_count": len([ref for ref in refs if ref.kind == "description"]),
            "low_readability_count": len(low_readability_ids),
            "signal_warning_count": len(signal_warning_ids),
            "ocr_text_image_count": len(ocr_text_ids),
            "description_linked_image_count": len(linked_description_ids),
            "low_readability_ids": low_readability_ids,
            "signal_warning_ids": signal_warning_ids,
            "ocr_text_ids": ocr_text_ids,
            "description_linked_ids": linked_description_ids,
            "draft_mapping_count": len(
                [ref for ref in refs if ref.kind == "image" and ref.draft_mapping is not None]
            ),
            "clarification_needed_count": len(evidence_assessment.clarification_items),
            "capture_mission_version": evidence_assessment.coverage_summary.get("capture_mission_version"),
            "capture_mission_path": evidence_assessment.coverage_summary.get("capture_mission_path"),
            "final_delivery_pass_line": evidence_assessment.coverage_summary.get("final_delivery_pass_line", []),
            "fallback_pass_line": evidence_assessment.coverage_summary.get("fallback_pass_line", []),
            "critical_path_count": evidence_assessment.coverage_summary.get("critical_path_count"),
            "final_delivery_missing_critical_paths": evidence_assessment.coverage_summary.get(
                "final_delivery_missing_critical_paths",
                [],
            ),
            "fallback_missing_critical_paths": evidence_assessment.coverage_summary.get(
                "fallback_missing_critical_paths",
                [],
            ),
            "fusion_trusted_page_mapping_count": len(fusion_summary.trusted_page_mappings)
            if fusion_summary is not None
            else 0,
            "fusion_trusted_state_mapping_count": len(fusion_summary.trusted_state_mappings)
            if fusion_summary is not None
            else 0,
            "fusion_provisional_mapping_count": len(fusion_summary.provisional_mappings)
            if fusion_summary is not None
            else 0,
            "fusion_conflict_count": len(fusion_summary.conflicting_evidence_groups)
            if fusion_summary is not None
            else 0,
            "fusion_unresolved_ambiguity_count": len(fusion_summary.unresolved_ambiguities)
            if fusion_summary is not None
            else 0,
            "targeted_acquisition_must_count": len(
                evidence_assessment.targeted_acquisition_plan.must_acquire_now
            )
            if evidence_assessment.targeted_acquisition_plan is not None
            else 0,
            "targeted_acquisition_clarify_count": len(
                evidence_assessment.targeted_acquisition_plan.clarify_existing_evidence
            )
            if evidence_assessment.targeted_acquisition_plan is not None
            else 0,
            "targeted_acquisition_top_targets": [
                item.target_page
                for item in evidence_assessment.targeted_acquisition_plan.highest_value_next_captures
            ]
            if evidence_assessment.targeted_acquisition_plan is not None
            else [],
            "client_mode_metrics_contract_version": (
                evidence_assessment.client_mode_metrics.contract_version
                if evidence_assessment.client_mode_metrics is not None
                else None
            ),
            "benchmark_contract_version": (
                evidence_assessment.benchmark_summary.contract_version
                if evidence_assessment.benchmark_summary is not None
                else None
            ),
            "benchmark_delivery_status": (
                evidence_assessment.benchmark_summary.delivery_status
                if evidence_assessment.benchmark_summary is not None
                else evidence_assessment.delivery_status
            ),
            "benchmark_input_quality_class": (
                evidence_assessment.benchmark_summary.input_quality_class
                if evidence_assessment.benchmark_summary is not None
                else None
            ),
            "benchmark_markdown_path": evidence_assessment.coverage_summary.get(
                "benchmark_markdown_path"
            ),
            **(remediation_summary or {}),
        },
    )


def _critical_path_breakdown_snapshot(
    assessment: EvidenceAssessment,
) -> dict[str, Any]:
    summary = assessment.critical_path_coverage_summary
    coverage_summary = assessment.coverage_summary
    if not isinstance(summary, CriticalPathCoverageSummary):
        return {
            "critical_path_count": _coerce_int(coverage_summary.get("critical_path_count", 0)),
            "final_passed_count": 0,
            "fallback_passed_count": 0,
            "final_pass_ratio": 0.0,
            "fallback_pass_ratio": 0.0,
            "failing_final_paths": [],
            "failing_fallback_paths": [],
        }
    records = list(summary.critical_paths)
    total = len(records)
    final_passed = len([record for record in records if record.final_delivery_pass])
    fallback_passed = len([record for record in records if record.fallback_pass])
    return {
        "critical_path_count": total,
        "final_passed_count": final_passed,
        "fallback_passed_count": fallback_passed,
        "final_pass_ratio": round(final_passed / total, 3) if total else 0.0,
        "fallback_pass_ratio": round(fallback_passed / total, 3) if total else 0.0,
        "failing_final_paths": list(summary.failing_final_paths),
        "failing_fallback_paths": list(summary.failing_fallback_paths),
    }


def _trusted_mapping_rate_snapshot(
    assessment: EvidenceAssessment,
) -> dict[str, Any]:
    summary = assessment.coverage_summary
    planned_page_count = _coerce_int(summary.get("planned_page_count", 0))
    trusted_mapping_count = _coerce_int(summary.get("final_delivery_trusted_mapping_count", 0))
    draft_mapping_count = _coerce_int(summary.get("draft_mapping_count", 0))
    trusted_rate = _bounded_rate(trusted_mapping_count, planned_page_count)
    return {
        "planned_page_count": planned_page_count,
        "trusted_mapping_count": trusted_mapping_count,
        "draft_mapping_count": draft_mapping_count,
        "trusted_mapping_rate": trusted_rate,
    }


def _supplement_cause_classification(
    assessment: EvidenceAssessment,
) -> list[str]:
    summary = assessment.coverage_summary
    causes: list[str] = []
    image_count = _coerce_int(summary.get("image_count", 0))
    planned_page_count = _coerce_int(summary.get("planned_page_count", 0))
    readable_ratio = _coerce_float(summary.get("readable_ratio", 0.0))
    missing_pages = _coerce_string_list(summary.get("missing_critical_pages"))
    missing_states = _coerce_string_list(summary.get("missing_planned_states"))
    missing_descriptions = _coerce_string_list(summary.get("missing_required_description_pages"))
    final_missing_pages = _coerce_string_list(summary.get("final_delivery_missing_critical_pages"))
    final_missing_states = _coerce_string_list(summary.get("final_delivery_missing_planned_states"))
    final_path_failures = _coerce_string_list(summary.get("final_delivery_missing_critical_paths"))
    clarification_paths = _coerce_string_list(summary.get("clarification_relative_paths"))
    unresolved_ambiguity_count = _coerce_int(summary.get("fusion_unresolved_ambiguity_count", 0))
    conflict_count = _coerce_int(summary.get("fusion_conflict_count", 0))

    min_image_target = min(5, planned_page_count) if planned_page_count else 5
    if image_count < min_image_target or missing_pages or missing_states or missing_descriptions:
        causes.append("missing_evidence")
    if readable_ratio < 0.8 or _coerce_string_list(summary.get("low_readability_paths")):
        causes.append("weak_readability")
    if clarification_paths or unresolved_ambiguity_count > 0:
        causes.append("mapping_unresolved")
    if (
        conflict_count > 0
        or (
            (final_missing_pages or final_missing_states)
            and not (missing_pages or missing_states)
        )
        or (
            _coerce_int(summary.get("final_delivery_trusted_mapping_count", 0))
            < _coerce_int(summary.get("matched_planned_page_count", 0))
            and image_count >= min_image_target
        )
    ):
        causes.append("fusion_insufficient")
    if final_path_failures:
        causes.append("critical_path_not_met")
    return _dedupe_preserve(causes)


def _first_pass_success_breakdown(
    *,
    baseline_assessment: EvidenceAssessment,
    evidence_assessment: EvidenceAssessment,
    remediation_summary: dict[str, Any],
) -> dict[str, Any]:
    supplement_causes = _supplement_cause_classification(evidence_assessment)
    baseline_status = baseline_assessment.delivery_status
    final_status = evidence_assessment.delivery_status
    first_pass_final = baseline_status == "final_delivery_ready"
    improved = baseline_status != final_status
    if first_pass_final:
        diagnosis = "already_good_enough"
    elif improved and final_status in {"final_delivery_ready", "fallback_safe"}:
        diagnosis = "existing_input_was_salvageable_but_needed_better_ingestion"
    elif any(cause in {"missing_evidence", "weak_readability", "critical_path_not_met"} for cause in supplement_causes):
        diagnosis = "input_truly_insufficient"
    elif any(cause in {"fusion_insufficient", "mapping_unresolved"} for cause in supplement_causes):
        diagnosis = "system_still_cannot_fully_consume_existing_input"
    else:
        diagnosis = "mixed_gap_profile"

    clarification_needed_count = len(evidence_assessment.clarification_items)
    image_count = _coerce_int(evidence_assessment.coverage_summary.get("image_count", 0))
    return {
        "contract_version": "2026-05-26",
        "first_pass_final_rate": 1.0 if first_pass_final else 0.0,
        "first_pass_final": first_pass_final,
        "baseline_delivery_status": baseline_status,
        "post_remediation_delivery_status": final_status,
        "pre_remediation_critical_path_coverage": _critical_path_breakdown_snapshot(baseline_assessment),
        "post_remediation_critical_path_coverage": _critical_path_breakdown_snapshot(evidence_assessment),
        "pre_remediation_trusted_mapping": _trusted_mapping_rate_snapshot(baseline_assessment),
        "post_remediation_trusted_mapping": _trusted_mapping_rate_snapshot(evidence_assessment),
        "clarification_burden": {
            "clarification_needed_count": clarification_needed_count,
            "clarification_unlocks_final_count": _coerce_int(
                evidence_assessment.coverage_summary.get("clarification_unlocks_final_count", 0)
            ),
            "clarification_burden_ratio": round(
                clarification_needed_count / image_count, 3
            )
            if image_count
            else 0.0,
        },
        "supplement_cause_classification": supplement_causes,
        "upstream_diagnosis": diagnosis,
        "auto_remediation_attempted": bool(remediation_summary.get("auto_remediation_attempted", False)),
        "auto_remediation_changed": bool(remediation_summary.get("auto_remediation_changed", False)),
        "next_best_action": evidence_assessment.required_actions[0] if evidence_assessment.required_actions else "",
    }


def _priority_critical_path_rates(
    assessment: EvidenceAssessment,
    *,
    priority: str,
) -> tuple[float, float]:
    records = [
        record
        for record in _critical_path_records(assessment)
        if record.priority == priority
    ]
    if not records:
        return 0.0, 0.0
    page_values = [float(record.final_delivery_page_coverage_ratio or 0.0) for record in records]
    state_values = [float(record.final_delivery_state_coverage_ratio or 0.0) for record in records]
    return (
        round(sum(page_values) / len(page_values), 3) if page_values else 0.0,
        round(sum(state_values) / len(state_values), 3) if state_values else 0.0,
    )


def _critical_path_records(
    assessment: EvidenceAssessment,
) -> list[CriticalPathCoverageRecord]:
    summary = assessment.critical_path_coverage_summary
    if not isinstance(summary, CriticalPathCoverageSummary):
        return []
    return list(summary.critical_paths)


def _critical_path_hit_rates(
    assessment: EvidenceAssessment,
) -> tuple[float, float]:
    records = [
        record
        for record in _critical_path_records(assessment)
        if record.gates_final_delivery
    ] or _critical_path_records(assessment)
    if not records:
        return 0.0, 0.0
    page_values = [
        float(record.final_delivery_page_coverage_ratio or 0.0)
        for record in records
    ]
    state_values = [
        float(record.final_delivery_state_coverage_ratio or 0.0)
        for record in records
    ]
    return (
        round(sum(page_values) / len(page_values), 3) if page_values else 0.0,
        round(sum(state_values) / len(state_values), 3) if state_values else 0.0,
    )


def _bounded_rate(numerator: float, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(min(1.0, numerator / denominator), 3)


def _input_quality_class(assessment: EvidenceAssessment) -> str:
    first_pass = (
        assessment.first_pass_success_breakdown
        if isinstance(assessment.first_pass_success_breakdown, dict)
        else {}
    )
    diagnosis = str(first_pass.get("upstream_diagnosis", ""))
    supplement_causes = {
        str(cause)
        for cause in first_pass.get("supplement_cause_classification", [])
    }
    if assessment.delivery_status == "final_delivery_ready":
        return "high_quality" if bool(first_pass.get("first_pass_final", False)) else "salvageable"
    if assessment.delivery_status == "blocked":
        return "blocked"
    if "weak_readability" in supplement_causes:
        return "weak_readability"
    if "missing_evidence" in supplement_causes or diagnosis == "input_truly_insufficient":
        return "missing_evidence"
    if "mapping_unresolved" in supplement_causes or assessment.clarification_items:
        return "clarification_limited"
    if (
        "fusion_insufficient" in supplement_causes
        or diagnosis == "system_still_cannot_fully_consume_existing_input"
    ):
        return "fusion_limited"
    if diagnosis == "existing_input_was_salvageable_but_needed_better_ingestion":
        return "salvageable"
    return "mixed"


def _auto_remediation_lift(first_pass_success_breakdown: dict[str, Any]) -> float:
    pre_critical = _coerce_float(
        first_pass_success_breakdown.get("pre_remediation_critical_path_coverage", {}).get(
            "final_pass_ratio",
            0.0,
        )
        if isinstance(first_pass_success_breakdown.get("pre_remediation_critical_path_coverage"), dict)
        else 0.0
    )
    post_critical = _coerce_float(
        first_pass_success_breakdown.get("post_remediation_critical_path_coverage", {}).get(
            "final_pass_ratio",
            0.0,
        )
        if isinstance(first_pass_success_breakdown.get("post_remediation_critical_path_coverage"), dict)
        else 0.0
    )
    pre_trusted = _coerce_float(
        first_pass_success_breakdown.get("pre_remediation_trusted_mapping", {}).get(
            "trusted_mapping_rate",
            0.0,
        )
        if isinstance(first_pass_success_breakdown.get("pre_remediation_trusted_mapping"), dict)
        else 0.0
    )
    post_trusted = _coerce_float(
        first_pass_success_breakdown.get("post_remediation_trusted_mapping", {}).get(
            "trusted_mapping_rate",
            0.0,
        )
        if isinstance(first_pass_success_breakdown.get("post_remediation_trusted_mapping"), dict)
        else 0.0
    )
    return round(((post_critical - pre_critical) + (post_trusted - pre_trusted)) / 2, 3)


def _salvageable_input_rate(first_pass_success_breakdown: dict[str, Any]) -> float:
    diagnosis = str(first_pass_success_breakdown.get("upstream_diagnosis", ""))
    if diagnosis in {"already_good_enough", "existing_input_was_salvageable_but_needed_better_ingestion"}:
        return 1.0
    if diagnosis == "system_still_cannot_fully_consume_existing_input":
        return 0.75
    if diagnosis == "mixed_gap_profile":
        return 0.5
    return 0.0


def _supplement_request_precision(
    assessment: EvidenceAssessment,
) -> float:
    plan = assessment.targeted_acquisition_plan
    if not isinstance(plan, TargetedAcquisitionPlan):
        return 1.0 if assessment.delivery_status == "final_delivery_ready" else 0.0
    total_actions = (
        len(plan.must_acquire_now)
        + len(plan.clarify_existing_evidence)
        + len(plan.nice_to_have_later)
    )
    if total_actions == 0:
        return 1.0 if assessment.delivery_status == "final_delivery_ready" else 0.0
    return round(len(plan.highest_value_next_captures) / total_actions, 3)


def _low_value_work_return_rate(assessment: EvidenceAssessment) -> float:
    plan = assessment.targeted_acquisition_plan
    required_actions = list(assessment.required_actions)
    low_value_hits = 0
    for action in required_actions:
        lowered = action.lower()
        if "重命名" in action or "rename" in lowered:
            low_value_hits += 1
        if "整套 mapping" in action or "完整 mapping" in action:
            low_value_hits += 1
    if isinstance(plan, TargetedAcquisitionPlan):
        low_value_hits += len(
            [
                item
                for item in plan.nice_to_have_later
                if item.suggested_input_form in {"screenshot", "markdown_description"}
                and not item.expected_unlocks_final_delivery
            ]
        )
        denominator = max(
            1,
            len(required_actions)
            + len(plan.must_acquire_now)
            + len(plan.clarify_existing_evidence)
            + len(plan.nice_to_have_later),
        )
    else:
        denominator = max(1, len(required_actions))
    return round(low_value_hits / denominator, 3)


def _client_mode_metrics(
    assessment: EvidenceAssessment,
) -> ClientModeMetrics:
    first_pass = (
        assessment.first_pass_success_breakdown
        if isinstance(assessment.first_pass_success_breakdown, dict)
        else {}
    )
    coverage_summary = assessment.coverage_summary
    page_hit_rate, state_hit_rate = _critical_path_hit_rates(assessment)
    p0_page_coverage, p0_state_coverage = _priority_critical_path_rates(assessment, priority="P0")
    p1_page_coverage, p1_state_coverage = _priority_critical_path_rates(assessment, priority="P1")
    trusted_snapshot = _trusted_mapping_rate_snapshot(assessment)
    planned_page_count = max(1, _coerce_int(coverage_summary.get("planned_page_count", 0)))
    provisional_mapping_rate = _bounded_rate(
        _coerce_int(coverage_summary.get("fusion_provisional_mapping_count", 0)),
        planned_page_count,
    )
    conflicting_mapping_rate = _bounded_rate(
        _coerce_int(coverage_summary.get("fusion_conflict_count", 0)),
        planned_page_count,
    )

    coverage_metrics = CoverageMetrics(
        critical_path_page_hit_rate=page_hit_rate,
        critical_path_state_hit_rate=state_hit_rate,
        p0_page_coverage=p0_page_coverage,
        p0_state_coverage=p0_state_coverage,
        p1_page_coverage=p1_page_coverage,
        p1_state_coverage=p1_state_coverage,
    )
    trust_metrics = TrustMetrics(
        trusted_mapping_rate=_coerce_float(trusted_snapshot.get("trusted_mapping_rate", 0.0)),
        provisional_mapping_rate=provisional_mapping_rate,
        conflicting_mapping_rate=conflicting_mapping_rate,
        unverified_leakage_rate=0.0,
    )
    success_metrics = SuccessThroughputMetrics(
        final_delivery_ready_rate=1.0 if assessment.delivery_status == "final_delivery_ready" else 0.0,
        fallback_safe_rate=1.0 if assessment.delivery_status == "fallback_safe" else 0.0,
        supplement_required_rate=1.0 if assessment.delivery_status == "supplement_required" else 0.0,
        blocked_rate=1.0 if assessment.delivery_status == "blocked" else 0.0,
        first_pass_final_rate=_coerce_float(first_pass.get("first_pass_final_rate", 0.0)),
        auto_remediation_lift=_auto_remediation_lift(first_pass),
        salvageable_input_rate=_salvageable_input_rate(first_pass),
    )
    human_burden_metrics = HumanBurdenMetrics(
        clarification_item_count=len(assessment.clarification_items),
        supplement_request_precision=_supplement_request_precision(assessment),
        low_value_work_return_rate=_low_value_work_return_rate(assessment),
    )
    return ClientModeMetrics(
        contract_version=_BENCHMARK_CONTRACT_VERSION,
        run_mode="client",
        input_quality_class=_input_quality_class(assessment),
        delivery_status=assessment.delivery_status,
        confidence="high" if assessment.delivery_status == "final_delivery_ready" else "medium",
        source_channel="mixed",
        evidence_basis=[
            f"critical_path_page_hit_rate={page_hit_rate:.3f}",
            f"critical_path_state_hit_rate={state_hit_rate:.3f}",
            f"trusted_mapping_rate={trust_metrics.trusted_mapping_rate:.3f}",
            f"auto_remediation_lift={success_metrics.auto_remediation_lift:.3f}",
        ],
        coverage_metrics=coverage_metrics,
        trust_metrics=trust_metrics,
        success_metrics=success_metrics,
        human_burden_metrics=human_burden_metrics,
        metric_notes={
            "unverified_leakage_rate": (
                "image-analyzer stage cannot yet see the final main issue list; "
                "downstream delivery audit should overwrite this metric with audited issue leakage."
            ),
        },
    )


def _metric_delta_note(metric: str, current: float, target: float) -> str | None:
    if current >= target:
        return None
    return f"{metric} still needs +{target - current:.3f} to reach {target:.2f}"


def _benchmark_root_cause(assessment: EvidenceAssessment) -> str:
    first_pass = (
        assessment.first_pass_success_breakdown
        if isinstance(assessment.first_pass_success_breakdown, dict)
        else {}
    )
    diagnosis = str(first_pass.get("upstream_diagnosis", ""))
    if diagnosis == "input_truly_insufficient":
        return "input_truly_insufficient"
    if diagnosis in {
        "system_still_cannot_fully_consume_existing_input",
        "existing_input_was_salvageable_but_needed_better_ingestion",
    }:
        return "system_ingestion_gap"
    if diagnosis == "already_good_enough":
        return "already_good_enough"
    return "mixed_gap_profile"


def _client_mode_benchmark_summary(
    assessment: EvidenceAssessment,
    metrics: ClientModeMetrics,
) -> BenchmarkSummary:
    breakdown = (
        assessment.delivery_readiness_breakdown
        if isinstance(assessment.delivery_readiness_breakdown, dict)
        else {}
    )
    failing_gates = [
        str(gate)
        for gate in breakdown.get("failing_final_gates", [])
        if isinstance(gate, str)
    ]
    met_metrics = [
        "delivery_status.final_delivery_ready"
        if metrics.success_metrics.final_delivery_ready_rate == 1.0
        else "delivery_status.bounded_or_lower",
        *(
            ["critical_path_page_hit_rate>=0.90"]
            if metrics.coverage_metrics.critical_path_page_hit_rate >= 0.9
            else []
        ),
        *(
            ["critical_path_state_hit_rate>=0.90"]
            if metrics.coverage_metrics.critical_path_state_hit_rate >= 0.9
            else []
        ),
        *(
            ["trusted_mapping_rate>=0.90"]
            if metrics.trust_metrics.trusted_mapping_rate >= 0.9
            else []
        ),
        *(
            ["clarification_item_count==0"]
            if metrics.human_burden_metrics.clarification_item_count == 0
            else []
        ),
        *(
            ["low_value_work_return_rate<=0.10"]
            if metrics.human_burden_metrics.low_value_work_return_rate <= 0.1
            else []
        ),
    ]
    unmet_metrics = [
        *(
            ["critical_path_page_hit_rate<0.90"]
            if metrics.coverage_metrics.critical_path_page_hit_rate < 0.9
            else []
        ),
        *(
            ["critical_path_state_hit_rate<0.90"]
            if metrics.coverage_metrics.critical_path_state_hit_rate < 0.9
            else []
        ),
        *(
            ["trusted_mapping_rate<0.90"]
            if metrics.trust_metrics.trusted_mapping_rate < 0.9
            else []
        ),
        *(
            ["clarification_item_count>0"]
            if metrics.human_burden_metrics.clarification_item_count > 0
            else []
        ),
        *(
            ["unverified_leakage_rate>0.00"]
            if metrics.trust_metrics.unverified_leakage_rate > 0.0
            else []
        ),
        *[f"gate:{gate}" for gate in failing_gates],
    ]
    distance_to_90_plus = _dedupe_preserve(
        [
            note
            for note in [
                _metric_delta_note(
                    "critical_path_page_hit_rate",
                    metrics.coverage_metrics.critical_path_page_hit_rate,
                    0.9,
                ),
                _metric_delta_note(
                    "critical_path_state_hit_rate",
                    metrics.coverage_metrics.critical_path_state_hit_rate,
                    0.9,
                ),
                _metric_delta_note(
                    "trusted_mapping_rate",
                    metrics.trust_metrics.trusted_mapping_rate,
                    0.9,
                ),
                (
                    f"clarification residue still has {metrics.human_burden_metrics.clarification_item_count} item(s)"
                    if metrics.human_burden_metrics.clarification_item_count > 0
                    else None
                ),
                *[
                    f"final gate still fails at {gate}"
                    for gate in failing_gates
                ],
            ]
            if note
        ]
    )
    root_cause = _benchmark_root_cause(assessment)
    headline = {
        "final_delivery_ready": "当前 run 已达到 normal mode 最终交付标准。",
        "fallback_safe": "当前 run 只达到 bounded fallback，不能冒充 final。",
        "supplement_required": "当前 run 仍需补充关键证据后才能继续逼近 final。",
        "blocked": "当前 run 被阻断，现有输入不足以形成可信 client-mode 结论。",
    }.get(assessment.delivery_status, "当前 run 仍需进一步诊断。")
    return BenchmarkSummary(
        contract_version=_BENCHMARK_CONTRACT_VERSION,
        run_mode="client",
        input_quality_class=metrics.input_quality_class,
        delivery_status=assessment.delivery_status,
        confidence="high" if assessment.delivery_status == "final_delivery_ready" else "medium",
        source_channel="mixed",
        evidence_basis=[
            f"delivery_status={assessment.delivery_status}",
            f"root_cause={root_cause}",
            f"first_pass_final_rate={metrics.success_metrics.first_pass_final_rate:.3f}",
            f"auto_remediation_lift={metrics.success_metrics.auto_remediation_lift:.3f}",
        ],
        metrics=metrics,
        met_metrics=_dedupe_preserve(met_metrics),
        unmet_metrics=_dedupe_preserve(unmet_metrics),
        distance_to_90_plus=distance_to_90_plus,
        root_cause=root_cause,
        next_best_action=assessment.required_actions[0] if assessment.required_actions else "",
        summary_headline=headline,
        artifact_paths={},
    )


def _render_benchmark_summary_markdown(
    *,
    summary: BenchmarkSummary,
) -> str:
    metrics = summary.metrics
    lines = [
        "# Client Mode Benchmark Summary",
        "",
        f"- contract_version: {summary.contract_version}",
        f"- run_mode: {summary.run_mode}",
        f"- input_quality_class: {summary.input_quality_class}",
        f"- delivery_status: {summary.delivery_status}",
        f"- summary_headline: {summary.summary_headline}",
        f"- root_cause: {summary.root_cause}",
    ]
    if summary.next_best_action:
        lines.append(f"- next_best_action: {summary.next_best_action}")

    lines.extend(
        [
            "",
            "## Coverage metrics",
            f"- critical_path_page_hit_rate: {metrics.coverage_metrics.critical_path_page_hit_rate:.3f}",
            f"- critical_path_state_hit_rate: {metrics.coverage_metrics.critical_path_state_hit_rate:.3f}",
            f"- p0_page_coverage: {metrics.coverage_metrics.p0_page_coverage:.3f}",
            f"- p0_state_coverage: {metrics.coverage_metrics.p0_state_coverage:.3f}",
            f"- p1_page_coverage: {metrics.coverage_metrics.p1_page_coverage:.3f}",
            f"- p1_state_coverage: {metrics.coverage_metrics.p1_state_coverage:.3f}",
            "",
            "## Trust metrics",
            f"- trusted_mapping_rate: {metrics.trust_metrics.trusted_mapping_rate:.3f}",
            f"- provisional_mapping_rate: {metrics.trust_metrics.provisional_mapping_rate:.3f}",
            f"- conflicting_mapping_rate: {metrics.trust_metrics.conflicting_mapping_rate:.3f}",
            f"- unverified_leakage_rate: {metrics.trust_metrics.unverified_leakage_rate:.3f}",
            "",
            "## Success / throughput metrics",
            f"- final_delivery_ready_rate: {metrics.success_metrics.final_delivery_ready_rate:.3f}",
            f"- fallback_safe_rate: {metrics.success_metrics.fallback_safe_rate:.3f}",
            f"- supplement_required_rate: {metrics.success_metrics.supplement_required_rate:.3f}",
            f"- blocked_rate: {metrics.success_metrics.blocked_rate:.3f}",
            f"- first_pass_final_rate: {metrics.success_metrics.first_pass_final_rate:.3f}",
            f"- auto_remediation_lift: {metrics.success_metrics.auto_remediation_lift:.3f}",
            f"- salvageable_input_rate: {metrics.success_metrics.salvageable_input_rate:.3f}",
            "",
            "## Human burden metrics",
            f"- clarification_item_count: {metrics.human_burden_metrics.clarification_item_count}",
            f"- supplement_request_precision: {metrics.human_burden_metrics.supplement_request_precision:.3f}",
            f"- low_value_work_return_rate: {metrics.human_burden_metrics.low_value_work_return_rate:.3f}",
            "",
            "## Met metrics",
        ]
    )
    if summary.met_metrics:
        lines.extend([f"- {item}" for item in summary.met_metrics])
    else:
        lines.append("- 无")
    lines.extend(["", "## Unmet metrics"])
    if summary.unmet_metrics:
        lines.extend([f"- {item}" for item in summary.unmet_metrics])
    else:
        lines.append("- 无")
    lines.extend(["", "## Distance to 90%+"])
    if summary.distance_to_90_plus:
        lines.extend([f"- {item}" for item in summary.distance_to_90_plus])
    else:
        lines.append("- 当前已达到或超过关键 90%+ 目标。")
    if summary.artifact_paths:
        lines.extend(["", "## Artifact paths"])
        for key, value in summary.artifact_paths.items():
            lines.append(f"- {key}: {value}")
    return "\n".join(lines).strip() + "\n"


def _write_benchmark_summary(
    *,
    output_dir: Path | None,
    summary: BenchmarkSummary,
) -> dict[str, str]:
    if output_dir is None:
        return {}
    benchmark_dir = output_dir / _BENCHMARK_DIRNAME
    benchmark_dir.mkdir(parents=True, exist_ok=True)
    json_path = benchmark_dir / _BENCHMARK_JSON_FILENAME
    markdown_path = benchmark_dir / _BENCHMARK_MD_FILENAME
    json_path.write_text(
        json.dumps(summary.model_dump(mode="json"), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    markdown_path.write_text(
        _render_benchmark_summary_markdown(summary=summary),
        encoding="utf-8",
    )
    return {
        "benchmark_dir": str(benchmark_dir.resolve()),
        "benchmark_json_path": str(json_path.resolve()),
        "benchmark_markdown_path": str(markdown_path.resolve()),
    }


def _critical_path_labels_for_page(
    assessment: EvidenceAssessment,
    *,
    page_name: str,
) -> list[str]:
    return _dedupe_preserve(
        f"[{record.priority}] {record.path_name}"
        for record in _critical_path_records(assessment)
        if page_name in record.required_pages
    )


def _critical_path_labels_for_state(
    assessment: EvidenceAssessment,
    *,
    state_label: str,
) -> list[str]:
    return _dedupe_preserve(
        f"[{record.priority}] {record.path_name}"
        for record in _critical_path_records(assessment)
        if state_label in record.required_states
    )


def _critical_path_priority_score(labels: list[str]) -> int:
    best_rank = min(
        (_clarification_priority_rank(label) for label in labels),
        default=3,
    )
    if best_rank == 0:
        return 100
    if best_rank == 1:
        return 72
    if best_rank == 2:
        return 40
    return 16


def _targeted_lift_delta(
    labels: list[str],
    *,
    target_type: str,
    suggested_input_form: str,
) -> float:
    base = 0.08
    best_rank = min(
        (_clarification_priority_rank(label) for label in labels),
        default=3,
    )
    if best_rank == 0:
        base = 0.22
    elif best_rank == 1:
        base = 0.16
    elif best_rank == 2:
        base = 0.1
    if target_type == "state":
        base = max(0.04, base - 0.03)
    if suggested_input_form == "clarification":
        base += 0.04
    elif suggested_input_form == "markdown_description":
        base += 0.02
    return round(min(base, 0.35), 3)


def _targeted_metric_lift(
    *,
    metric: str,
    current_value: float,
    expected_value: float,
    rationale: str,
) -> TargetedMetricLift:
    return TargetedMetricLift(
        metric=metric,  # type: ignore[arg-type]
        current_value=round(current_value, 3),
        expected_value=round(expected_value, 3),
        delta=round(expected_value - current_value, 3),
        confidence="medium",
        source_channel="mixed",
        evidence_basis=[rationale],
    )


def _targeted_item_sort_key(item: TargetedAcquisitionItem) -> tuple[int, int, str, str]:
    action_rank = {
        "must_acquire_now": 0,
        "clarify_existing_evidence": 1,
        "nice_to_have_later": 2,
    }.get(item.action_class, 3)
    return (-item.priority, action_rank, item.target_page, item.target_state or "")


def _dedupe_targeted_items(
    items: list[TargetedAcquisitionItem],
) -> list[TargetedAcquisitionItem]:
    seen: set[tuple[str, str, str, str, str]] = set()
    deduped: list[TargetedAcquisitionItem] = []
    for item in sorted(items, key=_targeted_item_sort_key):
        key = (
            item.action_class,
            item.target_page,
            item.target_state or "",
            item.suggested_input_form,
            item.screenshot_ref or "",
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _minimal_closure_set(
    items: list[TargetedAcquisitionItem],
    *,
    failing_final_paths: list[str],
    limit: int,
) -> list[TargetedAcquisitionItem]:
    if not items:
        return []
    remaining = set(failing_final_paths)
    selected: list[TargetedAcquisitionItem] = []
    for item in sorted(items, key=_targeted_item_sort_key):
        selected.append(item)
        remaining -= set(item.affected_critical_paths)
        if (not remaining and selected) or len(selected) >= limit:
            break
    return selected


def _aggregate_targeted_metric_lifts(
    items: list[TargetedAcquisitionItem],
) -> list[TargetedMetricLift]:
    if not items:
        return []
    order = [
        "critical_path_page_hit_rate",
        "critical_path_state_hit_rate",
        "trusted_mapping_rate",
        "clarification_burden",
        "expected_final_unlock_rate",
    ]
    aggregated: dict[str, dict[str, float]] = {}
    for item in items:
        for lift in item.expected_metric_lift:
            entry = aggregated.setdefault(
                lift.metric,
                {
                    "current_value": lift.current_value,
                    "expected_value": lift.current_value,
                },
            )
            if lift.metric == "clarification_burden":
                entry["expected_value"] = max(0.0, entry["expected_value"] + lift.delta)
            else:
                entry["expected_value"] = min(1.0, entry["expected_value"] + lift.delta)
    return [
        _targeted_metric_lift(
            metric=metric,
            current_value=aggregated[metric]["current_value"],
            expected_value=aggregated[metric]["expected_value"],
            rationale="aggregated from highest-value targeted acquisition set",
        )
        for metric in order
        if metric in aggregated
    ]


def _suggested_action_text(item: TargetedAcquisitionItem) -> str:
    if item.suggested_input_form == "clarification":
        if item.screenshot_ref:
            return f"先确认 `{item.screenshot_ref}` 的页面/状态；这一步对 final gate 的回报最高"
        return item.why_this_first
    if item.suggested_input_form == "markdown_description":
        target = f"{item.target_page}:{item.target_state}" if item.target_state else item.target_page
        if item.screenshot_ref:
            return f"先为 `{item.screenshot_ref}` 补 markdown 说明，优先补强 `{target}`"
        return f"先为 `{target}` 补 markdown 说明，优先补现有截图的页面/状态证据"
    target = f"{item.target_page}:{item.target_state}" if item.target_state else item.target_page
    return f"先补 `{target}` 的截图，这一步对 critical path 和 final gate 的回报最高"


def _single_action_can_unlock_final(
    assessment: EvidenceAssessment,
    *,
    affected_critical_paths: list[str],
) -> bool:
    if assessment.delivery_status == "final_delivery_ready":
        return False
    breakdown = assessment.delivery_readiness_breakdown
    failing_gates = set(breakdown.get("failing_final_gates", [])) if isinstance(breakdown, dict) else set()
    if failing_gates - {"critical_path_coverage", "clarification_residue", "trusted_evidence_sufficiency"}:
        return False
    summary = assessment.critical_path_coverage_summary
    failing_paths = set(summary.failing_final_paths) if isinstance(summary, CriticalPathCoverageSummary) else set()
    if not failing_paths or not affected_critical_paths:
        return False
    if len(failing_paths) > 1:
        return False
    if not (set(affected_critical_paths) & failing_paths):
        return False
    causes = set()
    if isinstance(assessment.first_pass_success_breakdown, dict):
        causes = set(
            str(cause)
            for cause in assessment.first_pass_success_breakdown.get("supplement_cause_classification", [])
        )
    return not bool(causes & {"missing_evidence", "weak_readability"})


def _page_refs_by_name(image_refs: list[ScreenshotRef]) -> dict[str, list[ScreenshotRef]]:
    refs_by_page: dict[str, list[ScreenshotRef]] = {}
    for ref in image_refs:
        if ref.kind != "image" or ref.draft_mapping is None or ref.draft_mapping.page_name is None:
            continue
        refs_by_page.setdefault(ref.draft_mapping.page_name, []).append(ref)
    return refs_by_page


def _best_existing_ref(
    refs: list[ScreenshotRef],
    *,
    prefer_low_readability: bool = False,
) -> ScreenshotRef | None:
    if not refs:
        return None
    return sorted(
        refs,
        key=lambda ref: (
            0 if prefer_low_readability and ref.readability.level in {"low", "unreadable"} else 1,
            0 if ref.draft_mapping is not None and ref.draft_mapping.final_delivery_eligible else 1,
            ref.relative_path,
        ),
    )[0]


def _final_missing_state_map(
    coverage_summary: dict[str, int | float | bool | str | list[str] | None],
) -> dict[str, list[StateCategory]]:
    mapping: dict[str, list[StateCategory]] = {}
    for label in _coerce_string_list(coverage_summary.get("final_delivery_missing_planned_states")):
        page_name, _, state_name = label.rpartition(":")
        if not page_name or not state_name:
            continue
        normalized = _normalize_state_label(state_name)
        if normalized is None:
            continue
        mapping.setdefault(page_name, []).append(normalized)
    return mapping


def _build_targeted_acquisition_plan(
    *,
    image_refs: list[ScreenshotRef],
    required_evidence_plan: RequiredEvidencePlan | None,
    evidence_assessment: EvidenceAssessment,
    first_pass_success_breakdown: dict[str, Any],
    ocr_available: bool,
) -> TargetedAcquisitionPlan | None:
    if required_evidence_plan is None:
        return None

    coverage_summary = evidence_assessment.coverage_summary
    mission = required_evidence_plan.capture_mission
    if evidence_assessment.delivery_status == "final_delivery_ready":
        return TargetedAcquisitionPlan(
            contract_version=_TARGETED_ACQUISITION_VERSION,
            delivery_status=evidence_assessment.delivery_status,
            first_pass_final=bool(first_pass_success_breakdown.get("first_pass_final", False)),
            supplement_cause_classification=[],
            must_acquire_now=[],
            clarify_existing_evidence=[],
            nice_to_have_later=[],
            highest_value_next_captures=[],
            expected_metric_lift=[],
            confidence="high",
            source_channel="mixed",
            evidence_basis=[
                "delivery_status=final_delivery_ready",
                f"capture_mission_version={mission.mission_version}",
            ],
            verification_gaps=[],
        )
    page_hit_rate, state_hit_rate = _critical_path_hit_rates(evidence_assessment)
    trusted_snapshot = _trusted_mapping_rate_snapshot(evidence_assessment)
    trusted_rate = float(trusted_snapshot["trusted_mapping_rate"])
    planned_page_count = max(1, _coerce_int(coverage_summary.get("planned_page_count", 0)))
    clarification_count = len(evidence_assessment.clarification_items)
    missing_pages = _coerce_string_list(coverage_summary.get("final_delivery_missing_critical_pages"))
    provisional_missing_pages = set(_coerce_string_list(coverage_summary.get("missing_critical_pages")))
    missing_descriptions = set(
        _coerce_string_list(coverage_summary.get("final_delivery_missing_required_description_pages"))
    )
    failing_final_paths = (
        list(evidence_assessment.critical_path_coverage_summary.failing_final_paths)
        if isinstance(evidence_assessment.critical_path_coverage_summary, CriticalPathCoverageSummary)
        else []
    )
    supplement_causes = [
        str(cause)
        for cause in first_pass_success_breakdown.get("supplement_cause_classification", [])
    ]
    refs_by_page = _page_refs_by_name(image_refs)
    final_missing_state_map = _final_missing_state_map(coverage_summary)
    used_targets: set[tuple[str, str | None]] = set()
    clarification_pages = {
        page
        for item in evidence_assessment.clarification_items
        for page in item.candidate_pages
    }

    clarify_candidates: list[TargetedAcquisitionItem] = []
    must_candidates: list[TargetedAcquisitionItem] = []
    nice_candidates: list[TargetedAcquisitionItem] = []

    for item in evidence_assessment.clarification_items:
        labels = item.affected_critical_paths or _critical_path_labels_for_page(
            evidence_assessment,
            page_name=item.candidate_pages[0] if item.candidate_pages else item.relative_path,
        )
        unlocks_final = item.unlocks_final_delivery or _single_action_can_unlock_final(
            evidence_assessment,
            affected_critical_paths=labels,
        )
        priority = _critical_path_priority_score(labels) + 28
        if unlocks_final:
            priority += 18
        target_page = (
            item.candidate_pages[0]
            if len(item.candidate_pages) == 1
            else " / ".join(item.candidate_pages[:2])
            if item.candidate_pages
            else item.relative_path
        )
        target_state = item.candidate_states[0] if item.candidate_states else None
        lifts = [
            _targeted_metric_lift(
                metric="clarification_burden",
                current_value=float(clarification_count),
                expected_value=max(0.0, float(clarification_count - 1)),
                rationale="this confirmation removes one bounded clarification residue",
            ),
            _targeted_metric_lift(
                metric="trusted_mapping_rate",
                current_value=trusted_rate,
                expected_value=min(1.0, trusted_rate + (1 / planned_page_count)),
                rationale="successful clarification can upgrade one provisional mapping into trusted coverage",
            ),
            _targeted_metric_lift(
                metric="critical_path_page_hit_rate",
                current_value=page_hit_rate,
                expected_value=min(
                    1.0,
                    page_hit_rate + _targeted_lift_delta(labels, target_type="page", suggested_input_form="clarification"),
                ),
                rationale="this screenshot already exists and affects a critical path that still fails final gating",
            ),
        ]
        if unlocks_final:
                lifts.append(
                    _targeted_metric_lift(
                        metric="expected_final_unlock_rate",
                        current_value=0.0,
                        expected_value=1.0,
                        rationale="this clarification is the smallest remaining action on the failing final path",
                    )
                )
        clarify_candidates.append(
            TargetedAcquisitionItem(
                action_class="clarify_existing_evidence",
                target_page=target_page,
                target_state=target_state,
                priority=priority,
                affected_critical_paths=labels,
                expected_unlocks_final_delivery=unlocks_final,
                expected_metric_lift=lifts,
                why_this_first=(
                    "现有截图已经具备高价值证据，只差一次轻量确认就能减少 clarification burden，并推动 trusted mapping 或 final gate。"
                ),
                suggested_input_form="clarification",
                screenshot_ref=item.relative_path,
                candidate_pages=item.candidate_pages,
                candidate_states=item.candidate_states,
                confidence=item.confidence,
                source_channel=item.source_channel,
                evidence_basis=item.evidence_basis,
                verification_gaps=item.verification_gaps,
            )
        )
        used_targets.add((target_page, target_state))

    for page_name in missing_pages:
        state_candidates = final_missing_state_map.get(page_name, [])
        target_state = state_candidates[0] if state_candidates else None
        labels = _critical_path_labels_for_page(evidence_assessment, page_name=page_name)
        page_refs = refs_by_page.get(page_name, [])
        low_readability_ref = _best_existing_ref(page_refs, prefer_low_readability=True)
        has_low_readability = bool(
            low_readability_ref is not None
            and low_readability_ref.readability.level in {"low", "unreadable"}
        )
        target_key = (page_name, target_state)
        if target_key in used_targets:
            continue

        existing_evidence_can_be_salvaged = bool(page_refs) and page_name not in provisional_missing_pages
        if page_name in clarification_pages:
            existing_evidence_can_be_salvaged = False

        if existing_evidence_can_be_salvaged:
            form = "markdown_description"
            action_class = "clarify_existing_evidence"
            priority = _critical_path_priority_score(labels) + 20
            if page_name in missing_descriptions or not ocr_available:
                priority += 10
            if has_low_readability:
                form = "screenshot"
                action_class = "must_acquire_now"
                priority += 14
            best_ref = _best_existing_ref(page_refs, prefer_low_readability=has_low_readability)
            lifts = [
                _targeted_metric_lift(
                    metric="trusted_mapping_rate",
                    current_value=trusted_rate,
                    expected_value=min(1.0, trusted_rate + (1 / planned_page_count)),
                    rationale="this page is already provisionally matched; strengthening existing evidence is cheaper than asking for a new mapping set",
                ),
                _targeted_metric_lift(
                    metric="critical_path_page_hit_rate",
                    current_value=page_hit_rate,
                    expected_value=min(
                        1.0,
                        page_hit_rate + _targeted_lift_delta(labels, target_type="page", suggested_input_form=form),
                    ),
                    rationale="the page already exists in the bundle and only needs stronger proof to count toward final coverage",
                ),
            ]
            unlocks_final = _single_action_can_unlock_final(
                evidence_assessment,
                affected_critical_paths=labels,
            )
            if unlocks_final:
                lifts.append(
                    _targeted_metric_lift(
                        metric="expected_final_unlock_rate",
                        current_value=0.0,
                        expected_value=1.0,
                        rationale="promoting this existing page to trusted coverage is likely enough to close the remaining final blocker",
                    )
                )
            target_item = TargetedAcquisitionItem(
                action_class=action_class,  # type: ignore[arg-type]
                target_page=page_name,
                target_state=target_state,
                priority=priority,
                affected_critical_paths=labels,
                expected_unlocks_final_delivery=unlocks_final,
                expected_metric_lift=lifts,
                why_this_first=(
                    "这页其实已经有截图；先把现有证据补强成 trusted，比重新补整套截图的单位回报更高。"
                ),
                suggested_input_form=form,  # type: ignore[arg-type]
                screenshot_ref=best_ref.relative_path if best_ref is not None else None,
                candidate_pages=[page_name],
                candidate_states=[target_state] if target_state is not None else [],
                confidence="medium",
                source_channel="mixed",
                evidence_basis=[
                    f"page={page_name}",
                    "existing screenshot is provisionally matched but not yet trusted for final delivery",
                ],
            )
            if action_class == "must_acquire_now":
                must_candidates.append(target_item)
            else:
                clarify_candidates.append(target_item)
        else:
            lifts = [
                _targeted_metric_lift(
                    metric="critical_path_page_hit_rate",
                    current_value=page_hit_rate,
                    expected_value=min(
                        1.0,
                        page_hit_rate + _targeted_lift_delta(labels, target_type="page", suggested_input_form="screenshot"),
                    ),
                    rationale="this page is still absent from the final-delivery evidence set",
                ),
                _targeted_metric_lift(
                    metric="trusted_mapping_rate",
                    current_value=trusted_rate,
                    expected_value=min(1.0, trusted_rate + (1 / planned_page_count)),
                    rationale="adding this page creates one more trusted mapping on the critical path",
                ),
            ]
            unlocks_final = _single_action_can_unlock_final(
                evidence_assessment,
                affected_critical_paths=labels,
            )
            if unlocks_final:
                lifts.append(
                    _targeted_metric_lift(
                        metric="expected_final_unlock_rate",
                        current_value=0.0,
                        expected_value=1.0,
                        rationale="this missing page is the last visible blocker on the failing critical path",
                    )
                )
            must_candidates.append(
                TargetedAcquisitionItem(
                    action_class="must_acquire_now",
                    target_page=page_name,
                    target_state=target_state,
                    priority=_critical_path_priority_score(labels) + 32,
                    affected_critical_paths=labels,
                    expected_unlocks_final_delivery=unlocks_final,
                    expected_metric_lift=lifts,
                    why_this_first="这页当前是真缺料，直接补这一页的截图比继续补次要页面更能抬升 final 概率。",
                    suggested_input_form="screenshot",
                    screenshot_ref=None,
                    candidate_pages=[page_name],
                    candidate_states=[target_state] if target_state is not None else [],
                    confidence="high",
                    source_channel="mixed",
                    evidence_basis=[
                        f"page={page_name}",
                        "page is still missing from the final-delivery-qualified coverage set",
                    ],
                )
            )
        used_targets.add(target_key)

    for page_name, states in final_missing_state_map.items():
        if page_name in missing_pages:
            continue
        page_refs = refs_by_page.get(page_name, [])
        existing_ref = _best_existing_ref(page_refs)
        labels = _critical_path_labels_for_page(evidence_assessment, page_name=page_name)
        for state_name in states:
            target_key = (page_name, state_name)
            if target_key in used_targets:
                continue
            has_existing_ref = bool(page_refs)
            input_form = "screenshot"
            action_class = "must_acquire_now"
            if has_existing_ref and (page_name in missing_descriptions or not ocr_available):
                input_form = "markdown_description"
                action_class = "clarify_existing_evidence"
            lifts = [
                _targeted_metric_lift(
                    metric="critical_path_state_hit_rate",
                    current_value=state_hit_rate,
                    expected_value=min(
                        1.0,
                        state_hit_rate + _targeted_lift_delta(labels, target_type="state", suggested_input_form=input_form),
                    ),
                    rationale="this state still blocks the critical path even though the page is mostly covered",
                ),
            ]
            unlocks_final = _single_action_can_unlock_final(
                evidence_assessment,
                affected_critical_paths=_critical_path_labels_for_state(
                    evidence_assessment,
                    state_label=f"{page_name}:{state_name}",
                )
                or labels,
            )
            if unlocks_final:
                lifts.append(
                    _targeted_metric_lift(
                        metric="expected_final_unlock_rate",
                        current_value=0.0,
                        expected_value=1.0,
                        rationale="this missing state is the remaining gap on the failing critical path",
                    )
                )
            target_item = TargetedAcquisitionItem(
                action_class=action_class,  # type: ignore[arg-type]
                target_page=page_name,
                target_state=state_name,
                priority=_critical_path_priority_score(labels) + (18 if action_class == "must_acquire_now" else 12),
                affected_critical_paths=labels,
                expected_unlocks_final_delivery=unlocks_final,
                expected_metric_lift=lifts,
                why_this_first="页面本身已经在，但关键状态还没闭合；先补这个状态的回报高于继续补泛化截图。",
                suggested_input_form=input_form,  # type: ignore[arg-type]
                screenshot_ref=existing_ref.relative_path if existing_ref is not None else None,
                candidate_pages=[page_name],
                candidate_states=[state_name],  # type: ignore[list-item]
                confidence="medium",
                source_channel="mixed",
                evidence_basis=[
                    f"state={page_name}:{state_name}",
                    "page exists but critical state coverage is still insufficient",
                ],
            )
            if action_class == "must_acquire_now":
                must_candidates.append(target_item)
            else:
                clarify_candidates.append(target_item)
            used_targets.add(target_key)

    valid_page_names = {
        requirement.page_name
        for requirement in required_evidence_plan.critical_pages
    }
    if mission.nice_to_have_pages:
        for page_name in mission.nice_to_have_pages:
            if page_name not in valid_page_names:
                continue
            if page_name in missing_pages or page_name in refs_by_page:
                continue
            labels = _critical_path_labels_for_page(evidence_assessment, page_name=page_name)
            nice_candidates.append(
                TargetedAcquisitionItem(
                    action_class="nice_to_have_later",
                    target_page=page_name,
                    target_state=None,
                    priority=_critical_path_priority_score(labels) + 4,
                    affected_critical_paths=labels,
                    expected_unlocks_final_delivery=False,
                    expected_metric_lift=[
                        _targeted_metric_lift(
                            metric="critical_path_page_hit_rate",
                            current_value=page_hit_rate,
                            expected_value=min(1.0, page_hit_rate + 0.04),
                            rationale="this page mainly improves confidence breadth after the blocking paths are solved",
                        )
                    ],
                    why_this_first="这页不会先于主链路 blocker 解决，但补上后能减少后续回合。",
                    suggested_input_form="screenshot",
                    screenshot_ref=None,
                    candidate_pages=[page_name],
                    candidate_states=[],
                    confidence="low",
                    source_channel="metadata",
                    evidence_basis=[f"page={page_name}", "nice-to-have page from capture mission"],
                )
            )

    must_acquire_now = _minimal_closure_set(
        _dedupe_targeted_items(must_candidates),
        failing_final_paths=failing_final_paths,
        limit=3,
    )
    clarify_existing_evidence = _minimal_closure_set(
        _dedupe_targeted_items(clarify_candidates),
        failing_final_paths=failing_final_paths,
        limit=3,
    )
    nice_to_have_later = _dedupe_targeted_items(nice_candidates)[:3]
    highest_value_next_captures = sorted(
        [*must_acquire_now, *clarify_existing_evidence],
        key=_targeted_item_sort_key,
    )[:3]
    aggregated_metric_lift = _aggregate_targeted_metric_lifts(highest_value_next_captures)

    if (
        not must_acquire_now
        and not clarify_existing_evidence
        and mission.capture_order
    ):
        fallback_page = mission.capture_order[0]
        labels = _critical_path_labels_for_page(evidence_assessment, page_name=fallback_page)
        must_acquire_now = [
            TargetedAcquisitionItem(
                action_class="must_acquire_now",
                target_page=fallback_page,
                target_state=None,
                priority=_critical_path_priority_score(labels) + 12,
                affected_critical_paths=labels,
                expected_unlocks_final_delivery=False,
                expected_metric_lift=[
                    _targeted_metric_lift(
                        metric="critical_path_page_hit_rate",
                        current_value=page_hit_rate,
                        expected_value=min(1.0, page_hit_rate + 0.08),
                        rationale="fallback to the first capture-mission page when the current bundle is still too sparse",
                    )
                ],
                why_this_first="当前输入过 sparse，先补 Capture Mission 第一页能最快建立主链路骨架。",
                suggested_input_form="screenshot",
                screenshot_ref=None,
                candidate_pages=[fallback_page],
                candidate_states=[],
                confidence="medium",
                source_channel="metadata",
                evidence_basis=[f"capture_order_first={fallback_page}"],
            )
        ]
        highest_value_next_captures = must_acquire_now
        aggregated_metric_lift = _aggregate_targeted_metric_lifts(highest_value_next_captures)

    return TargetedAcquisitionPlan(
        contract_version=_TARGETED_ACQUISITION_VERSION,
        delivery_status=evidence_assessment.delivery_status,
        first_pass_final=bool(first_pass_success_breakdown.get("first_pass_final", False)),
        supplement_cause_classification=supplement_causes,
        must_acquire_now=must_acquire_now,
        clarify_existing_evidence=clarify_existing_evidence,
        nice_to_have_later=nice_to_have_later,
        highest_value_next_captures=highest_value_next_captures,
        expected_metric_lift=aggregated_metric_lift,
        confidence=(
            "high"
            if highest_value_next_captures
            else "medium"
        ),
        source_channel="mixed",
        evidence_basis=[
            f"targeted_item_count={len(must_acquire_now) + len(clarify_existing_evidence) + len(nice_to_have_later)}",
            f"highest_value_next_capture_count={len(highest_value_next_captures)}",
            f"delivery_status={evidence_assessment.delivery_status}",
            f"capture_mission_version={mission.mission_version}",
            *[f"supplement_cause={cause}" for cause in supplement_causes],
        ],
        verification_gaps=[
            *(
                []
                if highest_value_next_captures
                else ["no high-leverage targeted action was detected beyond the current capture mission order"]
            ),
        ],
    )


def _evidence_fingerprint(files: list[Path], *, root: Path) -> str:
    payload = [
        {
            "relative_path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "mtime_ns": path.stat().st_mtime_ns,
        }
        for path in files
    ]
    digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    return digest.hexdigest()


def _gap_signature(assessment: EvidenceAssessment) -> str:
    payload = {
        "delivery_status": assessment.delivery_status,
        "blocking_reasons": assessment.blocking_reasons,
        "required_actions": assessment.required_actions,
        "missing_coverage": assessment.missing_coverage,
        "verification_gaps": assessment.verification_gaps,
        "clarification_relative_paths": [item.relative_path for item in assessment.clarification_items],
    }
    digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    return digest.hexdigest()


def _read_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _write_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _persist_clarification_state(
    *,
    output_dir: Path | None,
    evidence_fingerprint: str,
    clarification_items: list[ClarificationItem],
) -> tuple[str | None, bool]:
    if output_dir is None or not clarification_items:
        return None, False

    clarification_dir = output_dir / _CLARIFICATION_DIRNAME
    state_path = clarification_dir / _CLARIFICATION_STATE_FILENAME
    signature = _clarification_signature(clarification_items)
    previous = _read_json_file(state_path)
    previous_fingerprint = str(previous.get("evidence_fingerprint", ""))
    previous_surface_count = int(previous.get("surface_count", 0) or 0)
    already_surfaced = previous_fingerprint == evidence_fingerprint and previous_surface_count >= 1
    payload = {
        "evidence_fingerprint": evidence_fingerprint,
        "clarification_signature": signature,
        "surface_count": previous_surface_count if already_surfaced else previous_surface_count + 1,
        "clarification_relative_paths": [item.relative_path for item in clarification_items],
    }
    _write_json_file(state_path, payload)
    return str(state_path), already_surfaced


def _write_clarification_package(
    *,
    output_dir: Path | None,
    package_root: str,
    refs: list[ScreenshotRef],
    clarification_items: list[ClarificationItem],
) -> str | None:
    if output_dir is None or not clarification_items:
        return None

    package_dir = output_dir / package_root
    package_dir.mkdir(parents=True, exist_ok=True)
    draft_map_path = package_dir / "draft-screens-map.md"
    clarification_path = package_dir / "clarification-needed.md"
    json_path = package_dir / "clarification-items.json"

    draft_lines = [
        "# Clarification Mapping Draft",
        "",
        "只补下面这些歧义截图。不要重做整套 mapping，也不要批量改文件名。",
        "",
    ]
    clarification_by_path = {item.relative_path: item for item in clarification_items}
    for ref in refs:
        if ref.kind != "image" or ref.draft_mapping is None or ref.relative_path not in clarification_by_path:
            continue
        item = clarification_by_path[ref.relative_path]
        states = ", ".join(item.candidate_states) if item.candidate_states else "default"
        candidate_pages = " / ".join(item.candidate_pages) if item.candidate_pages else "unknown"
        draft_lines.append(
            f"- `{ref.relative_path}` -> page={candidate_pages}; states={states}"
        )

    clarification_lines = [
        "# Bounded Clarification Package",
        "",
        "只确认下面这些少量高回报歧义截图。其余截图映射已经自动起草，不需要你逐张整理。",
        "",
    ]
    for item in clarification_items:
        candidate_pages = " / ".join(item.candidate_pages) if item.candidate_pages else "unknown"
        candidate_states = ", ".join(item.candidate_states) if item.candidate_states else "default"
        affected_paths = " / ".join(item.affected_critical_paths) if item.affected_critical_paths else "无"
        clarification_lines.extend(
            [
                f"## {item.relative_path}",
                f"- screenshot_ref: {item.screenshot_ref}",
                f"- candidate_pages: {candidate_pages}",
                f"- candidate_states: {candidate_states}",
                f"- ambiguity_reason: {item.ambiguity_reason}",
                f"- affected_critical_paths: {affected_paths}",
                f"- unlocks_final_delivery: {'yes' if item.unlocks_final_delivery else 'no'}",
                f"- confirmation_prompt: {item.confirmation_prompt}",
                "- evidence_basis:",
            ]
        )
        clarification_lines.extend(f"  - {basis}" for basis in item.evidence_basis[:6])
        clarification_lines.append("")

    draft_map_path.write_text("\n".join(draft_lines).strip() + "\n", encoding="utf-8")
    clarification_path.write_text("\n".join(clarification_lines).strip() + "\n", encoding="utf-8")
    _write_json_file(
        json_path,
        {
            "clarification_items": [item.model_dump(mode="json") for item in clarification_items],
            "drafted_image_count": len([ref for ref in refs if ref.kind == "image" and ref.draft_mapping is not None]),
        },
    )
    return str(package_dir)


def _description_texts_for_refs(refs: list[ScreenshotRef]) -> dict[str, str]:
    texts: dict[str, str] = {}
    for ref in refs:
        if ref.kind != "description":
            continue
        texts[ref.id] = _read_text(Path(ref.path))
    return texts


def _auto_remediate_refs(
    refs: list[ScreenshotRef],
    *,
    output_dir: Path | None,
    task_checklist_lite: str | None,
    required_evidence_plan: RequiredEvidencePlan | None,
) -> tuple[list[ScreenshotRef], dict[str, Any]]:
    image_refs = [ref for ref in refs if ref.kind == "image"]
    if not image_refs:
        return refs, {
            "auto_remediation_attempted": False,
            "auto_remediation_changed": False,
            "auto_remediation_note_count": 0,
            "auto_remediation_note_paths": [],
        }

    description_texts = _description_texts_for_refs(refs)
    sections: list[dict[str, str]] = []
    for ref in refs:
        if ref.kind != "description":
            continue
        text = description_texts.get(ref.id, "")
        sections.extend(_markdown_sections(text, ref.relative_path))

    note_dir = output_dir / _REMEDIATION_DIRNAME / _REMEDIATION_NOTES_DIRNAME if output_dir else None
    updated_refs: list[ScreenshotRef] = list(refs)
    note_paths: list[str] = []
    note_count = 0
    changed = False
    priority_page_names = _remediation_priority_page_names(
        required_evidence_plan,
        refs=refs,
    )
    priority_ref_count = 0
    low_readability_target_count = 0
    markdown_section_uplift_count = 0

    for idx, ref in enumerate(updated_refs):
        if ref.kind != "image":
            continue

        matched_pages = _matched_pages_for_remediation(
            ref,
            required_evidence_plan=required_evidence_plan,
            priority_page_names=priority_page_names,
        )
        matched_sections = _select_description_sections(
            ref,
            sections,
            matched_pages=matched_pages,
        )
        matched_tasks = _match_tasks_for_ref(ref, task_checklist_lite)
        if matched_pages and any(page.page_name in priority_page_names for page in matched_pages):
            priority_ref_count += 1
        if ref.readability.level in {"low", "unreadable"} and (matched_sections or ref.ocr_text_lines):
            low_readability_target_count += 1
        note_text = _render_auto_note(
            ref,
            matched_sections=matched_sections,
            matched_tasks=matched_tasks,
            matched_pages=matched_pages,
        )
        if note_text is None:
            continue

        note_relpath = f"{_REMEDIATION_DIRNAME}/{_REMEDIATION_NOTES_DIRNAME}/{ref.id.lower()}-auto.md"
        note_count += 1
        if note_dir is not None:
            note_path = note_dir / f"{ref.id.lower()}-auto.md"
            note_path.parent.mkdir(parents=True, exist_ok=True)
            note_path.write_text(note_text, encoding="utf-8")
            note_paths.append(str(note_path))

        section_titles: list[TextCue] = []
        section_buttons: list[TextCue] = []
        section_navs: list[TextCue] = []
        section_states: list[TextCue] = []
        for section in matched_sections:
            title_cues, button_cues, nav_cues, state_cues = _markdown_cues(
                f"{section['title']}\n{section['body']}",
                f"{section['source_path']}#{section['title']}",
            )
            section_titles.extend(title_cues)
            section_buttons.extend(button_cues)
            section_navs.extend(nav_cues)
            section_states.extend(state_cues)
        if matched_sections:
            markdown_section_uplift_count += 1

        note_titles, note_buttons, note_navs, note_states = _markdown_cues(note_text, note_relpath)
        note_link = DescriptionLink(
            description_id=f"AUTO-{ref.id}",
            description_path=note_relpath,
            confidence="high" if matched_sections and ref.ocr_text_lines else "medium",
            source_channel="mixed",
            evidence_basis=(
                [f"auto-remediation note built from {len(matched_sections)} matched markdown sections"]
                if matched_sections
                else []
            )
            + (
                [f"auto-remediation note built from {len(ref.ocr_text_lines)} OCR text cues"]
                if ref.ocr_text_lines
                else []
            ),
            verification_gaps=[
                "auto-remediation note is derived evidence; do not treat it as an independent semantic source"
            ],
        )
        note_basis = f"auto-remediation note from '{note_relpath}' is mixed-source derived evidence"
        note_titles = _retag_cues(note_titles, source_channel="mixed", evidence_note=note_basis)
        note_buttons = _retag_cues(note_buttons, source_channel="mixed", evidence_note=note_basis)
        note_navs = _retag_cues(note_navs, source_channel="mixed", evidence_note=note_basis)
        note_states = _retag_cues(note_states, source_channel="mixed", evidence_note=note_basis)
        existing_links = list(ref.description_links)
        if not any(link.description_path == note_link.description_path for link in existing_links):
            existing_links.append(note_link)
        existing_titles = list(ref.page_title_candidates)
        existing_buttons = list(ref.button_text_candidates)
        existing_navs = list(ref.navigation_text_candidates)
        existing_states = list(ref.state_text_candidates)

        verification_gaps = [
            gap
            for gap in ref.verification_gaps
            if gap != "no linked markdown description for this screenshot"
        ]

        updated_refs[idx] = ref.model_copy(
            update={
                "description_links": existing_links,
                "page_title_candidates": _merge_unique(existing_titles + section_titles + note_titles),
                "button_text_candidates": _merge_unique(existing_buttons + section_buttons + note_buttons),
                "navigation_text_candidates": _merge_unique(existing_navs + section_navs + note_navs),
                "state_text_candidates": _merge_unique(existing_states + section_states + note_states),
                "confidence": _max_confidence(ref.confidence, "medium"),
                "source_channel": "mixed",
                "evidence_basis": ref.evidence_basis + [f"auto-remediation note={note_relpath}"],
                "verification_gaps": verification_gaps,
            }
        )
        changed = True

    return updated_refs, {
        "auto_remediation_attempted": True,
        "auto_remediation_changed": changed,
        "auto_remediation_note_count": note_count,
        "auto_remediation_note_paths": note_paths,
        "auto_remediation_priority_ref_count": priority_ref_count,
        "auto_remediation_low_readability_target_count": low_readability_target_count,
        "auto_remediation_markdown_section_uplift_count": markdown_section_uplift_count,
    }


def _persist_remediation_state(
    *,
    output_dir: Path | None,
    evidence_fingerprint: str,
    evidence_assessment: EvidenceAssessment,
) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    if output_dir is None:
        return summary

    remediation_dir = output_dir / _REMEDIATION_DIRNAME
    state_path = remediation_dir / _REMEDIATION_STATE_FILENAME
    gap_signature = _gap_signature(evidence_assessment)
    previous = _read_json_file(state_path)
    previous_fingerprint = previous.get("evidence_fingerprint")
    previous_signature = previous.get("gap_signature")
    previous_pause_count = int(previous.get("pause_surface_count", 0) or 0)

    unresolved = evidence_assessment.delivery_status != "final_delivery_ready"
    repeated_gap = (
        unresolved
        and previous_fingerprint == evidence_fingerprint
        and previous_signature == gap_signature
        and previous_pause_count >= 1
    )

    payload = {
        "evidence_fingerprint": evidence_fingerprint,
        "gap_signature": gap_signature,
        "delivery_status": evidence_assessment.delivery_status,
        "pause_surface_count": 0 if not unresolved else previous_pause_count + 1,
        "required_actions": evidence_assessment.required_actions,
        "missing_coverage": evidence_assessment.missing_coverage,
    }
    _write_json_file(state_path, payload)
    summary.update(
        {
            "pause_already_surfaced": repeated_gap,
            "evidence_fingerprint": evidence_fingerprint,
            "gap_signature": gap_signature,
            "remediation_state_path": str(state_path),
        }
    )
    if repeated_gap:
        actions = "；".join(evidence_assessment.required_actions[:4]) or "补齐缺失证据后再 resume"
        raise RemediationLoopError(
            "Evidence remediation did not change the unresolved client-evidence gap since the last pause. "
            f"Please update the evidence bundle before resuming again: {actions}"
        )
    return summary


def _planning_gap_signature(guidance: EvidenceInputGuidance) -> str:
    payload = {
        "pre_run_status": guidance.pre_run_status,
        "required_actions": guidance.required_actions,
        "missing_pages": guidance.missing_pages,
        "missing_states": guidance.missing_states,
        "missing_descriptions": guidance.missing_descriptions,
        "naming_issues": guidance.naming_issues,
        "hard_requirements_missing": guidance.hard_requirements_missing,
        "clarification_relative_paths": [item.relative_path for item in guidance.clarification_items],
    }
    digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    return digest.hexdigest()


def _persist_planning_state(
    *,
    output_dir: Path | None,
    evidence_fingerprint: str,
    evidence_input_guidance: EvidenceInputGuidance,
) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    if output_dir is None:
        return summary

    planning_dir = output_dir / _PLANNING_DIRNAME
    state_path = planning_dir / _PLANNING_STATE_FILENAME
    gap_signature = _planning_gap_signature(evidence_input_guidance)
    previous = _read_json_file(state_path)
    previous_fingerprint = previous.get("evidence_fingerprint")
    previous_signature = previous.get("gap_signature")
    previous_pause_count = int(previous.get("pause_surface_count", 0) or 0)

    unresolved = evidence_input_guidance.pre_run_status != "ready"
    repeated_gap = (
        unresolved
        and previous_fingerprint == evidence_fingerprint
        and previous_signature == gap_signature
        and previous_pause_count >= 1
    )

    payload = {
        "evidence_fingerprint": evidence_fingerprint,
        "gap_signature": gap_signature,
        "pre_run_status": evidence_input_guidance.pre_run_status,
        "pause_surface_count": 0 if not unresolved else previous_pause_count + 1,
        "required_actions": evidence_input_guidance.required_actions,
        "missing_pages": evidence_input_guidance.missing_pages,
        "missing_states": evidence_input_guidance.missing_states,
        "missing_descriptions": evidence_input_guidance.missing_descriptions,
    }
    _write_json_file(state_path, payload)
    summary.update(
        {
            "pre_run_planning_state_path": str(state_path),
            "pre_run_gap_signature": gap_signature,
        }
    )
    if repeated_gap:
        actions = "；".join(evidence_input_guidance.required_actions[:4]) or "先按补料清单更新关键截图和说明"
        raise PlanningLoopError(
            "Pre-run evidence planning surfaced the same unresolved critical input gap again. "
            f"Please update the screenshot bundle before resuming: {actions}"
        )
    return summary


def _write_capture_mission(
    *,
    output_dir: Path | None,
    mission: CaptureMission,
    guidance: EvidenceInputGuidance,
) -> str | None:
    if output_dir is None:
        return None
    planning_dir = output_dir / _PLANNING_DIRNAME
    planning_dir.mkdir(parents=True, exist_ok=True)
    mission_path = planning_dir / _PLANNING_MISSION_FILENAME
    mission_path.write_text(
        _render_capture_mission_markdown(mission=mission, guidance=guidance),
        encoding="utf-8",
    )
    return str(mission_path.resolve())


def _render_targeted_acquisition_markdown(
    *,
    plan: TargetedAcquisitionPlan,
) -> str:
    lines = [
        "# Targeted Acquisition Plan",
        "",
        "只先补最值钱的那几项。不要批量改名，也不要手写整套 mapping。",
        "",
        f"- delivery_status: {plan.delivery_status}",
        f"- first_pass_final: {'yes' if plan.first_pass_final else 'no'}",
        f"- supplement_cause_classification: {', '.join(plan.supplement_cause_classification) if plan.supplement_cause_classification else 'none'}",
        "",
        "## Highest value next captures",
    ]
    if plan.highest_value_next_captures:
        for index, item in enumerate(plan.highest_value_next_captures, start=1):
            target = f"{item.target_page}:{item.target_state}" if item.target_state else item.target_page
            paths = " / ".join(item.affected_critical_paths) if item.affected_critical_paths else "无"
            lines.extend(
                [
                    f"{index}. {target}",
                    f"   - action_class: {item.action_class}",
                    f"   - suggested_input_form: {item.suggested_input_form}",
                    f"   - affected_critical_paths: {paths}",
                    f"   - expected_unlocks_final_delivery: {'yes' if item.expected_unlocks_final_delivery else 'no'}",
                    f"   - why_this_first: {item.why_this_first}",
                ]
            )
    else:
        lines.append("1. 当前不需要 targeted acquisition；现有输入已达到 final_delivery_ready。")

    for section, items in (
        ("Must acquire now", plan.must_acquire_now),
        ("Clarify existing evidence", plan.clarify_existing_evidence),
        ("Nice to have later", plan.nice_to_have_later),
    ):
        lines.extend(["", f"## {section}"])
        if not items:
            lines.append("- 无")
            continue
        for item in items:
            target = f"{item.target_page}:{item.target_state}" if item.target_state else item.target_page
            lines.append(f"- {target} ({item.suggested_input_form})")
            if item.screenshot_ref:
                lines.append(f"  - screenshot_ref: {item.screenshot_ref}")
            lines.append(f"  - why_this_first: {item.why_this_first}")
            for lift in item.expected_metric_lift:
                lines.append(
                    f"  - expected_metric_lift: {lift.metric} {lift.current_value:.3f} -> {lift.expected_value:.3f}"
                )

    lines.extend(["", "## Expected metric lift"])
    if plan.expected_metric_lift:
        for lift in plan.expected_metric_lift:
            lines.append(
                f"- {lift.metric}: {lift.current_value:.3f} -> {lift.expected_value:.3f} (delta {lift.delta:+.3f})"
            )
    else:
        lines.append("- 当前无需额外 uplift。")

    return "\n".join(lines).strip() + "\n"


def _write_targeted_acquisition_plan(
    *,
    output_dir: Path | None,
    plan: TargetedAcquisitionPlan | None,
) -> str | None:
    if output_dir is None or plan is None:
        return None
    package_dir = output_dir / _TARGETED_ACQUISITION_DIRNAME
    package_dir.mkdir(parents=True, exist_ok=True)
    plan_path = package_dir / _TARGETED_ACQUISITION_FILENAME
    plan_path.write_text(
        _render_targeted_acquisition_markdown(plan=plan),
        encoding="utf-8",
    )
    _write_json_file(
        package_dir / "targeted_acquisition_plan.json",
        plan.model_dump(mode="json"),
    )
    return str(package_dir.resolve())


def plan_required_evidence(
    modules: Any,
    key_features: Any,
    task_checklist_lite: str | None = None,
    journey_map: Any = None,
    journey_stages: Any = None,
    screenshots_dir: Path | str | None = None,
    *,
    output_dir: Path | str | None = None,
    run_id: str | None = None,
    stage_id: str | None = None,
) -> PlanRequiredEvidenceResult:
    """Build a deterministic critical-evidence plan and pre-run intake guidance."""
    required_evidence_plan = _build_required_evidence_plan(
        modules=modules,
        key_features=key_features,
        task_checklist_lite=task_checklist_lite,
        journey_map=journey_map,
        journey_stages=journey_stages,
    )

    output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
    screenshots_path = Path(screenshots_dir) if isinstance(screenshots_dir, str) else screenshots_dir

    files: list[Path] = []
    refs: list[ScreenshotRef] = []
    if screenshots_path is not None and screenshots_path.exists() and screenshots_path.is_dir():
        files = _collect_files(screenshots_path)
        refs = _build_refs(files, root=screenshots_path, ocr_backend=None)
        refs, _clarification_items = _apply_draft_mappings(
            refs,
            plan=required_evidence_plan,
        )
        refs, _remediation_summary = _auto_remediate_refs(
            refs,
            output_dir=None,
            task_checklist_lite=task_checklist_lite,
            required_evidence_plan=required_evidence_plan,
        )
        refs, _clarification_items = _apply_draft_mappings(
            refs,
            plan=required_evidence_plan,
        )

    probe = probe_ocr_backend()
    evidence_input_guidance = _pre_run_input_guidance(
        refs=refs,
        required_evidence_plan=required_evidence_plan,
        ocr_available=probe.available,
    )
    capture_mission = required_evidence_plan.capture_mission
    capture_mission_path = _write_capture_mission(
        output_dir=output_dir,
        mission=capture_mission,
        guidance=evidence_input_guidance,
    )
    if capture_mission_path is not None:
        capture_mission = capture_mission.model_copy(update={"mission_doc_path": capture_mission_path})
        required_evidence_plan = required_evidence_plan.model_copy(
            update={"capture_mission": capture_mission}
        )
        evidence_input_guidance.evidence_basis.append(
            f"capture_mission_path={capture_mission_path}"
        )
        if evidence_input_guidance.pre_run_status != "ready":
            evidence_input_guidance.required_actions = _dedupe_preserve(
                [
                    f"先看 {capture_mission_path}，按 capture order 一次性补最关键证据",
                    *evidence_input_guidance.required_actions,
                ]
            )
    evidence_fingerprint: str | None = None
    if screenshots_path is not None:
        evidence_fingerprint = _evidence_fingerprint(files, root=screenshots_path)
    already_surfaced = False
    clarification_state_path: str | None = None
    if evidence_fingerprint is not None:
        clarification_state_path, already_surfaced = _persist_clarification_state(
            output_dir=output_dir,
            evidence_fingerprint=evidence_fingerprint,
            clarification_items=evidence_input_guidance.clarification_items,
        )
    clarification_package_path = _write_clarification_package(
        output_dir=output_dir,
        package_root=_CLARIFICATION_DIRNAME,
        refs=refs,
        clarification_items=evidence_input_guidance.clarification_items,
    )
    if clarification_package_path is not None:
        evidence_input_guidance.clarification_package_path = clarification_package_path
        if (
            evidence_input_guidance.clarification_items
            and evidence_input_guidance.pre_run_status != "ready"
            and not already_surfaced
        ):
            evidence_input_guidance.required_actions = _dedupe_preserve(
                [
                    f"先查看 {clarification_package_path}，只确认其中列出的歧义截图",
                    *evidence_input_guidance.required_actions,
                ]
            )
        evidence_input_guidance.evidence_basis.append(
            f"clarification_package_path={clarification_package_path}"
        )
    if clarification_state_path is not None:
        evidence_input_guidance.evidence_basis.append(
            f"clarification_state_path={clarification_state_path}"
        )

    if screenshots_path is not None and evidence_fingerprint is not None:
        planning_state = _persist_planning_state(
            output_dir=output_dir,
            evidence_fingerprint=evidence_fingerprint,
            evidence_input_guidance=evidence_input_guidance,
        )
        if planning_state:
            evidence_input_guidance.evidence_basis.extend(
                f"{key}={value}"
                for key, value in planning_state.items()
            )

    return PlanRequiredEvidenceResult(
        capture_mission=capture_mission,
        required_evidence_plan=required_evidence_plan,
        critical_page_requirements=required_evidence_plan.critical_pages,
        critical_state_requirements=required_evidence_plan.critical_states,
        evidence_input_guidance=evidence_input_guidance,
    )


def _pre_run_input_guidance(
    *,
    refs: list[ScreenshotRef],
    required_evidence_plan: RequiredEvidencePlan,
    ocr_available: bool,
) -> EvidenceInputGuidance:
    mission = required_evidence_plan.capture_mission
    image_refs = [ref for ref in refs if ref.kind == "image"]
    description_refs = [ref for ref in refs if ref.kind == "description"]
    plan_coverage = _plan_coverage_summary(
        image_refs,
        plan=required_evidence_plan,
        ocr_available=ocr_available,
    )
    missing_pages = list(plan_coverage["missing_critical_pages"])
    missing_states = list(plan_coverage["missing_planned_states"])
    missing_descriptions = list(plan_coverage["missing_required_description_pages"])
    naming_issues = list(plan_coverage["naming_issues"])
    raw_clarification_items = [
        _clarification_from_ref(ref, plan=required_evidence_plan)
        for ref in image_refs
        if ref.draft_mapping is not None and ref.draft_mapping.clarification_needed
    ]
    clarification_items, clarification_suppressed_reason = _select_clarification_items(
        clarification_items=[item for item in raw_clarification_items if item is not None],
        missing_pages=missing_pages,
        missing_states=missing_states,
        missing_descriptions=missing_descriptions,
    )
    planned_page_count = int(plan_coverage["planned_page_count"] or 0)
    matched_page_count = int(plan_coverage["matched_planned_page_count"] or 0)
    planned_page_ratio = plan_coverage["planned_page_coverage_ratio"]

    status = "ready"
    status_reason = "当前截图输入已满足 Capture Mission 基线，可继续进入正式截图证据分析。"
    required_actions: list[str] = []
    optional_suggestions: list[str] = []
    hard_missing: list[str] = []
    verification_gaps: list[str] = []
    missing_coverage: list[str] = []

    if not image_refs:
        status = "blocked"
        status_reason = "当前还没有任何截图，无法开始 client 模式关键证据分析。"
        hard_missing.append("至少补 5 张关键页面截图")
        required_actions.append("补至少 5 张关键页面截图到 inputs/screens/")
    else:
        min_image_target = min(5, planned_page_count) if planned_page_count else 5
        if len(image_refs) < min_image_target:
            status = "supplement_required"
            missing_coverage.append(
                f"当前仅 {len(image_refs)} 张截图，低于 Capture Mission 的关键页面最小目标 {min_image_target} 张"
            )
            required_actions.append(
                f"优先按 Capture Mission 补足关键页面截图，建议至少 {min_image_target} 张，覆盖主流程核心页面"
            )
            hard_missing.append("关键页面截图数量不足")
        if missing_pages:
            preview = "；".join(missing_pages[:6])
            if status == "ready" and (
                not isinstance(planned_page_ratio, float) or planned_page_ratio < 0.8 or not ocr_available
            ):
                status = "supplement_required"
            missing_coverage.append(f"Capture Mission 未覆盖关键页面：{preview}")
            required_actions.append(f"优先补这些 must_capture_pages：{preview}")
            hard_missing.append("关键页面覆盖不足")

    if missing_states and not ocr_available:
        preview = "；".join(missing_states[:6])
        if status == "ready":
            status = "supplement_required"
        missing_coverage.append(f"Capture Mission 未覆盖关键状态：{preview}")
        required_actions.extend(
            [
                f"补这些 must_capture_states 的截图或 markdown 说明：{preview}",
                "如页面较多，可在 inputs/screens/ 补 screens-map.md 或 screens-index.md，写最小截图映射",
            ]
        )
        hard_missing.append("关键状态覆盖不足")

    if missing_descriptions and not ocr_available:
        preview = "；".join(missing_descriptions[:6])
        if status == "ready":
            status = "supplement_required"
        missing_coverage.append(f"OCR 不可用时，Capture Mission 的关键页面说明仍缺失：{preview}")
        required_actions.extend(
            [
                f"为这些页面补充 markdown 说明：{preview}",
                "补充 inputs/screens-description.md 或同目录页面说明文件",
                "如页面较多，可在 inputs/screens/ 补 screens-map.md 或 screens-index.md，写最小截图映射",
            ]
        )
        hard_missing.append("无 OCR 时缺少关键页面说明")

    if naming_issues:
        verification_gaps.append("当前部分截图命名不规范，计划匹配主要依赖 markdown/OCR 补充")
        optional_suggestions.append(
            "如当前自动匹配仍不稳定，可在 inputs/screens/ 补 screens-map.md 或 screens-index.md，按“截图文件 -> 页面 / 状态”写最小映射"
        )
        optional_suggestions.append(_rename_accelerator_suggestion(naming_issues))

    if clarification_items:
        required_actions.append(
            f"先确认这 {len(clarification_items)} 张歧义截图的页面/状态，其余 screenshot -> page/state 映射已自动起草"
        )
        verification_gaps.append(
            "少量截图仍需轻量确认；系统已自动起草其余 screenshot -> page/state 映射"
        )
    elif clarification_suppressed_reason and raw_clarification_items:
        verification_gaps.append(clarification_suppressed_reason)

    if status == "ready" and not required_actions:
        required_actions = []
    elif status == "supplement_required":
        status_reason = "开跑前发现 Capture Mission 仍有明显缺口，先一次性补齐更有利于首次达到 final_delivery_ready。"
    elif status == "blocked":
        status_reason = "开跑前缺少最基础的 Capture Mission 输入，继续运行只会制造无效往返。"

    return EvidenceInputGuidance(
        pre_run_status=status,  # type: ignore[arg-type]
        current_input_sufficient=status == "ready",
        status_reason=status_reason,
        required_actions=_dedupe_preserve(required_actions),
        optional_suggestions=_dedupe_preserve(optional_suggestions),
        missing_pages=missing_pages,
        missing_states=missing_states,
        missing_descriptions=missing_descriptions,
        naming_issues=naming_issues,
        hard_requirements_missing=_dedupe_preserve(hard_missing),
        clarification_items=clarification_items,
        confidence="high" if status in {"ready", "blocked"} else "medium",
        source_channel="mixed" if description_refs else "metadata",
        evidence_basis=[
            f"capture_mission_version={mission.mission_version}",
            f"planned_page_count={planned_page_count}",
            f"matched_planned_page_count={matched_page_count}",
            f"image_count={len(image_refs)}",
            f"description_count={len(description_refs)}",
            f"ocr_available={ocr_available}",
            *(
                [f"clarification_suppressed_reason={clarification_suppressed_reason}"]
                if clarification_suppressed_reason
                else []
            ),
        ],
        verification_gaps=_dedupe_preserve(
            [
                *verification_gaps,
                *missing_coverage,
                *(
                    []
                    if status == "ready"
                    else [f"final pass line: {line}" for line in mission.final_delivery_pass_line]
                ),
            ]
        ),
    )


def probe_runtime_capabilities() -> dict[str, str | bool | None]:
    """Expose OCR capability probing for preflight and tests."""
    result = probe_ocr_backend()
    return {
        "ocr_available": result.available,
        "ocr_backend": result.backend,
        "ocr_error": result.error,
    }


def load_and_analyze(
    screenshots_dir: Path | str,
    task_checklist_lite: str | None = None,
    required_evidence_plan: RequiredEvidencePlan | dict[str, Any] | None = None,
    *,
    output_dir: Path | str | None = None,
    run_id: str | None = None,
    stage_id: str | None = None,
) -> LoadAnalyzeResult:
    """Analyze screenshot evidence with OCR-aware local capabilities."""
    screenshots_dir = Path(screenshots_dir)
    output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
    files = _collect_files(screenshots_dir)
    probe = probe_ocr_backend()
    ocr_backend = probe.backend if probe.available else None
    required_plan = _coerce_required_evidence_plan(required_evidence_plan)
    refs = _build_refs(files, root=screenshots_dir, ocr_backend=ocr_backend)
    refs, _baseline_clarification_items = _apply_draft_mappings(
        refs,
        plan=required_plan,
    )
    baseline_assessment = _evidence_assessment(
        refs,
        ocr_available=probe.available,
        task_checklist_lite=task_checklist_lite,
        required_evidence_plan=required_plan,
    )
    remediated_refs = refs
    remediation_summary: dict[str, Any] = {
        "auto_remediation_attempted": False,
        "auto_remediation_changed": False,
        "auto_remediation_note_count": 0,
        "auto_remediation_note_paths": [],
    }
    if baseline_assessment.delivery_status != "final_delivery_ready":
        remediated_refs, remediation_summary = _auto_remediate_refs(
            refs,
            output_dir=output_dir,
            task_checklist_lite=task_checklist_lite,
            required_evidence_plan=required_plan,
        )
    remediated_refs, _clarification_items = _apply_draft_mappings(
        remediated_refs,
        plan=required_plan,
    )
    evidence_assessment = _evidence_assessment(
        remediated_refs,
        ocr_available=probe.available,
        task_checklist_lite=task_checklist_lite,
        required_evidence_plan=required_plan,
    )
    evidence_fingerprint = _evidence_fingerprint(files, root=screenshots_dir)
    clarification_state_path, already_surfaced = _persist_clarification_state(
        output_dir=output_dir,
        evidence_fingerprint=evidence_fingerprint,
        clarification_items=evidence_assessment.clarification_items,
    )
    clarification_package_path = _write_clarification_package(
        output_dir=output_dir,
        package_root=_CLARIFICATION_DIRNAME,
        refs=remediated_refs,
        clarification_items=evidence_assessment.clarification_items,
    )
    if clarification_package_path is not None:
        evidence_assessment.clarification_package_path = clarification_package_path
        if (
            evidence_assessment.clarification_items
            and evidence_assessment.delivery_status != "final_delivery_ready"
            and not already_surfaced
        ):
            evidence_assessment.required_actions = _dedupe_preserve(
                [
                    f"先查看 {clarification_package_path}，只确认其中列出的歧义截图",
                    *evidence_assessment.required_actions,
                ]
            )
        evidence_assessment.evidence_basis.append(
            f"clarification_package_path={clarification_package_path}"
        )
    if clarification_state_path is not None:
        evidence_assessment.evidence_basis.append(
            f"clarification_state_path={clarification_state_path}"
        )
    remediation_state = _persist_remediation_state(
        output_dir=output_dir,
        evidence_fingerprint=evidence_fingerprint,
        evidence_assessment=evidence_assessment,
    )
    evidence_assessment.coverage_summary.update(
        {
            "delivery_status_before_remediation": baseline_assessment.delivery_status,
            "delivery_status_after_remediation": evidence_assessment.delivery_status,
            "required_evidence_plan_version": required_plan.plan_version if required_plan is not None else None,
            "run_id": run_id,
            "stage_id": stage_id,
            **remediation_summary,
            **remediation_state,
        }
    )
    first_pass_success_breakdown = _first_pass_success_breakdown(
        baseline_assessment=baseline_assessment,
        evidence_assessment=evidence_assessment,
        remediation_summary=remediation_summary,
    )
    targeted_acquisition_plan = _build_targeted_acquisition_plan(
        image_refs=[ref for ref in remediated_refs if ref.kind == "image"],
        required_evidence_plan=required_plan,
        evidence_assessment=evidence_assessment,
        first_pass_success_breakdown=first_pass_success_breakdown,
        ocr_available=probe.available,
    )
    targeted_acquisition_plan_path = _write_targeted_acquisition_plan(
        output_dir=output_dir,
        plan=targeted_acquisition_plan,
    )
    if targeted_acquisition_plan is not None and targeted_acquisition_plan_path is not None:
        targeted_acquisition_plan = targeted_acquisition_plan.model_copy(
            update={"plan_doc_path": targeted_acquisition_plan_path}
        )

    targeted_actions = [
        _suggested_action_text(item)
        for item in (
            targeted_acquisition_plan.highest_value_next_captures[:3]
            if targeted_acquisition_plan is not None
            else []
        )
    ]
    targeted_summary_updates: dict[str, Any] = {}
    targeted_verification_gaps: list[str] = []
    targeted_basis: list[str] = []
    if targeted_acquisition_plan is not None:
        targeted_summary_updates = {
            "targeted_acquisition_contract_version": targeted_acquisition_plan.contract_version,
            "targeted_acquisition_must_count": len(targeted_acquisition_plan.must_acquire_now),
            "targeted_acquisition_clarify_count": len(targeted_acquisition_plan.clarify_existing_evidence),
            "targeted_acquisition_nice_count": len(targeted_acquisition_plan.nice_to_have_later),
            "highest_value_next_capture_targets": [
                (
                    f"{item.target_page}:{item.target_state}"
                    if item.target_state
                    else item.target_page
                )
                for item in targeted_acquisition_plan.highest_value_next_captures
            ],
            "expected_metric_lift_metrics": [
                lift.metric for lift in targeted_acquisition_plan.expected_metric_lift
            ],
            "targeted_acquisition_plan_path": targeted_acquisition_plan.plan_doc_path,
        }
        targeted_verification_gaps = [
            (
                "下一步优先按 targeted acquisition plan 处理这些最高收益动作："
                + "；".join(
                    (
                        f"{item.target_page}:{item.target_state}"
                        if item.target_state
                        else item.target_page
                    )
                    for item in targeted_acquisition_plan.highest_value_next_captures[:3]
                )
            )
        ] if (
            targeted_acquisition_plan.highest_value_next_captures
            and evidence_assessment.delivery_status != "final_delivery_ready"
        ) else []
        targeted_basis = [
            f"targeted_acquisition_contract_version={targeted_acquisition_plan.contract_version}",
            *(
                [f"targeted_acquisition_plan_path={targeted_acquisition_plan.plan_doc_path}"]
                if targeted_acquisition_plan.plan_doc_path
                else []
            ),
        ]
    evidence_assessment = evidence_assessment.model_copy(
        update={
            "first_pass_success_breakdown": first_pass_success_breakdown,
            "targeted_acquisition_plan": targeted_acquisition_plan,
            "required_actions": _dedupe_preserve(
                [
                    *(
                        [
                            (
                                f"先看 {targeted_acquisition_plan.plan_doc_path}，按 highest-value next captures 只补最值钱的几项"
                            )
                        ]
                        if (
                            targeted_acquisition_plan is not None
                            and targeted_acquisition_plan.plan_doc_path
                            and targeted_acquisition_plan.highest_value_next_captures
                            and evidence_assessment.delivery_status != "final_delivery_ready"
                        )
                        else []
                    ),
                    *targeted_actions,
                    *evidence_assessment.required_actions,
                ]
            ),
            "coverage_summary": {
                **evidence_assessment.coverage_summary,
                **targeted_summary_updates,
            },
            "verification_gaps": _dedupe_preserve(
                [
                    *evidence_assessment.verification_gaps,
                    *targeted_verification_gaps,
                ]
            ),
            "evidence_basis": [
                *evidence_assessment.evidence_basis,
                *targeted_basis,
            ],
        }
    )
    client_mode_metrics = _client_mode_metrics(evidence_assessment)
    benchmark_summary = _client_mode_benchmark_summary(
        evidence_assessment,
        client_mode_metrics,
    )
    benchmark_artifact_paths: dict[str, str] = {}
    if output_dir is not None:
        benchmark_dir = output_dir / _BENCHMARK_DIRNAME
        capture_mission_path = evidence_assessment.coverage_summary.get("capture_mission_path")
        benchmark_artifact_paths = {
            "benchmark_dir": str(benchmark_dir.resolve()),
            "benchmark_json_path": str((benchmark_dir / _BENCHMARK_JSON_FILENAME).resolve()),
            "benchmark_markdown_path": str((benchmark_dir / _BENCHMARK_MD_FILENAME).resolve()),
            **(
                {"capture_mission_path": str(capture_mission_path)}
                if isinstance(capture_mission_path, str)
                and str(capture_mission_path)
                else {}
            ),
            **(
                {"targeted_acquisition_plan_path": str(targeted_acquisition_plan.plan_doc_path)}
                if targeted_acquisition_plan is not None and targeted_acquisition_plan.plan_doc_path
                else {}
            ),
            **(
                {"clarification_package_path": str(evidence_assessment.clarification_package_path)}
                if evidence_assessment.clarification_package_path
                else {}
            ),
        }
    benchmark_summary = benchmark_summary.model_copy(update={"artifact_paths": benchmark_artifact_paths})
    _write_benchmark_summary(output_dir=output_dir, summary=benchmark_summary)
    evidence_assessment = evidence_assessment.model_copy(
        update={
            "client_mode_metrics": client_mode_metrics,
            "benchmark_summary": benchmark_summary,
            "coverage_summary": {
                **evidence_assessment.coverage_summary,
                "client_mode_metrics_contract_version": client_mode_metrics.contract_version,
                "benchmark_contract_version": benchmark_summary.contract_version,
                "benchmark_delivery_status": benchmark_summary.delivery_status,
                "benchmark_input_quality_class": benchmark_summary.input_quality_class,
                **benchmark_artifact_paths,
            },
            "evidence_basis": [
                *evidence_assessment.evidence_basis,
                f"client_mode_metrics_contract_version={client_mode_metrics.contract_version}",
                f"benchmark_contract_version={benchmark_summary.contract_version}",
            ],
        }
    )
    return LoadAnalyzeResult(
        screenshots=remediated_refs,
        image_analysis=_analysis_summary(
            remediated_refs,
            ocr_available=probe.available,
            ocr_backend=ocr_backend,
            evidence_assessment=evidence_assessment,
            remediation_summary={
                "run_id": run_id,
                "stage_id": stage_id,
                "delivery_status_before_remediation": baseline_assessment.delivery_status,
                "delivery_status_after_remediation": evidence_assessment.delivery_status,
                "required_evidence_plan_version": required_plan.plan_version if required_plan is not None else None,
                "first_pass_final_rate": first_pass_success_breakdown["first_pass_final_rate"],
                "clarification_burden": first_pass_success_breakdown["clarification_burden"][
                    "clarification_needed_count"
                ],
                "supplement_cause_classification": first_pass_success_breakdown[
                    "supplement_cause_classification"
                ],
                "upstream_diagnosis": first_pass_success_breakdown["upstream_diagnosis"],
                **remediation_summary,
                **remediation_state,
            },
        ),
        evidence_assessment=evidence_assessment,
    )


__all__ = ["load_and_analyze", "plan_required_evidence", "probe_runtime_capabilities"]
