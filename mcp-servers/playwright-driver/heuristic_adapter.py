"""Adapter: convert playwright-driver evidence to heuristic-engine DetectionRequest format."""

from __future__ import annotations

from typing import Any

from schemas import ExecutionResult, StepEvidence


def build_detection_request(
    execution_results: list[ExecutionResult],
    principles: list[dict[str, str]] | None = None,
    task_checklist: dict[str, Any] | None = None,
    constitution: str = "",
) -> dict[str, Any]:
    """Convert playwright-driver execution results into heuristic-engine DetectionRequest format.

    Returns a dict matching heuristic-engine's DetectionRequest schema.
    """
    screenshots = []
    dom_snapshots = []
    screenshot_counter = 0

    for result in execution_results:
        for ev in result.evidence:
            if ev.screenshot_path:
                screenshot_counter += 1
                sid = f"S-{screenshot_counter:03d}"
                screenshots.append({
                    "id": sid,
                    "path": ev.screenshot_path,
                    "flow": result.task_title,
                    "region": "",
                    "page_url": ev.url,
                    "note": f"Step {ev.step}, action={ev.action.value}",
                })

                if ev.dom_snapshot:
                    dom_snapshots.append(
                        _build_dom_snapshot(sid, ev)
                    )

            elif ev.dom_snapshot and screenshots:
                last_sid = screenshots[-1]["id"]
                dom_snapshots.append(
                    _build_dom_snapshot(last_sid, ev)
                )

    if principles is None:
        principles = _default_principles()

    request = {
        "screenshots": screenshots,
        "principles": principles,
        "mode": "web",
        "dom_data": dom_snapshots if dom_snapshots else None,
        "constitution": constitution,
    }

    if task_checklist:
        request["task_checklist"] = task_checklist

    return request


def _build_dom_snapshot(screenshot_id: str, ev: StepEvidence) -> dict[str, Any]:
    """Convert a StepEvidence dom_snapshot into heuristic-engine DomSnapshot format."""
    dom = ev.dom_snapshot or {}
    elements = dom.get("elements", [])

    nodes = []
    has_loading = False
    has_error = False

    for el in elements:
        text = el.get("text", "")
        tag = el.get("tag", "")
        role = el.get("role", "") or ""

        if any(kw in text.lower() for kw in ("loading", "加载中", "请稍候")):
            has_loading = True
        if any(kw in text.lower() for kw in ("error", "错误", "失败", "异常")):
            has_error = True

        nodes.append({
            "tag": tag,
            "role": role,
            "text": text[:200],
            "placeholder": el.get("placeholder", ""),
            "aria_label": el.get("aria_label", ""),
            "classes": el.get("classes", []),
            "attrs": {k: v for k, v in el.items() if k not in ("tag", "text", "role", "placeholder", "aria_label", "classes")},
        })

    return {
        "screenshot_id": screenshot_id,
        "nodes": nodes,
        "has_loading_indicator": has_loading,
        "has_error_message": has_error,
        "page_url": ev.url,
    }


def _default_principles() -> list[dict[str, str]]:
    """Return the standard 10 Nielsen heuristics as default principles."""
    return [
        {"id": "H1", "name": "系统状态可见性", "description": "系统应始终让用户知道当前状态", "source": "Nielsen"},
        {"id": "H2", "name": "匹配用户心智", "description": "系统应使用用户熟悉的语言和概念", "source": "Nielsen"},
        {"id": "H3", "name": "用户控制与自由度", "description": "用户应能轻松撤销和重做操作", "source": "Nielsen"},
        {"id": "H4", "name": "一致性与标准化", "description": "遵循平台惯例，保持一致", "source": "Nielsen"},
        {"id": "H5", "name": "错误预防", "description": "通过设计防止错误发生", "source": "Nielsen"},
        {"id": "H6", "name": "识别而非记忆", "description": "减少用户记忆负担", "source": "Nielsen"},
        {"id": "H7", "name": "灵活高效", "description": "为新手和专家都提供高效路径", "source": "Nielsen"},
        {"id": "H8", "name": "美学与极简", "description": "界面不应包含无关信息", "source": "Nielsen"},
        {"id": "H9", "name": "帮助用户识别和恢复错误", "description": "错误信息应清晰且提供解决方案", "source": "Nielsen"},
        {"id": "H10", "name": "帮助和说明", "description": "必要时提供帮助文档", "source": "Nielsen"},
    ]
