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
from typing import Any, Iterable

from ocr_runtime import OCRLine, probe_ocr_backend, run_ocr
from schemas import (
    ClarificationItem,
    CriticalStateRequirement,
    DescriptionLink,
    DraftScreenshotMapping,
    EvidenceAssessment,
    EvidenceInputGuidance,
    EvidencePageRequirement,
    ImageAnalysisSummary,
    LoadAnalyzeResult,
    PlanRequiredEvidenceResult,
    ReadabilityAssessment,
    RequiredEvidencePlan,
    ScreenshotRef,
    StateCategory,
    TextCue,
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
_PLAN_VERSION = "2026-05-22"
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
    weights = {"ocr": 7, "markdown": 5, "metadata": 3, "filename": 2}
    source_scores: dict[str, int] = {key: 0 for key in weights}
    basis: list[str] = []

    for channel in ("ocr", "markdown", "metadata", "filename"):
        overlap = page_tokens & channel_tokens.get(channel, set())
        if not overlap:
            continue
        score = weights[channel] + len(overlap)
        source_scores[channel] += score
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
        "metadata": Path(ref.relative_path).parent.as_posix().lower(),
        "filename": Path(ref.relative_path).stem.lower(),
    }
    for channel, blob in exact_channel_blobs.items():
        if requirement.page_name.lower() and requirement.page_name.lower() in blob:
            source_scores[channel] += weights[channel] + 2
            basis.append(f"{channel} explicitly mentions page name '{requirement.page_name}'")
        elif requirement.page_key.lower() in blob:
            source_scores[channel] += weights[channel]
            basis.append(f"{channel} explicitly mentions page key '{requirement.page_key}'")

    total_score = sum(source_scores.values())
    dominant_channel = max(
        source_scores.items(),
        key=lambda item: (item[1], {"ocr": 4, "markdown": 3, "metadata": 2, "filename": 1}[item[0]]),
    )[0]
    return {
        "requirement": requirement,
        "score": total_score,
        "source_scores": source_scores,
        "source_channel": dominant_channel,
        "evidence_basis": basis,
    }


def _draft_mapping_for_ref(
    ref: ScreenshotRef,
    *,
    plan: RequiredEvidencePlan | None,
) -> DraftScreenshotMapping | None:
    if plan is None:
        return None

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
    delta = int(best["score"]) - int(runner_up["score"]) if runner_up is not None else int(best["score"])
    dominant_channel = str(best["source_channel"])
    candidate_pages = [str(item["requirement"].page_name) for item in candidates[:3]]
    matched_states = sorted(_state_categories_for_ref(ref))

    strong_semantic_signal = dominant_channel in {"ocr", "markdown"}
    high_confidence = strong_semantic_signal and int(best["score"]) >= 8 and delta >= 3
    medium_confidence = int(best["score"]) >= 5 and delta >= 2

    confidence = "low"
    if high_confidence:
        confidence = "high"
    elif medium_confidence:
        confidence = "medium"

    clarification_needed = confidence == "low" or (runner_up is not None and delta <= 1)
    clarification_reason: str | None = None
    verification_gaps: list[str] = []
    if clarification_needed:
        clarification_reason = (
            "multiple planned pages remain close in confidence"
            if runner_up is not None and delta <= 1
            else "mapping mainly relies on weaker filename or directory hints"
        )
        verification_gaps.append("confirm page/state mapping only for this ambiguous screenshot")

    if dominant_channel in {"metadata", "filename"} and confidence == "high":
        confidence = "medium"

    draft_mapping = DraftScreenshotMapping(
        page_key=best["requirement"].page_key,
        page_name=best["requirement"].page_name,
        matched_states=matched_states,
        candidate_pages=candidate_pages,
        clarification_needed=clarification_needed,
        clarification_reason=clarification_reason,
        confidence=confidence,  # type: ignore[arg-type]
        source_channel=dominant_channel,  # type: ignore[arg-type]
        evidence_basis=list(best["evidence_basis"]),
        unsupported=["no full semantic scene understanding"],
        unknown=[] if not clarification_needed else ["exact page mapping still needs light confirmation"],
        verification_gaps=verification_gaps,
    )
    final_delivery_eligible, final_delivery_reason = _final_delivery_mapping_verdict(
        ref,
        draft_mapping=draft_mapping,
    )
    return draft_mapping.model_copy(
        update={
            "final_delivery_eligible": final_delivery_eligible,
            "final_delivery_reason": final_delivery_reason,
        }
    )


