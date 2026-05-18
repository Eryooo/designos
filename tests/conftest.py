"""Shared pytest fixtures for integration and E2E tests."""

from __future__ import annotations

import pytest
from pathlib import Path

from kernel.contracts.schemas import Issue
from kernel.contracts.enums import SeverityLevel


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    """Create a minimal temporary workspace directory."""
    ws = tmp_path / "test-project"
    ws.mkdir()
    (ws / "inputs").mkdir()
    (ws / "inputs" / "prd.md").write_text("# Test PRD\n## 功能\n- 登录\n- 注册")
    return ws


@pytest.fixture
def mock_llm_response() -> str:
    """Mock LLM response JSON string."""
    return '{"modules": [{"name": "auth", "features": ["login", "register"]}]}'


@pytest.fixture
def sample_issues() -> list[Issue]:
    """Return 5 test Issues covering all severity levels."""
    return [
        Issue(
            id="I-001",
            title="登录按钮对比度不足",
            description="主登录按钮前景色与背景色对比度低于 WCAG AA 标准 4.5:1",
            severity=SeverityLevel.CRITICAL,
            principle_ids=["H4"],
            evidence_refs=["E-001"],
            user_impact="视力障碍用户无法识别登录入口，导致无法完成核心任务",
            suggestion="将按钮背景色改为 #0057B8，确保对比度 ≥ 4.5:1",
        ),
        Issue(
            id="I-002",
            title="表单错误提示缺失",
            description="密码输入框校验失败时无任何错误提示文字",
            severity=SeverityLevel.MAJOR,
            principle_ids=["H9"],
            evidence_refs=["E-002"],
            user_impact="用户不知道输入哪里出错，需要反复猜测",
            suggestion="在输入框下方添加内联错误提示，说明具体校验规则",
        ),
        Issue(
            id="I-003",
            title="加载状态缺少进度反馈",
            description="提交表单后页面无任何加载指示器",
            severity=SeverityLevel.MINOR,
            principle_ids=["H1"],
            evidence_refs=["E-003"],
            user_impact="用户不确定操作是否已提交，可能重复点击",
            suggestion="添加 spinner 或进度条，在请求期间禁用提交按钮",
        ),
        Issue(
            id="I-004",
            title="注册流程步骤指示不清晰",
            description="多步骤注册流程缺少步骤进度指示器",
            severity=SeverityLevel.MINOR,
            principle_ids=["H1", "H8"],
            evidence_refs=["E-004"],
            user_impact="用户不清楚当前处于第几步，无法预估完成时间",
            suggestion="在页面顶部添加步骤条，高亮当前步骤",
        ),
        Issue(
            id="I-005",
            title="帮助文档链接文字不具描述性",
            description='帮助链接文字为"点击这里"，缺乏上下文',
            severity=SeverityLevel.SUGGESTION,
            principle_ids=["H6"],
            evidence_refs=["E-005"],
            user_impact="屏幕阅读器用户无法从链接文字判断目标内容",
            suggestion='将链接文字改为"查看注册帮助文档"等描述性文字',
        ),
    ]
