#!/usr/bin/env python3
"""validate_self_review_templates.py — 校验 S2-H4 self-review-gate 模板.

纯标准库(无第三方依赖)。校验项:
  1. 5 个 self-review-gate.md 都存在。
  2. 每个模板含 10 个统一章节(## 1.~## 10.)。
  3. 每个模板正好引用 8 个 fm_id(FM-<SKILL>-00x)。
  4. 每个模板含全部 4 个 delivery_decision 枚举。
  5. 每个模板引用对应 golden template path。
  6. 每个模板引用对应 failure-modes.md path。
  7. 无过度声明(fully automated / 完全自动化 / 生产就绪 / 资深设计师水平已达成 /
     validated in production)——作为正向陈述。

退出码:0 = 全过;1 = 有失败。
用法:python3 scripts/validate_self_review_templates.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# skill -> (self-review path, golden path, failure-modes path, FM prefix)
SKILLS = {
    "prd2proto": (
        "skills/prd2proto/templates/self-review-gate.md",
        "skills/prd2proto/templates/golden-prd2proto-output.md",
        "skills/prd2proto/eval/failure/failure-modes.md",
        "FM-PRD2PROTO-",
    ),
    "uxeval": (
        "skills/uxeval/templates/self-review-gate.md",
        "skills/uxeval/templates/golden-evaluation-report.md",
        "skills/uxeval/eval/failure/failure-modes.md",
        "FM-UXEVAL-",
    ),
    "ai-analytics": (
        "skills/ai-analytics/templates/self-review-gate.md",
        "skills/ai-analytics/templates/golden-analysis-output.md",
        "skills/ai-analytics/eval/failure/failure-modes.md",
        "FM-AIANALYTICS-",
    ),
    "ip-design": (
        "skills/ip-design/templates/self-review-gate.md",
        "skills/ip-design/templates/golden-ip-design-output.md",
        "skills/ip-design/eval/failure/failure-modes.md",
        "FM-IPDESIGN-",
    ),
    "brand-creative": (
        "skills/brand-creative/templates/self-review-gate.md",
        "skills/brand-creative/templates/golden-brand-creative-output.md",
        "skills/brand-creative/eval/failure/failure-modes.md",
        "FM-BRANDCREATIVE-",
    ),
}

REQUIRED_SECTIONS = [f"## {i}." for i in range(1, 11)]

DELIVERY_ENUMS = ["pass", "pass_with_minor_warnings", "degrade_with_gaps", "block"]

# 过度声明:作为"正向断言"出现才算违规。本校验用简单子串匹配 + 上下文豁免。
# 模板里这些词只允许出现在"禁止声明清单"语境(行内含"命中 → block"或"禁止"),
# 否则视为违规。
OVERCLAIM_PATTERNS = [
    "fully automated",
    "完全自动化",
    "生产就绪",
    "资深设计师水平已达成",
    "validated in production",
]


def main() -> int:
    errors: list[str] = []

    for skill, (srp, golden, fm_path, fm_prefix) in SKILLS.items():
        p = REPO_ROOT / srp
        if not p.is_file():
            errors.append(f"{skill}: missing self-review template {srp}")
            continue
        text = p.read_text(encoding="utf-8")

        # 2. 10 章节
        for sec in REQUIRED_SECTIONS:
            if sec not in text:
                errors.append(f"{skill}: missing section '{sec}'")

        # 3. 正好 8 个 fm_id
        fm_ids = sorted(set(re.findall(rf"{re.escape(fm_prefix)}\d+", text)))
        if len(fm_ids) != 8:
            errors.append(f"{skill}: expected 8 fm_id, got {len(fm_ids)} ({fm_ids})")

        # 4. 4 个 delivery_decision 枚举
        for enum in DELIVERY_ENUMS:
            if enum not in text:
                errors.append(f"{skill}: missing delivery_decision enum '{enum}'")

        # 5. 引用 golden path
        golden_name = Path(golden).name
        if golden_name not in text:
            errors.append(f"{skill}: does not reference golden template '{golden_name}'")

        # 6. 引用 failure-modes path
        if "eval/failure/failure-modes.md" not in text:
            errors.append(f"{skill}: does not reference failure-modes.md")

        # 7. 过度声明检查(豁免"禁止声明"语境的行)
        for line in text.splitlines():
            low = line.lower()
            for pat in OVERCLAIM_PATTERNS:
                if pat.lower() in low:
                    # 豁免:该行处于禁止清单(含 "命中" / "禁止" / "→ block" / "不宣称")
                    if any(tok in line for tok in ["命中", "禁止", "block", "不宣称", "不得", "❌"]):
                        continue
                    errors.append(f"{skill}: positive overclaim '{pat}' in line: {line.strip()[:60]}")

    print(f"checked {len(SKILLS)} self-review templates")
    if errors:
        print(f"\n❌ {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\n✅ all self-review templates valid (10 sections / 8 FM / 4 enums / golden+failure refs / no overclaim)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