def _final_delivery_mapping_verdict(
    ref: ScreenshotRef,
    *,
    draft_mapping: DraftScreenshotMapping,
) -> tuple[bool, str]:
    if draft_mapping.clarification_needed or draft_mapping.page_name is None:
        return False, "mapping still needs clarification and cannot count toward final delivery"
    if draft_mapping.confidence == "high":
        return True, "high-confidence mapping can count toward final delivery coverage"
    if draft_mapping.confidence != "medium":
        return False, "only high confidence or explicitly re-verified medium mappings can count toward final delivery"

    page_name = draft_mapping.page_name.lower()
    filename_blob = Path(ref.relative_path).stem.lower()
    has_filename_page_hint = bool(page_name and page_name in filename_blob)
    has_high_conf_description_link = any(link.confidence == "high" for link in ref.description_links)
    has_non_default_state = any(state != "default" for state in draft_mapping.matched_states)

    semantic_channels: set[str] = set()
    for group in (
        ref.page_title_candidates,
        ref.button_text_candidates,
        ref.navigation_text_candidates,
        ref.state_text_candidates,
    ):
        for cue in group:
            if cue.source_channel not in {"ocr", "markdown"}:
                continue
            if page_name and page_name in cue.value.lower():
                semantic_channels.add(cue.source_channel)

    if "ocr" in semantic_channels and (
        "markdown" in semantic_channels or has_filename_page_hint or has_high_conf_description_link
    ):
        return True, "medium-confidence mapping was re-verified by OCR plus an independent supporting signal"
    if "markdown" in semantic_channels and has_high_conf_description_link and (
        has_filename_page_hint or has_non_default_state
    ):
        return True, "medium-confidence mapping was re-verified by filename-specific markdown evidence plus state support"
    return False, "medium-confidence mapping remains provisional and cannot by itself unlock final delivery"


