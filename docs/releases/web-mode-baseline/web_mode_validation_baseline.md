# Web Mode Validation Baseline

适用范围：DesignOS web mode 运行底座（playwright-driver + uxeval web 接线）。
本文件是 web mode 的**自包含最小回归基线**：脱离任何特定机器、不绑定某个 `.venv` 绝对路径，
任何人按此安装与执行即可判断 web mode 是“能力坏了”还是“只是没装依赖”。

- baseline 日期：2026-06-01
- 分支：factory-and-prd2proto-p1
- run_mode：web
- release_blocker_count：0

## 1. 最小依赖安装要求

web mode 把浏览器依赖列为 **optional dependency**（`designos[web]`），核心包不强依赖它。

```bash
# Python 包（最小）
pip install -e ".[web]"          # 等价于 pip install "playwright>=1.40"
# 真浏览器 smoke 还需要 chromium 二进制
python -m playwright install chromium
```

依赖分级：

| 能跑哪一层 | 需要什么 |
| --- | --- |
| Layer 1 `unit` | 无需 Playwright（任何环境必绿） |
| Layer 2 `requires_playwright` | `playwright` Python 包可 import |
| Layer 3 `browser_smoke` | chromium 二进制可真实 launch |

依赖缺失时，Layer 2/3 **显式 skip 并说明原因**，不会 fail，也不会污染 Layer 1。

## 2. 最小验证命令

下列命令用 `python`（按你的环境换成 `python3` 或对应解释器即可），
不依赖任何固定 `.venv` 路径。运行前设置 import 路径：

```bash
export PYTHONPATH="$PWD:$PWD/mcp-servers/playwright-driver"
```

### Layer 1 — unit（任何环境必绿）

```bash
python -m pytest -q -m unit mcp-servers/playwright-driver/tests/test_core.py
```

通过标准：全 passed，0 failed。**即使 `playwright` 未安装也必须全绿**——这是“能力坏没坏”
与“环境装没装”解耦的核心保证。可用如下方式自证（模拟依赖缺失后仍应全绿）：

```bash
# 用一个会抛 ImportError 的桩遮蔽 playwright，验证 unit 层不被污染
SHADOW=$(mktemp -d); mkdir -p "$SHADOW/playwright"
printf "raise ImportError('simulated absent')\n" > "$SHADOW/playwright/__init__.py"
PYTHONPATH="$SHADOW:$PWD:$PWD/mcp-servers/playwright-driver" \
  python -m pytest -rs mcp-servers/playwright-driver/tests/
rm -rf "$SHADOW"
# 期望：12 passed, 7 skipped（integration 显式 skip，不是 fail）
```

### Layer 2+3 — requires_playwright + browser_smoke（真 chromium）

```bash
python -m pytest -q mcp-servers/playwright-driver/tests/test_integration.py
```

通过标准（`browser_smoke` 不是“无条件已稳定跑绿”，而是条件化语义）：
- **依赖齐备时**（playwright 包 + chromium 二进制可 launch）：应全 `passed`。
- **依赖不齐时**：应全 `skipped` 并附原因，不计入 `failed`。
- **`skip` 不是 release blocker**：它是被设计的、显式可解释的环境事实，不代表能力回退。

### uxeval web-mode 接线

```bash
python -m pytest -q skills/uxeval/tests/test_pipeline_integration.py
```

### preflight 对 playwright-driver 的发现/提示

```bash
python -m pytest -q tests/unit/test_kernel_preflight.py
```

## 3. 当前已验证能力（2026-06-01）

下列为本基线**真实跑绿**的能力，可被后续 skill 直接信赖：

- web-mode 测试三层分层成立：`unit` / `requires_playwright` / `browser_smoke`。
- import 级联已切断：`playwright` 缺失时纯逻辑模块（schemas / evidence_builder /
  server 工具定义 / script_executor mock 执行）仍可 import 并通过单元测试。
- 真浏览器自动化 smoke：单页导航、截图、DOM 抽取、批量 JSON 脚本执行（`execute_batch`）、
  多 tab 切换、iframe 切换与读取、表单填充（不提交）——均在真 chromium 上 ground_truth 取证。
- uxeval web/client 分支与 `only_when` 路由、`web-automation → playwright-driver.execute_batch`
  接线在 SkillLoader 层成立。
- preflight 能在 web 模式缺 Playwright 时给出 mode-specific 的安装提示。

## 4. 当前未充分验证能力（不得当作“已生产可用”）

下列能力**代码已实现，但尚未有真实环境/真实站点的充分回归**，引用时必须标注边界：

- 真实登录态：`launch_persistent_context` 持久化目录已写，但**无真实账号密码登录全流程回归**。
- 多 tab / iframe：仅在本地 mock HTTP server 上验证；**未在真实复杂 Web 应用**（跨域 iframe、
  懒加载新窗口、SSO 跳转）上验证。
- heuristic-engine 集成：`heuristic_adapter.build_detection_request` 能产出
  DetectionRequest 结构，但**端到端“driver → heuristic-engine → 问题清单”闭环未在本基线内回归**。
- RetryPlanner 纠错：单测覆盖纠错策略生成，但**真实失败场景下的纠错有效性未做真站点回归**。

## 5. Release Blocker

- release_blocker_count：**0**
- 判定口径：web-mode 基线的 release blocker 仅指“Layer 1 unit 在依赖缺失时变红”
  或“真浏览器 smoke 在依赖齐备时变红”。当前两者皆未发生。
- 依赖缺失导致的 skip **不是** blocker，它是被设计的、显式可解释的行为。

## 6. 后续 skill 应该信哪条基线

- 想判断“web runtime 还活着吗” → 跑 Layer 1 unit（最快、无依赖）。
- 想判断“真浏览器能力还在吗” → 装 `designos[web]` + `playwright install chromium` 后跑 Layer 2+3。
- 想引用“某能力可直接用” → 只引用第 3 节；第 4 节能力必须自带“未充分验证”标注。

