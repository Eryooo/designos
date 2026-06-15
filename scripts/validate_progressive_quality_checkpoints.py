#!/usr/bin/env python3
"""validate_progressive_quality_checkpoints.py — 校验 S2-H5.1 渐进质量检查点.

纯标准库(无第三方依赖)。校验项:
  1. 总控报告存在。
  2. 全局 checkpoint log 模板存在。
  3. 5 个 skill progressive-quality-checkpoints.md 存在。
  4. 每个 skill 模板含 10 个统一章节(## 1.~## 10.)。
  5. 每个 skill 模板正好含 5 个 checkpoint id(CP-{P/U/A/I/B}{1-5})。
  6. decision enum 只含 5 个:continue / continue_with_gaps / ask_user /
     degrade_scope / stop_blocked。
  7. 每个模板含:User Notices / Carry-Forward Rules / Degrade Scope Rules /
     Stop Blocked Rules / Handoff To H4 Self Review。
  8. 无过度声明。
  9. 无真实业务敏感词(豁免讨论"防止/禁止"的负向语境)。

退出码:0 = 全过;1 = 有失败。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

MASTER_REPORT = "docs/audits/S2-H5.1-PROGRESSIVE-QUALITY-CHECKPOINTS.md"
GLOBAL_LOG = "templates/progressive-quality-checkpoint-log.md"

# skill -> (template path, CP prefix letter)
SKILLS = {
    "prd2proto": ("skills/prd2proto/templates/progressive-quality-checkpoints.md", "P"),
    "uxeval": ("skills/uxeval/templates/progressive-quality-checkpoints.md", "U"),
    "ai-analytics": ("skills/ai-analytics/templates/progressive-quality-checkpoints.md", "A"),
    "ip-design": ("skills/ip-design/templates/progressive-quality-checkpoints.md", "I"),
    "brand-creative": ("skills/brand-creative/templates/progressive-quality-checkpoints.md", "B"),
}

REQUIRED_SECTIONS = [f"## {i}." for i in range(1, 11)]

DECISION_ENUMS = [
    "continue",
    "continue_with_gaps",
    "ask_user",
    "degrade_scope",
    "stop_blocked",
]

REQUIRED_BLOCKS = [
    "User Notices",
    "Carry-Forward Rules",
    "Degrade Scope Rules",
    "Stop Blocked Rules",
    "Handoff To H4 Self Review",
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
    "声称", "修正", "阻断", "命中", "却含", "打码", "脱敏",
    "FM-", "blocker", "stop_blocked",
]


def main() -> int:
    errors: list[str] = []

    # 1. 总控报告
    if not (REPO_ROOT / MASTER_REPORT).is_file():
        errors.append(f"missing master report: {MASTER_REPORT}")

    # 2. 全局 log 模板
    if not (REPO_ROOT / GLOBAL_LOG).is_file():
        errors.append(f"missing global checkpoint log template: {GLOBAL_LOG}")

    # 3-9. 各 skill 模板
    for skill, (tpl, letter) in SKILLS.items():
        p = REPO_ROOT / tpl
        if not p.is_file():
            errors.append(f"{skill}: missing template {tpl}")
            continue
        text = p.read_text(encoding="utf-8")

        # 4. 10 章节
        for sec in REQUIRED_SECTIONS:
            if sec not in text:
                errors.append(f"{skill}: missing section '{sec}'")

        # 5. 正好 5 个 CP id
        cp_ids = sorted(set(re.findall(rf"CP-{letter}\d+", text)))
        if len(cp_ids) != 5:
            errors.append(f"{skill}: expected 5 CP ids, got {len(cp_ids)} ({cp_ids})")

        # 6. 5 个 decision 枚举
        for enum in DECISION_ENUMS:
            if enum not in text:
                errors.append(f"{skill}: missing decision enum '{enum}'")

        # 7. 必含 block
        for blk in REQUIRED_BLOCKS:
            if blk not in text:
                errors.append(f"{skill}: missing block '{blk}'")

        # 8. 过度声明
        for line in text.splitlines():
            low = line.lower()
            for pat in OVERCLAIM_PATTERNS:
                if pat.lower() in low and not any(t in line for t in EXEMPT_TOKENS):
                    errors.append(f"{skill}: positive overclaim '{pat}': {line.strip()[:50]}")

        # 9. 敏感词
        for line in text.splitlines():
            for pat in SENSITIVE_PATTERNS:
                if pat in line and not any(t in line for t in EXEMPT_TOKENS):
                    errors.append(f"{skill}: sensitive '{pat}': {line.strip()[:50]}")

    print(f"checked master report + global log + {len(SKILLS)} skill checkpoint templates")
    if errors:
        print(f"\n❌ {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(
        "\n✅ all progressive checkpoint templates valid "
        "(10 sections / 5 CP each / 5 enums / required blocks / no overclaim / no sensitive)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