def _apply_draft_mappings(
    refs: list[ScreenshotRef],
    *,
    plan: RequiredEvidencePlan | None,
) -> tuple[list[ScreenshotRef], list[ClarificationItem]]:
    if plan is None:
        return refs, []

    updated_refs: list[ScreenshotRef] = list(refs)
    clarification_items: list[ClarificationItem] = []
    for idx, ref in enumerate(updated_refs):
        if ref.kind != "image":
            continue
        draft_mapping = _draft_mapping_for_ref(ref, plan=plan)
        if draft_mapping is None:
            continue
        updated_refs[idx] = ref.model_copy(update={"draft_mapping": draft_mapping})
        if draft_mapping.clarification_needed:
            clarification_items.append(
                ClarificationItem(
                    screenshot_id=ref.id,
                    relative_path=ref.relative_path,
                    candidate_pages=draft_mapping.candidate_pages,
                    candidate_states=draft_mapping.matched_states,
                    clarification_reason=draft_mapping.clarification_reason
                    or "mapping confidence is still too low to auto-confirm",
                    confidence=draft_mapping.confidence,
                    source_channel=draft_mapping.source_channel,
                    evidence_basis=draft_mapping.evidence_basis,
                    unsupported=draft_mapping.unsupported,
                    unknown=draft_mapping.unknown,
                    verification_gaps=draft_mapping.verification_gaps,
                )
            )
    return updated_refs, clarification_items


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

    return {
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
) -> list[dict[str, str]]:
    image_tokens = set(_normalized_tokens(Path(ref.relative_path).stem))
    image_tokens.update(_normalized_tokens(ref.ocr_text_preview))
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
    image_parent = Path(ref.relative_path).parent.as_posix()
    stem = Path(ref.relative_path).stem.lower()
    scored: list[tuple[int, dict[str, str]]] = []

    for section in sections:
        raw_text = f"{section['title']}\n{section['body']}"
        lowered = raw_text.lower()
        section_tokens = set(_normalized_tokens(raw_text))
        overlap = _token_overlap(image_tokens, section_tokens)
        score = len(overlap)
        exact_filename_match = bool(stem and stem in lowered)
        if exact_filename_match:
            score += 6
        elif len(overlap) >= 2:
            score += 2
        elif len(overlap) == 1:
            score += 1
        if image_parent == Path(section["source_path"]).parent.as_posix() and (exact_filename_match or overlap):
            score += 1
        if len(overlap) >= 3:
            score += 2
        if score >= 2 and (exact_filename_match or len(overlap) >= 2):
            scored.append((score, section))

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
    if matched_sections:
        first_body_line = next(
            (line.strip() for line in matched_sections[0]["body"].splitlines() if line.strip()),
            "",
        )
        if first_body_line:
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
            description_text = description_texts.get(link.description_id, "")
            desc_titles, desc_buttons, desc_navs, desc_states = _markdown_cues(
                description_text,
                link.description_path,
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
    required_plan = _coerce_required_evidence_plan(required_evidence_plan)
    task_coverage = _task_coverage_summary(image_refs, task_checklist_lite)
    plan_coverage = _plan_coverage_summary(
        image_refs,
        plan=required_plan,
        ocr_available=ocr_available,
    )
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
    clarification_items = [
        ClarificationItem(
            screenshot_id=ref.id,
            relative_path=ref.relative_path,
            candidate_pages=ref.draft_mapping.candidate_pages,
            candidate_states=ref.draft_mapping.matched_states,
            clarification_reason=ref.draft_mapping.clarification_reason
            or "mapping confidence is still too low to auto-confirm",
            confidence=ref.draft_mapping.confidence,
            source_channel=ref.draft_mapping.source_channel,
            evidence_basis=ref.draft_mapping.evidence_basis,
            unsupported=ref.draft_mapping.unsupported,
            unknown=ref.draft_mapping.unknown,
            verification_gaps=ref.draft_mapping.verification_gaps,
        )
        for ref in image_refs
        if ref.draft_mapping is not None and ref.draft_mapping.clarification_needed
    ]
    missing_state_categories = (
        _dedupe_preserve(
            state.rsplit(":", 1)[-1]
            for state in plan_missing_states
        )
        if plan_missing_states
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

    if plan_missing_pages:
        preview = "；".join(plan_missing_pages[:6])
        missing_coverage.append(f"关键计划缺少页面：{preview}")
        required_actions.append(f"补这些关键页面截图：{preview}")

    if plan_missing_states:
        preview = "；".join(plan_missing_states[:6])
        missing_coverage.append(f"关键计划缺少状态：{preview}")
        required_actions.append(f"补这些关键状态截图或说明：{preview}")

    if plan_missing_descriptions and not ocr_available:
        preview = "；".join(plan_missing_descriptions[:6])
        missing_coverage.append(f"关键计划缺少页面说明：{preview}")
        required_actions.extend(
            [
                f"这些关键页面缺说明，请补 markdown 说明：{preview}",
                "如页面较多，可先在 inputs/screens/ 补 screens-map.md 或 screens-index.md，写关键截图 -> 页面/状态 映射",
            ]
        )

    if plan_naming_issues:
        verification_gaps.append("当前部分截图命名不规范，自动匹配更多依赖 OCR / markdown / 轻量映射补充")
        if missing_coverage or blocking_reasons:
            verification_gaps.append(_rename_accelerator_suggestion(plan_naming_issues))

    if clarification_items and (missing_coverage or blocking_reasons):
        required_actions.append(
            f"先确认这 {len(clarification_items)} 张歧义截图的页面/状态，其余截图映射已自动起草"
        )
        verification_gaps.append("少量截图仍需轻量确认；系统已自动起草其余 screenshot -> page/state 映射")

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
                not final_plan_missing_pages
                and not final_plan_missing_states
                and (ocr_available or not final_plan_missing_descriptions)
                and (
                    not isinstance(final_delivery_page_ratio, float)
                    or final_delivery_page_ratio >= 0.8
                )
                and (
                    not isinstance(final_delivery_state_ratio, float)
                    or final_delivery_state_ratio >= 0.8
                )
            )
        )
        plan_fallback_ready = (
            required_plan is None
            or (
                (
                    not isinstance(planned_page_ratio, float)
                    or planned_page_ratio >= 0.5
                )
                and (
                    not isinstance(planned_state_ratio, float)
                    or planned_state_ratio >= 0.4
                )
            )
        )
        final_delivery_ready = (
            image_count >= 5
            and readable_ratio >= 0.8
            and text_rich_ratio >= 0.8
            and (ocr_available or description_link_ratio >= 0.8)
            and (
                key_task_coverage_ratio is None
                or (
                    isinstance(key_task_coverage_ratio, float)
                    and key_task_coverage_ratio >= 0.8
                )
            )
            and plan_final_ready
        )
        fallback_safe = (
            image_count >= 1
            and readable_ratio >= 0.6
            and text_rich_ratio >= 0.6
            and (ocr_available or bool(description_refs))
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
                final_plan_missing_pages or final_plan_missing_states or final_plan_missing_descriptions
            ):
                if final_plan_missing_pages:
                    verification_gaps.append(
                        "这些关键页面当前仅有 provisional mapping，尚不能计入 final_delivery_ready："
                        + "；".join(final_plan_missing_pages[:6])
                    )
                if final_plan_missing_states:
                    verification_gaps.append(
                        "这些关键状态当前只被 provisional mapping 覆盖，尚不能计入 final_delivery_ready："
                        + "；".join(final_plan_missing_states[:6])
                    )
                if final_plan_missing_descriptions and not ocr_available:
                    verification_gaps.append(
                        "这些关键页面说明缺少足够强的二次验证，尚不能计入 final_delivery_ready："
                        + "；".join(final_plan_missing_descriptions[:6])
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
        "clarification_needed_count": len(clarification_items),
        "clarification_relative_paths": [item.relative_path for item in clarification_items],
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
        blocking_reasons=sorted(set(blocking_reasons)),
        required_actions=sorted(set(required_actions)),
        missing_coverage=sorted(set(missing_coverage)),
        coverage_summary=coverage_summary,
        unsupported=[
            "full page semantic summary",
            "automatic task_id attribution",
            "automatic module_id attribution",
            "automatic scenario intent inference",
        ],
        unknown=["unseen interaction states not covered by screenshots"] if image_refs else [],
        verification_gaps=sorted(set(verification_gaps)),
        clarification_items=clarification_items,
    )


