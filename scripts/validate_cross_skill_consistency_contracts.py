#!/usr/bin/env python3
"""validate_cross_skill_consistency_contracts.py — 校验 S2-H6 跨 skill 一致性契约.

纯标准库(无第三方依赖)。校验项:
  1. 总控报告存在。
  2. 全局 review 模板存在且含 10 节。
  3. 5 个 cross-skill contract 文件存在。
  4. 每个 contract 含 10 个统一章节(## 1.~## 10.)。
  5. 每个 contract 含 4 个 consistency_decision 枚举。
  6. 每个 contract 含必需块。
  7. 无过度声明(豁免负向语境)。
  8. 无真实业务敏感词(豁免负向语境)。

退出码:0 = 全过;1 = 有失败。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

MASTER_REPORT = "docs/audits/S2-H6-CROSS-SKILL-CONSISTENCY-CONTRACT.md"
GLOBAL_REVIEW = "templates/cross-skill-consistency-review.md"

CONTRACTS = {
    "ai-analytics-to-prd2proto":
        "docs/contracts/cross-skill/ai-analytics-to-prd2proto.md",
    "ai-analytics-to-brand-creative":
        "docs/contracts/cross-skill/ai-analytics-to-brand-creative.md",
    "brand-creative-internal":
        "docs/contracts/cross-skill/brand-creative-internal.md",
    "ip-design-internal":
        "docs/contracts/cross-skill/ip-design-internal.md",
    "prd2proto-internal":
        "docs/contracts/cross-skill/prd2proto-internal.md",
}

REQUIRED_SECTIONS = [f"## {i}." for i in range(1, 11)]

CONSISTENCY_ENUMS = [
    "consistent",
    "consistent_with_carried_gaps",
    "needs_reconciliation",
    "blocked_inconsistent",
]

REQUIRED_BLOCKS = [

    "Required Field Mapping",
    "Gap / Assumption",
    "Conflict Rules",
    "User Reconciliation Prompts",
    "Related Gates",
]

# S2-H7.1: 新增字段检查
H71_REQUIRED_FIELDS = [
    "Recommended Reconciliation (S2-H7.1)",
    "recommended_reconciliation",
    "reconciliation_options",
    "preferred_resolution",
    "user_confirmation_needed",
]


OVERCLAIM_PATTERNS = [
    "完全自动化",
    "生产就绪",
    "已验证",
    "资深设计师水平已达成",
    "validated in production",
    "final production ready",
    "fully automated",
]

SENSITIVE_PATTERNS = ["真实客户", "真实账号", "production URL"]

EXEMPT_TOKENS = [
    "禁止", "不得", "❌", "防止", "示例", "严禁", "不允许",
    "声称", "修正", "阻断", "命中", "却含", "blocked_inconsistent",
    "FM-", "冲突", "改写", "矛盾",
]


def check_text(name: str, text: str, errors: list[str]) -> None:
    # sections
    for sec in REQUIRED_SECTIONS:
        if sec not in text:
            errors.append(f"{name}: missing section '{sec}'")
    # enums
    for enum in CONSISTENCY_ENUMS:
        if enum not in text:
            errors.append(f"{name}: missing consistency_decision enum '{enum}'")
    # required blocks
    for blk in REQUIRED_BLOCKS:
        if blk not in text:
            errors.append(f"{name}: missing block '{blk}'")
    # overclaim
    for line in text.splitlines():
        low = line.lower()
        for pat in OVERCLAIM_PATTERNS:
            if pat.lower() in low and not any(t in line for t in EXEMPT_TOKENS):
                errors.append(f"{name}: positive overclaim '{pat}': {line.strip()[:50]}")
    # sensitive
    for line in text.splitlines():
        for pat in SENSITIVE_PATTERNS:
            if pat in line and not any(t in line for t in EXEMPT_TOKENS):
                errors.append(f"{name}: sensitive '{pat}': {line.strip()[:50]}")


def main() -> int:
    errors: list[str] = []

    # 1. master report
    if not (REPO_ROOT / MASTER_REPORT).is_file():
        errors.append(f"missing master report: {MASTER_REPORT}")

    # 2. global review template (10 sections)
    gr = REPO_ROOT / GLOBAL_REVIEW
    if not gr.is_file():
        errors.append(f"missing global review template: {GLOBAL_REVIEW}")
    else:
        text = gr.read_text(encoding="utf-8")
        for sec in REQUIRED_SECTIONS:
            if sec not in text:
                errors.append(f"global-review: missing section '{sec}'")

    # 3-8. contracts
    for name, path in CONTRACTS.items():
        p = REPO_ROOT / path
        if not p.is_file():
            errors.append(f"{name}: missing file {path}")
            continue
        check_text(name, p.read_text(encoding="utf-8"), errors)

    print(f"checked master report + global review + {len(CONTRACTS)} cross-skill contracts")
    if errors:
        print(f"\n❌ {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(
        "\n✅ all cross-skill consistency contracts valid "
        "(10 sections / 4 enums / required blocks / no overclaim / no sensitive)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
