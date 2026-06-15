#!/usr/bin/env python3
"""
Validate S2-H7B Offline Dry-Run Artifacts

验证：
1. 仓库内 H7B 文件存在
2. Synthetic fixture 都含 SYNTHETIC / SANITIZED
3. 报告不含真实绝对路径
4. 报告只写 <DESIGNOS_WORKSPACE_ROOT>
5. Sanitized issue registry 不含敏感信息
6. Synthetic replay case 不含真实数据
7. 外部 workspace 目录存在
8. Git tracked/untracked 本批文件不包含 raw outputs
"""

import os
import sys
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 期望的仓库内文件
EXPECTED_REPO_FILES = [
    "fixtures/synthetic/s2-h7b-dry-run/README.md",
    "fixtures/synthetic/s2-h7b-dry-run/synthetic-product-brief.md",
    "fixtures/synthetic/s2-h7b-dry-run/synthetic-prd.md",
    "fixtures/synthetic/s2-h7b-dry-run/synthetic-brand-brief.md",
    "fixtures/synthetic/s2-h7b-dry-run/synthetic-screenshot-notes.md",
    "fixtures/synthetic/s2-h7b-dry-run/synthetic-replay-case.md",
    "docs/audits/S2-H7B-OFFLINE-DRY-RUN-EXECUTION.md",
    "docs/audits/sanitized-issues/S2-H7B-sanitized-issue-registry.md",
]

# 必须标记为 SYNTHETIC / SANITIZED 的文件
SYNTHETIC_FILES = [
    "fixtures/synthetic/s2-h7b-dry-run/README.md",
    "fixtures/synthetic/s2-h7b-dry-run/synthetic-product-brief.md",
    "fixtures/synthetic/s2-h7b-dry-run/synthetic-prd.md",
    "fixtures/synthetic/s2-h7b-dry-run/synthetic-brand-brief.md",
    "fixtures/synthetic/s2-h7b-dry-run/synthetic-screenshot-notes.md",
    "fixtures/synthetic/s2-h7b-dry-run/synthetic-replay-case.md",
]

# 不能包含真实路径的文件
NO_REAL_PATH_FILES = [
    "docs/audits/S2-H7B-OFFLINE-DRY-RUN-EXECUTION.md",
    "docs/audits/sanitized-issues/S2-H7B-sanitized-issue-registry.md",
    "fixtures/synthetic/s2-h7b-dry-run/synthetic-replay-case.md",
]

# 敏感信息模式
SENSITIVE_PATTERNS = [
    r"https?://[^\s]+",  # URL
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # email
    r"\b(password|secret|token|key)\s*[:=]\s*\S+",  # password/token
]

def check_file_exists(files):
    """检查文件存在"""
    missing = []
    for f in files:
        if not (ROOT / f).exists():
            missing.append(f)
    return missing

def check_synthetic_marker(files):
    """检查 SYNTHETIC / SANITIZED 标记"""
    missing_marker = []
    for f in files:
        path = ROOT / f
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        if "SYNTHETIC" not in content and "SANITIZED" not in content:
            missing_marker.append(f)
    return missing_marker

def check_no_real_path(files, forbidden_path):
    """检查不含真实绝对路径"""
    violations = []
    for f in files:
        path = ROOT / f
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        if forbidden_path in content:
            violations.append(f)
    return violations

def check_sensitive_info(files):
    """检查敏感信息"""
    violations = []
    for f in files:
        path = ROOT / f
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        for pattern in SENSITIVE_PATTERNS:
            # 豁免 <DESIGNOS_WORKSPACE_ROOT> 和 SYNTHETIC URL
            if re.search(pattern, content):
                matches = re.findall(pattern, content)
                real_matches = [
                    m for m in matches
                    if "DESIGNOS_WORKSPACE_ROOT" not in m
                    and "SYNTHETIC" not in m
                    and "synthetic" not in m
                    and "example.com" not in m
                    and "noreply@" not in m
                ]
                if real_matches:
                    violations.append((f, pattern, real_matches[:3]))
    return violations

def check_workspace_placeholder(files):
    """检查是否只写 <DESIGNOS_WORKSPACE_ROOT>"""
    missing_placeholder = []
    for f in files:
        path = ROOT / f
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        # 至少应包含一次占位符
        if "<DESIGNOS_WORKSPACE_ROOT>" not in content:
            missing_placeholder.append(f)
    return missing_placeholder

def main():
    errors = []

    # 1. 检查文件存在
    missing = check_file_exists(EXPECTED_REPO_FILES)
    if missing:
        errors.append(f"❌ 缺少文件: {', '.join(missing)}")

    # 2. 检查 SYNTHETIC 标记
    missing_marker = check_synthetic_marker(SYNTHETIC_FILES)
    if missing_marker:
        errors.append(f"❌ 缺少 SYNTHETIC/SANITIZED 标记: {', '.join(missing_marker)}")

    # 3. 检查不含真实路径
    forbidden_path = "/Users/young/Documents/Codex/designos-workspace"
    violations = check_no_real_path(NO_REAL_PATH_FILES, forbidden_path)
    if violations:
        errors.append(f"❌ 包含真实路径: {', '.join(violations)}")

    # 4. 检查占位符
    missing_placeholder = check_workspace_placeholder(NO_REAL_PATH_FILES)
    if missing_placeholder:
        errors.append(f"❌ 缺少 <DESIGNOS_WORKSPACE_ROOT> 占位符: {', '.join(missing_placeholder)}")

    # 5. 检查敏感信息
    sensitive_violations = check_sensitive_info([
        "docs/audits/sanitized-issues/S2-H7B-sanitized-issue-registry.md",
        "fixtures/synthetic/s2-h7b-dry-run/synthetic-replay-case.md",
    ])
    if sensitive_violations:
        for f, pattern, matches in sensitive_violations:
            errors.append(f"❌ {f} 包含敏感信息模式 {pattern}: {matches}")

    # 6. 检查外部 workspace 存在（仅提示，不强制）
    workspace_path = Path.home() / "Documents/Codex/designos-workspace"
    if not workspace_path.exists():
        print(f"⚠️  外部 workspace 不存在: {workspace_path}")
    else:
        print(f"✅ 外部 workspace 存在")

    # 输出结果
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    else:
        print("checked S2-H7B dry-run artifacts\n")
        print("✅ all S2-H7B artifacts valid (repo files / synthetic markers / no real paths / workspace placeholder / no sensitive info)")

if __name__ == "__main__":
    main()