def _analysis_summary(
    refs: list[ScreenshotRef],
    *,
    ocr_available: bool,
    ocr_backend: str | None,
    evidence_assessment: EvidenceAssessment,
    remediation_summary: dict[str, Any] | None = None,
) -> ImageAnalysisSummary:
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
            **(remediation_summary or {}),
        },
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
        "# Auto-drafted Screenshot Mapping",
        "",
        "系统已自动起草大部分 screenshot -> page/state 映射。只有标记为 `needs_confirmation` 的截图需要你补最少量确认。",
        "",
    ]
    for ref in refs:
        if ref.kind != "image" or ref.draft_mapping is None:
            continue
        draft = ref.draft_mapping
        states = ", ".join(draft.matched_states) if draft.matched_states else "default"
        status = "needs_confirmation" if draft.clarification_needed else "auto_confirmed"
        page_name = draft.page_name or "unknown"
        draft_lines.append(
            f"- `{ref.relative_path}` -> `{page_name}` / states: `{states}` "
            f"[{draft.confidence}, {draft.source_channel}, {status}]"
        )

    clarification_lines = [
        "# Minimal Clarification Needed",
        "",
        "只确认以下低置信度截图，其余 mapping 已由系统自动起草并继续使用。",
        "",
    ]
    for item in clarification_items:
        candidate_pages = " / ".join(item.candidate_pages) if item.candidate_pages else "unknown"
        candidate_states = ", ".join(item.candidate_states) if item.candidate_states else "default"
        clarification_lines.extend(
            [
                f"## {item.relative_path}",
                f"- screenshot_id: {item.screenshot_id}",
                f"- candidate_pages: {candidate_pages}",
                f"- candidate_states: {candidate_states}",
                f"- confidence: {item.confidence}",
                f"- source_channel: {item.source_channel}",
                f"- reason: {item.clarification_reason}",
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

    for idx, ref in enumerate(updated_refs):
        if ref.kind != "image":
            continue

        matched_sections = _select_description_sections(ref, sections)
        matched_tasks = _match_tasks_for_ref(ref, task_checklist_lite)
        matched_pages = []
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
                "auto-remediation note is derived evidence; verify details against the original screenshot"
            ],
        )
        existing_links = list(ref.description_links)
        if not any(link.description_path == note_link.description_path for link in existing_links):
            existing_links.append(note_link)
        existing_non_markdown_titles = [
            cue for cue in ref.page_title_candidates if cue.source_channel != "markdown"
        ]
        existing_non_markdown_buttons = [
            cue for cue in ref.button_text_candidates if cue.source_channel != "markdown"
        ]
        existing_non_markdown_navs = [
            cue for cue in ref.navigation_text_candidates if cue.source_channel != "markdown"
        ]
        existing_non_markdown_states = [
            cue for cue in ref.state_text_candidates if cue.source_channel != "markdown"
        ]

        verification_gaps = [
            gap
            for gap in ref.verification_gaps
            if gap != "no linked markdown description for this screenshot"
        ]

        updated_refs[idx] = ref.model_copy(
            update={
                "description_links": existing_links,
                "page_title_candidates": _merge_unique(existing_non_markdown_titles + note_titles),
                "button_text_candidates": _merge_unique(existing_non_markdown_buttons + note_buttons),
                "navigation_text_candidates": _merge_unique(existing_non_markdown_navs + note_navs),
                "state_text_candidates": _merge_unique(existing_non_markdown_states + note_states),
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
    clarification_package_path = _write_clarification_package(
        output_dir=output_dir,
        package_root=f"{_PLANNING_DIRNAME}/{_PLANNING_CLARIFICATION_DIRNAME}",
        refs=refs,
        clarification_items=evidence_input_guidance.clarification_items,
    )
    if clarification_package_path is not None:
        evidence_input_guidance.clarification_package_path = clarification_package_path
        if evidence_input_guidance.clarification_items and evidence_input_guidance.pre_run_status != "ready":
            evidence_input_guidance.required_actions = _dedupe_preserve(
                [
                    f"先查看 {clarification_package_path}，只确认其中列出的歧义截图",
                    *evidence_input_guidance.required_actions,
                ]
            )
        evidence_input_guidance.evidence_basis.append(
            f"clarification_package_path={clarification_package_path}"
        )

    if screenshots_path is not None:
        evidence_fingerprint = _evidence_fingerprint(files, root=screenshots_path)
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
    clarification_items = [
        ClarificationItem(
            screenshot_id=ref.id,
            relative_path=ref.relative_path,
            candidate_pages=ref.draft_mapping.candidate_pages,
            candidate_states=ref.draft_mapping.matched_states,
            clarification_reason=ref.draft_mapping.clarification_reason
            or "mapping confidence is still too low to auto-confirm",
            confidence=ref.draft_mapping.confidence,
            source_channel=ref.draft_mapping.source_channel,
            evidence_basis=ref.draft_mapping.evidence_basis,
            unsupported=ref.draft_mapping.unsupported,
            unknown=ref.draft_mapping.unknown,
            verification_gaps=ref.draft_mapping.verification_gaps,
        )
        for ref in image_refs
        if ref.draft_mapping is not None and ref.draft_mapping.clarification_needed
    ]
    planned_page_count = int(plan_coverage["planned_page_count"] or 0)
    matched_page_count = int(plan_coverage["matched_planned_page_count"] or 0)
    planned_page_ratio = plan_coverage["planned_page_coverage_ratio"]

    status = "ready"
    status_reason = "当前截图输入已覆盖关键页面计划，可继续进入正式截图证据分析。"
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
                f"当前仅 {len(image_refs)} 张截图，低于建议的关键页面最小目标 {min_image_target} 张"
            )
            required_actions.append(
                f"优先补足关键页面截图，建议至少 {min_image_target} 张，覆盖主流程核心页面"
            )
            hard_missing.append("关键页面截图数量不足")
        if missing_pages:
            preview = "；".join(missing_pages[:6])
            if status == "ready" and (
                not isinstance(planned_page_ratio, float) or planned_page_ratio < 0.8 or not ocr_available
            ):
                status = "supplement_required"
            missing_coverage.append(f"关键页面计划未覆盖：{preview}")
            required_actions.append(f"优先补这些关键页面截图：{preview}")
            hard_missing.append("关键页面覆盖不足")

    if missing_states and not ocr_available:
        preview = "；".join(missing_states[:6])
        if status == "ready":
            status = "supplement_required"
        missing_coverage.append(f"关键状态计划未覆盖：{preview}")
        required_actions.extend(
            [
                f"补这些关键状态的截图或 markdown 说明：{preview}",
                "如页面较多，可在 inputs/screens/ 补 screens-map.md 或 screens-index.md，写最小截图映射",
            ]
        )
        hard_missing.append("关键状态覆盖不足")

    if missing_descriptions and not ocr_available:
        preview = "；".join(missing_descriptions[:6])
        if status == "ready":
            status = "supplement_required"
        missing_coverage.append(f"OCR 不可用时，关键页面说明仍缺失：{preview}")
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

    if clarification_items and (missing_pages or missing_states or missing_descriptions or hard_missing):
        required_actions.append(
            f"先确认这 {len(clarification_items)} 张歧义截图的页面/状态，其余截图映射已自动起草"
        )
        verification_gaps.append(
            "少量截图仍需轻量确认；系统已自动起草其余 screenshot -> page/state 映射"
        )

    if status == "ready" and not required_actions:
        required_actions = []
    elif status == "supplement_required":
        status_reason = "开跑前发现关键页面/状态/说明仍有明显缺口，先一次性补齐更有利于首次达到 final_delivery_ready。"
    elif status == "blocked":
        status_reason = "开跑前缺少最基础的截图输入，继续运行只会制造无效往返。"

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
            f"planned_page_count={planned_page_count}",
            f"matched_planned_page_count={matched_page_count}",
            f"image_count={len(image_refs)}",
            f"description_count={len(description_refs)}",
            f"ocr_available={ocr_available}",
        ],
        verification_gaps=_dedupe_preserve(verification_gaps + missing_coverage),
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
    clarification_package_path = _write_clarification_package(
        output_dir=output_dir,
        package_root=f"{_REMEDIATION_DIRNAME}/{_REMEDIATION_CLARIFICATION_DIRNAME}",
        refs=remediated_refs,
        clarification_items=evidence_assessment.clarification_items,
    )
    if clarification_package_path is not None:
        evidence_assessment.clarification_package_path = clarification_package_path
        if evidence_assessment.clarification_items and evidence_assessment.delivery_status != "final_delivery_ready":
            evidence_assessment.required_actions = _dedupe_preserve(
                [
                    f"先查看 {clarification_package_path}，只确认其中列出的歧义截图",
                    *evidence_assessment.required_actions,
                ]
            )
        evidence_assessment.evidence_basis.append(
            f"clarification_package_path={clarification_package_path}"
        )
    evidence_fingerprint = _evidence_fingerprint(files, root=screenshots_dir)
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
                **remediation_summary,
                **remediation_state,
            },
        ),
        evidence_assessment=evidence_assessment,
    )


__all__ = ["load_and_analyze", "plan_required_evidence", "probe_runtime_capabilities"]
