"""Shared pytest fixtures for the heuristic-engine tests.

Provides reusable :class:`ScreenshotRef`, :class:`DomSnapshot`, and the full
``DetectionRequest`` payload variants so each test focuses on a single rule
or contract assertion.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make the server modules importable without packaging install.
SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from principles_library import default_principles  # noqa: E402
from schemas import (  # noqa: E402
    DetectionRequest,
    DomNode,
    DomSnapshot,
    HeuristicPrinciple,
    ScreenshotRef,
    TaskChecklist,
    TaskItem,
)


FIXTURE_IMAGE = Path(__file__).parent / "fixtures" / "blank.png"


@pytest.fixture(scope="session", autouse=True)
def _ensure_fixture_image() -> None:
    """Materialise a tiny PNG so LLM judge encoding can be exercised."""

    FIXTURE_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    if FIXTURE_IMAGE.exists():
        return
    # 1x1 transparent PNG, hand-crafted to keep the fixture binary-free.
    payload = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
        b"\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00"
        b"\x00IEND\xaeB`\x82"
    )
    FIXTURE_IMAGE.write_bytes(payload)


@pytest.fixture
def basic_principles() -> list[HeuristicPrinciple]:
    """Return the default principle catalogue."""

    return default_principles()


@pytest.fixture
def loading_screenshot() -> ScreenshotRef:
    return ScreenshotRef(
        id="S-LOAD",
        path=FIXTURE_IMAGE,
        flow="任务运行中",
        region="提交",
    )


@pytest.fixture
def failure_screenshot() -> ScreenshotRef:
    return ScreenshotRef(
        id="S-FAIL",
        path=FIXTURE_IMAGE,
        flow="导入失败",
        region="错误",
    )


@pytest.fixture
def calm_screenshot() -> ScreenshotRef:
    return ScreenshotRef(
        id="S-CALM",
        path=FIXTURE_IMAGE,
        flow="账户概览",
        region="头部",
    )


@pytest.fixture
def overload_snapshot() -> DomSnapshot:
    """A snapshot with 6 distinct action buttons in one row."""

    nodes = [
        DomNode(tag="button", text="详情"),
        DomNode(tag="button", text="编辑"),
        DomNode(tag="button", text="运行"),
        DomNode(tag="button", text="停止"),
        DomNode(tag="button", text="删除"),
        DomNode(tag="button", text="更多"),
    ]
    return DomSnapshot(screenshot_id="S-CALM", nodes=nodes)


@pytest.fixture
def jargon_snapshot() -> DomSnapshot:
    nodes = [
        DomNode(tag="span", text="OCR 解析"),
        DomNode(tag="span", text="ASR 识别"),
    ]
    return DomSnapshot(screenshot_id="S-CALM", nodes=nodes)


@pytest.fixture
def naked_form_snapshot() -> DomSnapshot:
    nodes = [
        DomNode(tag="input", text=""),
        DomNode(tag="textarea", text=""),
    ]
    return DomSnapshot(screenshot_id="S-CALM", nodes=nodes)


@pytest.fixture
def task_checklist() -> TaskChecklist:
    return TaskChecklist(
        tasks=[
            TaskItem(
                id="T-001",
                title="登录到分类分级模块",
                description="管理员第一次进入模块",
                journey_stage="进入与定位",
                role="管理员",
            )
        ],
        journey_summary="管理员从登录到完成识别任务的旅程。",
    )


@pytest.fixture
def detection_request_factory() -> object:
    """Factory used by core tests to build :class:`DetectionRequest` quickly."""

    def _make(
        screenshots: list[ScreenshotRef],
        principles: list[HeuristicPrinciple],
        *,
        task_checklist: TaskChecklist | None = None,
        constitution: str = "证据必须可见，不输出敏感信息。",
        mode: str = "client",
        dom_data: list[DomSnapshot] | None = None,
    ) -> DetectionRequest:
        return DetectionRequest(
            screenshots=screenshots,
            principles=principles,
            task_checklist=task_checklist or TaskChecklist(),
            constitution=constitution,
            mode=mode,  # type: ignore[arg-type]
            dom_data=dom_data,
        )

    return _make
