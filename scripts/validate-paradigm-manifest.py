#!/usr/bin/env python3
"""validate-paradigm-manifest.py — 校验 design-work-paradigm manifest 与目录一致性.

S1-0C 引入的最小校验。仅依赖 Python 标准库（不引入 PyYAML 等依赖，避免新依赖项）。

校验项:
  1. manifest 中每个 method.file 在 design-work-paradigm/ 目录中真实存在（区分大小写）。
  2. 目录中每个 .md 文件（除 README.md）都已被 manifest 登记，或显式列入 EXCLUDED_FILES。
  3. method id 不重复。
  4. method.file 不重复登记。

退出码:
  0 = 全部通过
  1 = 有不一致

用法:
  python3 scripts/validate-paradigm-manifest.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PARADIGM_DIR = REPO_ROOT / "knowledge" / "design-work-paradigm"
MANIFEST_PATH = PARADIGM_DIR / "manifest.yaml"

# 显式排除清单（README 永远不算方法文件；其他文件加入此列表需评审说明）。
EXCLUDED_FILES: set[str] = {"README.md"}


def parse_manifest_methods(text: str) -> list[dict[str, str]]:
    """极简 YAML 解析: 抓出 methods 列表中每个 entry 的 id 和 file（标准库, 不引 PyYAML）.

    依赖于本仓库 manifest 的稳定缩进格式: methods 项以 `  - id:` 起首, 同 entry 内 `    file:`.
    若 manifest 改用 PyYAML 不可读的复杂结构, 本解析器会报告 0 entries 触发失败.
    """
    methods: list[dict[str, str]] = []
    in_methods = False
    current: dict[str, str] | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        # 进入 methods: 区段
        if re.match(r"^methods:\s*$", line):
            in_methods = True
            continue
        if not in_methods:
            continue
        # 退出 methods 区段(遇到下一个顶层 key,如 skill_integration:)
        if re.match(r"^[a-zA-Z_]+:\s*$", line):
            if current is not None:
                methods.append(current)
                current = None
            in_methods = False
            continue
        # entry 起首
        m = re.match(r'^\s*-\s*id:\s*"?([^"\s]+)"?\s*$', line)
        if m:
            if current is not None:
                methods.append(current)
            current = {"id": m.group(1), "file": ""}
            continue
        # file 字段
        m = re.match(r'^\s*file:\s*"?([^"\s]+)"?\s*$', line)
        if m and current is not None:
            current["file"] = m.group(1)
    if current is not None:
        methods.append(current)
    return methods


def main() -> int:
    if not MANIFEST_PATH.exists():
        print(f"❌ manifest not found: {MANIFEST_PATH}", file=sys.stderr)
        return 1

    methods = parse_manifest_methods(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not methods:
        print("❌ no methods parsed from manifest (parser limitation or empty manifest)", file=sys.stderr)
        return 1

    errors: list[str] = []

    # 1. 每个 method.file 真实存在(大小写敏感)
    for entry in methods:
        if not entry["file"]:
            errors.append(f"method id={entry['id']} 缺少 file 字段")
            continue
        target = PARADIGM_DIR / entry["file"]
        if not target.is_file():
            # 大小写不敏感再查一次,给出具体提示
            siblings = {p.name.lower(): p.name for p in PARADIGM_DIR.glob("*.md")}
            ci_match = siblings.get(entry["file"].lower())
            if ci_match:
                errors.append(
                    f"method id={entry['id']} 大小写不一致: manifest='{entry['file']}' 磁盘='{ci_match}'"
                )
            else:
                errors.append(f"method id={entry['id']} 文件不存在: {entry['file']}")

    # 2. id 不重复 / file 不重复
    seen_ids: dict[str, int] = {}
    seen_files: dict[str, int] = {}
    for entry in methods:
        seen_ids[entry["id"]] = seen_ids.get(entry["id"], 0) + 1
        if entry["file"]:
            seen_files[entry["file"]] = seen_files.get(entry["file"], 0) + 1
    for k, v in seen_ids.items():
        if v > 1:
            errors.append(f"id 重复: {k} (出现 {v} 次)")
    for k, v in seen_files.items():
        if v > 1:
            errors.append(f"file 重复登记: {k} (出现 {v} 次)")

    # 3. 目录中无悬空 .md
    disk_files = {p.name for p in PARADIGM_DIR.glob("*.md")}
    registered = {entry["file"] for entry in methods if entry["file"]}
    unregistered = sorted(disk_files - registered - EXCLUDED_FILES)
    for f in unregistered:
        errors.append(f"目录文件未登记到 manifest: {f}")

    # 输出结果
    print(f"manifest 登记 method 数: {len(methods)}")
    print(f"磁盘 .md 数(含 README): {len(disk_files)}")
    print(f"显式 excluded: {sorted(EXCLUDED_FILES)}")
    if errors:
        print()
        print(f"❌ 校验失败 ({len(errors)} 项):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print()
    print("✅ design-work-paradigm manifest 与目录完全一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
