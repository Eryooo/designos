#!/usr/bin/env python3
"""validate_input_quality_templates.py — 校验 S2-H5 input-quality-gate 模板.

纯标准库(无第三方依赖)。校验项:
  1. 5 个 input-quality-gate.md 都存在。
  2. 每个模板含 10 个统一章节(## 1.~## 10.)。
  3. 每个模板含全部 4 个 input_decision 枚举。
  4. 每个模板引用对应 golden template path。
  5. 每个模板引用对应 failure-modes.md path。
  6. 每个模板含 Gap Ledger / Assumption Ledger / Clarification Questions。
  7. 无过度承诺(完全自动化 / 生产就绪 / 已验证 / 资深设计师水平已达成 /
     validated in production / final production ready)——作为正向陈述。
  8. 无真实业务敏感词命中(仅基础检查,scan-sensitive 更全面)。

退出码:0 = 全过;1 = 有失败。
用法:python3 scripts/validate_input_quality_templates.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# skill -> (input-quality path, golden path, failure-modes path)
SKILLS = {
    "prd2proto": (
        "skills/prd2proto/templates/input-quality-gate.md",
        "skills/prd2proto/templates/golden-prd2proto-output.md",
        "skills/prd2proto/eval/failure/failure-modes.md",
    ),
    "uxeval": (
        "skills/uxeval/templates/input-quality-gate.md",
        "skills/uxeval/templates/golden-evaluation-report.md",
        "skills/uxeval/eval/failure/failure-modes.md",
    ),
    "ai-analytics": (
        "skills/ai-analytics/templates/input-quality-gate.md",
        "skills/ai-analytics/templates/golden-analysis-output.md",
        "skills/ai-analytics/eval/failure/failure-modes.md",
    ),
    "ip-design": (
        "skills/ip-design/templates/input-quality-gate.md",
        "skills/ip-design/templates/golden-ip-design-output.md",
        "skills/ip-design/eval/failure/failure-modes.md",
    ),
    "brand-creative": (
        "skills/brand-creative/templates/input-quality-gate.md",
        "skills/brand-creative/templates/golden-brand-creative-output.md",
        "skills/brand-creative/eval/failure/failure-modes.md",
    ),
}

REQUIRED_SECTIONS = [f"## {i}." for i in range(1, 11)]

INPUT_DECISION_ENUMS = [
    "ready",
    "ready_with_assumptions",
    "needs_user_clarification",
    "blocked_insufficient_input",
]

LEDGER_KEYWORDS = ["Gap Ledger", "Assumption", "Clarification Questions"]

# S2-H7.1: 新增字段检查
H71_REQUIRED_FIELDS = [
    "Recommended Missing Fields (S2-H7.1)",
    "recommended_field",
    "minimum_needed_to_continue",
    "Recommended User Questions (S2-H7.1)",
    "Minimum Needed to Continue (S2-H7.1)",
]

# 过度承诺(作为正向断言算违规,出现在"禁止"清单语境豁免)
OVERCLAIM_PATTERNS = [
    "完全自动化",
    "生产就绪",
    "已验证",
    "资深设计师水平已达成",
    "validated in production",
    "final production ready",
    "fully automated",
]

# 基础敏感词(scan-sensitive 更全面)
SENSITIVE_PATTERNS = ["真实客户", "真实账号", "production URL"]


def main() -> int:
    errors: list[str] = []

    for skill, (iqp, golden, fm_path) in SKILLS.items():
        p = REPO_ROOT / iqp
        if not p.is_file():
            errors.append(f"{skill}: missing input-quality template {iqp}")
            continue
        text = p.read_text(encoding="utf-8")

        # 2. 10 章节
        for sec in REQUIRED_SECTIONS:
            if sec not in text:
                errors.append(f"{skill}: missing section '{sec}'")

        # 3. 4 个 input_decision 枚举
        for enum in INPUT_DECISION_ENUMS:
            if enum not in text:
                errors.append(f"{skill}: missing input_decision enum '{enum}'")

        # 4. 引用 golden path
        golden_name = Path(golden).name
        if golden_name not in text:
            errors.append(f"{skill}: does not reference golden template '{golden_name}'")

        # 5. 引用 failure-modes path
        if "eval/failure/failure-modes.md" not in text:
            errors.append(f"{skill}: does not reference failure-modes.md")

        # 6. Ledger 关键词
        for kw in LEDGER_KEYWORDS:
            if kw not in text:
                errors.append(f"{skill}: missing '{kw}'")

        # 6.1 S2-H7.1 新增字段检查
        for field in H71_REQUIRED_FIELDS:
            if field not in text:
                errors.append(f"{skill}: missing S2-H7.1 field '{field}'")

        # 7. 过度承诺检查(豁免禁止清单语境)
        for line in text.splitlines():
            low = line.lower()
            for pat in OVERCLAIM_PATTERNS:
                if pat.lower() in low:
                    # 豁免:该行含"禁止/不得/❌/防止/示例/严禁/不允许/声称.../修正/阻断"
                    # —— 输入门必然讨论 not_allowed_claims 的负向场景
                    if any(
                        tok in line
                        for tok in [
                            "禁止", "不得", "❌", "防止", "示例", "严禁", "不允许",
                            "声称", "修正", "阻断", "命中", "却含",
                        ]
                    ):
                        continue
                    errors.append(
                        f"{skill}: positive overclaim '{pat}' in line: {line.strip()[:60]}"
                    )

        # 8. 敏感词基础检查(豁免讨论"如何防止/打码/阻断"的语境)
        # —— input gate 必然讨论 constitution 中的 not_allowed_claims 负向场景
        for line in text.splitlines():
            for pat in SENSITIVE_PATTERNS:
                if pat in line:
                    if any(
                        tok in line
                        for tok in [
                            "防止", "打码", "脱敏", "阻断", "禁止", "严禁", "❌",
                            "不允许", "示例", "blocker", "FM-",
                        ]
                    ):
                        continue
                    errors.append(f"{skill}: contains sensitive pattern '{pat}': {line.strip()[:60]}")

    print(f"checked {len(SKILLS)} input-quality templates")
    if errors:
        print(f"\n❌ {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(
        "\n✅ all input-quality templates valid (10 sections / 4 enums / golden+failure refs / ledgers / no overclaim / no sensitive)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
