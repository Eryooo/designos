"""Test fixtures for excel-builder tests."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_issues():
    """Create mock Issue data for testing."""
    return [
        {
            "id": "I-001",
            "title": "登录按钮位置不明显",
            "description": "用户在首页找不到登录入口，按钮隐藏在右上角",
            "severity": "critical",
            "principle_ids": ["H1", "H4"],
            "journey_stage_id": "JS-001",
            "task_id": "T-001",
            "module_id": "登录模块",
            "evidence_refs": ["E-001", "E-002"],
            "user_impact": "用户无法快速找到登录入口，导致流失",
            "suggestion": "将登录按钮移至页面中心位置，增大尺寸",
            "source_basis": "screenshot",
        },
        {
            "id": "I-002",
            "title": "表单错误提示不清晰",
            "description": "输入错误时，错误提示文案模糊",
            "severity": "major",
            "principle_ids": ["H5", "H9"],
            "journey_stage_id": "JS-002",
            "task_id": "T-002",
            "module_id": "表单模块",
            "evidence_refs": ["E-003"],
            "user_impact": "用户不知道如何修正错误，增加操作成本",
            "suggestion": "提供具体的错误原因和修正建议",
            "source_basis": "screenshot",
        },
        {
            "id": "I-003",
            "title": "加载动画缺失",
            "description": "数据加载时没有任何反馈",
            "severity": "minor",
            "principle_ids": ["H1"],
            "journey_stage_id": "JS-003",
            "task_id": "T-003",
            "module_id": "数据展示",
            "evidence_refs": ["E-004"],
            "user_impact": "用户不确定系统是否在响应",
            "suggestion": "添加加载动画或进度条",
            "source_basis": "screenshot",
        },
        {
            "id": "I-004",
            "title": "配色方案可优化",
            "description": "当前配色对比度不足",
            "severity": "suggestion",
            "principle_ids": ["H8"],
            "journey_stage_id": "JS-001",
            "task_id": "T-001",
            "module_id": "视觉设计",
            "evidence_refs": ["E-005"],
            "user_impact": "部分用户可能看不清文字",
            "suggestion": "提高文字与背景的对比度",
            "source_basis": "screenshot",
        },
        {
            "id": "I-005",
            "title": "搜索功能响应慢",
            "description": "搜索结果需要等待3秒以上",
            "severity": "major",
            "principle_ids": ["H1", "H5"],
            "journey_stage_id": "JS-004",
            "task_id": "T-004",
            "module_id": "搜索模块",
            "evidence_refs": ["E-006", "E-007"],
            "user_impact": "用户体验差，可能放弃使用搜索功能",
            "suggestion": "优化搜索算法，添加缓存机制",
            "source_basis": "screenshot",
        },
    ]


__all__ = ["temp_output_dir", "mock_issues"]
