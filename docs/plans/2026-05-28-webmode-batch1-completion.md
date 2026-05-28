# Web Mode Batch 1 完成记录

## 日期
2026-05-28

## 产品价值
用户输入 `/uxeval web <URL>` 后，系统现在有了真实的浏览器自动化能力。playwright-driver MCP server 可以启动浏览器、导航页面、点击交互、截图、提取 DOM，并以 ground truth 级别的 evidence 返回结构化数据。

## 交付物

### 新增文件
```
mcp-servers/playwright-driver/
├── __init__.py
├── pyproject.toml
├── schemas.py          # 数据模型（ScriptStep, EvaluationScript, PageState, StepEvidence, ExecutionResult）
├── core.py             # BrowserManager（launch/close/navigate/click/fill/screenshot/get_state/switch_page/switch_frame/extract_dom）
├── evidence_builder.py # ground_truth evidence 格式化，对齐 Evidence Contract
├── script_executor.py  # JSON 脚本解释执行器
├── server.py           # MCP server 入口，11 个 tools 注册
└── tests/
    ├── __init__.py
    └── test_core.py    # 12 个单元测试
```

## 验证结果

- 单元测试：12 passed, 0 failed
- Kernel preflight 发现：✅ `_server_available()` 返回 True
- 冒烟测试（headless）：
  - ✅ 浏览器启动
  - ✅ 导航 https://example.com
  - ✅ 截图保存
  - ✅ DOM 提取
  - ✅ JSON 脚本批量执行（4/4 steps passed）
  - ✅ Evidence confidence = ground_truth
  - ✅ 浏览器关闭

## 关键指标映射

| 指标 | Batch 1 前 | Batch 1 后 |
|---|---|---|
| playwright-driver 存在 | ❌ | ✅ |
| kernel preflight 可发现 | ❌ | ✅ |
| 浏览器可启动 | ❌ | ✅ |
| evidence confidence = ground_truth | N/A | ✅ |
| JSON 脚本可执行 | ❌ | ✅ |

## 已知边界

- 登录态持久化已实现（persistent context），但未在真实登录场景验证
- 非 headless 模式已支持，但冒烟测试用的 headless
- switch_page / switch_frame 已实现，但未在多 tab/iframe 场景验证
- 与 heuristic-engine 的集成尚未完成

## 下一步（Batch 2 候选）

1. Stage 5a prompt 重写（生成 JSON 指令而非 JavaScript）
2. 非 headless 真实登录场景验证
3. 多 tab / iframe 场景验证
4. 与 heuristic-engine 集成
5. Web mode benchmark / golden cases
