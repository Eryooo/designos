# Batch W1：Web Mode Self-Contained Baseline（计划）

日期：2026-06-01 ｜ 分支：factory-and-prd2proto-p1 ｜ Scope：仅 web mode 基线收口

## 问题根因（已实证）

1. `core.py` 顶层 `from playwright.sync_api import ...`，而 `server.py` / `script_executor.py`
   顶层又 import `core`。→ Playwright 缺失时，连纯 schema 单元测试也在 collection 阶段红。
   已模拟证明：playwright 缺失时 `test_core.py` 5 红 7 绿（本该全绿）。
2. 当前 worktree 无 `.venv`，client-mode baseline 里的 `./.venv/bin/python ...` 命令在此跑不起来。
3. 测试没有分层标记，"没装 Playwright" 会污染整套 web mode 质量判断。

## 改动清单

### A. 切断 import 级联（核心）
- `mcp-servers/playwright-driver/core.py`：把 playwright 导入改为 try/except 守卫；
  缺失时占位为 None，并新增 `playwright_available()`；在 `launch()` 真正用到时才抛清晰错误。
  （`from __future__ import annotations` 已在，注解为字符串，运行时不求值，安全。）

### B. 测试三层显式分层
- 新 marker：`unit`（无需 Playwright，任何环境必绿）、`requires_playwright`（包可导入）、
  `browser_smoke`（chromium 可真实 launch）。
- `tests/test_core.py`：标 `unit`（守卫后无 playwright 也全绿）。
- `tests/test_integration.py`：模块级标 `requires_playwright` + `browser_smoke`。
- `tests/conftest.py`：`pytest_configure` 注册 marker；`pytest_collection_modifyitems`
  在依赖缺失时对后两层 **skip 并写明原因**（不是 fail）。
- 根 `pyproject.toml`：注册同名 marker；新增 optional-dependency `web = ["playwright>=1.40"]`，
  让"最小安装命令"可被文档引用。

### C. baseline 文档落盘（脱机可读，不绑定本机路径）
- `docs/releases/web-mode-baseline/web_mode_validation_baseline.md`
- `docs/releases/web-mode-baseline/web_mode_known_boundaries.md`
- `docs/releases/web-mode-baseline/web_mode_baseline_manifest.json`
四问必答：最小依赖安装、最小验证命令（三层）、已验证能力、未充分验证能力、release_blocker。

### D. uxeval web mode 产品边界收正
- `skills/uxeval/SKILL.md`「Playwright（仅 web 模式）」段：把"已验证"与"已实现未充分验证"
  （真实登录态 / 多 tab / iframe / heuristic-engine 集成）分开写清，禁止写成"已生产可用"。

## 真回归（写进 baseline）
1. Layer1 unit：playwright 在场跑一次 + **模拟 playwright 缺失** 再跑一次，证明都绿。
2. Layer2 requires_playwright、Layer3 browser_smoke（真 chromium）。
3. uxeval web-mode pipeline integration（mode/only_when/web-automation 接线）。
4. preflight 对 playwright-driver 的真实发现/提示：`tests/unit/test_kernel_preflight.py`。

## 不做（Scope 红线）
prd2proto 新能力 / 其余 6 skills / factory 新功能 / client mode 增强 / 大范围重构。
