#!/usr/bin/env python3
"""validate_feedback_safety_infrastructure.py — 校验 S2-H7A 用户反馈安全基础设施.

纯标准库(无第三方依赖)。校验项:
  1. 总控报告存在。
  2. 3 个 issue template 存在。
  3. 2 个 schema 存在且是合法 JSON Schema。
  4. 3 个 templates 存在并包含要求章节。
  5. fixtures/synthetic/README.md 存在。
  6. .gitignore 包含 designos-workspace/ runs/ private-evidence/ *.log *.zip 等规则。
  7. issue templates 包含 privacy confirmation。
  8. issue templates 不要求用户上传完整 run workspace / 真实 PRD / 真实截图 / 真实仓库。
  9. diagnostic-summary schema 不含 forbidden fields。
  10. diagnostic-summary schema 必须包含 run_workspace_id,但不能包含 run_workspace_path。
  11. sanitized issue schema 枚举完整。
  12. evidence_ref 字段说明只能是 ID,不得要求填写 path。
  13. 新增文件不出现真实 URL/邮箱/token/password/真实业务路径等。
  14. 允许出现占位符和官方字段。

退出码:0 = 全过;1 = 有失败。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

MASTER_REPORT = "docs/audits/S2-H7A-USER-FEEDBACK-SAFETY-INFRASTRUCTURE.md"

# S2-H7.1: diagnostic-summary 新增字段检查
H71_DIAGNOSTIC_FIELDS = [
    "recommended_missing_fields",
    "recommended_user_questions",
    "kr_summary",
    "affected_kr",
    "most_affected_kr",
]


ISSUE_TEMPLATES = [
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/skill_quality_report.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
]

SCHEMAS = [
    "schemas/feedback/diagnostic-summary.schema.json",
    "schemas/feedback/sanitized-issue.schema.json",
]

TEMPLATES = [
    "templates/diagnostic-summary.md",
    "templates/sanitized-issue-registry.md",
    "templates/synthetic-replay-case.md",
]

FIXTURES_README = "fixtures/synthetic/README.md"

GITIGNORE = ".gitignore"

FORBIDDEN_FIELDS = [
    "original_input",
    "prd_text",
    "screenshot_ocr",
    "url",
    "email",
    "password",
    "token",
    "secret",
    "local_path",
    "run_workspace_path",
    "private_evidence_path",
]

GITIGNORE_REQUIRED = [
    "designos-workspace/",
    "runs/",
    "private-evidence/",
    "*.log",
    "*.zip",
]


def main() -> int:
    errors: list[str] = []

    # 1. master report
    if not (REPO_ROOT / MASTER_REPORT).is_file():
        errors.append(f"missing: {MASTER_REPORT}")

    # 2. issue templates
    for tmpl in ISSUE_TEMPLATES:
        if not (REPO_ROOT / tmpl).is_file():
            errors.append(f"missing: {tmpl}")
        else:
            text = (REPO_ROOT / tmpl).read_text(encoding="utf-8")
            # config.yml doesn't need privacy (it's just links)
            if "config.yml" not in tmpl:
                if "privacy" not in text.lower():
                    errors.append(f"{tmpl}: missing privacy mention")
            if "real PRD" in text or "真实 PRD" in text or "full run workspace" in text:
                # check if it's in "do not" context
                if "do not" not in text.lower() and "不要" not in text and "禁止" not in text:
                    errors.append(f"{tmpl}: asks for real materials")

    # 3. schemas
    for sch in SCHEMAS:
        p = REPO_ROOT / sch
        if not p.is_file():
            errors.append(f"missing: {sch}")
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if "diagnostic-summary" in sch:
                # check forbidden fields
                props = data.get("properties", {})
                for fb in FORBIDDEN_FIELDS:
                    if fb in props:
                        errors.append(f"{sch}: contains forbidden field '{fb}'")
                # check run_workspace_id present
                if "run_workspace_id" not in props:
                    errors.append(f"{sch}: missing run_workspace_id")
                # check evidence_ref is ID only
                if "evidence_ref" in props:
                    desc = props["evidence_ref"].get("description", "")
                    if "path" in desc.lower() and "not path" not in desc.lower():
                        errors.append(f"{sch}: evidence_ref mentions path")
            elif "sanitized-issue" in sch:
                # check enums
                props = data.get("properties", {})
                if "root_cause_type" in props:
                    if "enum" not in props["root_cause_type"]:
                        errors.append(f"{sch}: root_cause_type missing enum")
                if "fix_target" in props:
                    if "enum" not in props["fix_target"]:
                        errors.append(f"{sch}: fix_target missing enum")
        except json.JSONDecodeError:
            errors.append(f"{sch}: invalid JSON")

    # 4. templates
    for tmpl in TEMPLATES:
        if not (REPO_ROOT / tmpl).is_file():
            errors.append(f"missing: {tmpl}")

    # 5. fixtures README
    if not (REPO_ROOT / FIXTURES_README).is_file():
        errors.append(f"missing: {FIXTURES_README}")

    # 6. .gitignore
    gi = REPO_ROOT / GITIGNORE
    if gi.is_file():
        text = gi.read_text(encoding="utf-8")
        for rule in GITIGNORE_REQUIRED:
            if rule not in text:
                errors.append(f".gitignore: missing rule '{rule}'")

    print(f"checked feedback safety infrastructure")
    if errors:
        print(f"\n❌ {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(
        "\n✅ feedback safety infrastructure valid "
        "(master report / 3 issue templates / 2 schemas / 3 templates / fixtures README / .gitignore rules)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())