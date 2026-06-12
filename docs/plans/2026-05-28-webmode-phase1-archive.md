# Web Mode Phase 1 — 完整存档

## 日期
2026-05-28

## 阶段定位
按 DesignOS 阶段顺序：
- Phase A（client mode freeze）：✅ 已完成
- **Phase B（web mode 封装）：本阶段，Phase 1 完成，待真实产品验证**
- Phase C（Skills Factory Template）：下一步
- Phase D（剩余 6 skills）：未开始

---

## 产品价值

用户输入 `/uxeval web <URL> + PRD` 后，系统现在可以：
1. 自动从 PRD 生成评估任务清单
2. 自动生成 JSON 执行脚本
3. 启动真实浏览器（用户首次手动登录，登录态持久化）
4. 批量执行脚本，采集 ground truth evidence（URL + DOM + screenshot 三重锚定）
5. 自动重试失败步骤（selector 降级 / timeout 增加）
6. 输出 heuristic-engine 可直接消费的 DetectionRequest
7. 通过 heuristic-engine 检测体验问题
8. 生成最终评估报告

---

## 交付物清单

### 新增 MCP Server
```
mcp-servers/playwright-driver/
├── __init__.py
├── pyproject.toml
├── schemas.py            # 数据模型（9 个 Pydantic model）
├── core.py               # BrowserManager（11 个方法）
├── evidence_builder.py   # ground_truth evidence 格式化
├── script_executor.py    # JSON 脚本解释执行器
├── server.py             # MCP server 入口（12 个 tools）
├── heuristic_adapter.py  # web evidence → heuristic-engine 适配
├── retry_planner.py      # 失败步骤自动修正
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_core.py        # 12 个单元测试
    └── test_integration.py # 7 个集成测试
```

### 12 个 MCP Tools

| Tool | 职责 |
|---|---|
| browser_launch | 启动浏览器，加载 persistent context |
| browser_close | 关闭浏览器会话 |
| navigate | 导航到 URL |
| click_element | 点击（CSS / text / role 三种 selector） |
| fill_input | 填写表单 |
| capture_screenshot | 截图（full_page 可选） |
| get_page_state | 获取当前页面状态（URL/title/dom_text） |
| execute_script | 执行单个 JSON 脚本 |
| execute_batch | 批量执行多个脚本 + 自动重试 + 输出 detection_request |
| switch_page | 切换浏览器页签 |
| switch_frame | 切换 iframe |
| extract_dom | 提取 DOM 结构（含 placeholder/aria-label/classes 等） |

### Pipeline 改造（skills/uxeval/pipeline.yaml）

Web mode 现在有 **8 个 stages 的纯净链路**，client-only stages 已用 `only_when: mode == "client"` 隔离：

```
Stage 1: prd-understanding (LLM)
Stage 2: principle-mapping (LLM)
Stage 3: journey-modeling (LLM)
Stage 4: task-generation (LLM)
Stage 5a: task-script-generation (LLM → JSON 指令)
Stage 5b: web-automation (playwright-driver.execute_batch)
Stage 6: issue-attribution (LLM + heuristic-engine)
Stage 7: report-generation (excel-builder)
```

### Stage 5a Prompt 重写
从生成 JavaScript Playwright 代码改为生成结构化 JSON 指令，对齐 playwright-driver 的输入契约。

### SKILL.md 更新
- 移除 `APP_USERNAME` / `APP_PASSWORD`（改为用户手动登录 + persistent context）
- 保留 `APP_BASE_URL`

---

## 验证结果

### 测试覆盖
- 单元测试：12 passed（schemas + evidence + server + executor）
- 集成测试：7 passed（multi-tab + iframe + batch + form fill）
- **总计：19 passed, 0 failed**

### Kernel 集成验证
- ✅ Preflight：`mode == "web"` 时正确发现 playwright-driver
- ✅ Preflight：`mode == "client"` 时正确跳过 playwright-driver
- ✅ Stage 5a → 5b 数据流：evaluation_script (JSON) 正确传递
- ✅ Stage 5b → 6 数据流：screenshots + dom_data + detection_request 完整
- ✅ Pipeline 8 stages 无缺失依赖

### Pipeline 模拟测试
- ✅ 完整数据流：JSON 脚本 → execute_batch → screenshots + dom_data + detection_request
- ✅ DOM 富字段：placeholder + aria-label 正确捕获
- ✅ heuristic-engine 输入兼容：mode/screenshots/dom_data/principles 全部就绪

### 质量指标（合成测试场景）
| 指标 | 目标 | 实测 |
|---|---|---|
| 覆盖率 | 100% | 100%（15/15 steps） |
| 准确率 | 100% | 100%（all ground_truth） |
| 置信度 | 100% | 100%（verification_gap = []） |

---

## Git 状态

**分支：** `web-mode-phase1`（领先 main 10 commits）

**Commits：**
```
4df2684 fix(pipeline): scope client-only stages and gates for web mode compatibility
acf37b1 fix(pipeline): skip evidence gate in web mode + add dom_data to Stage 6 inputs
2ca4c76 fix(playwright-driver): accept evaluation_script from kernel pipeline
1e06436 feat(web-mode): integrate playwright-driver with kernel pipeline
3e29302 feat(playwright-driver): add execute_batch tool + enrich DOM extraction
65e2859 feat(playwright-driver): add RetryPlanner for failed step correction
ae4f100 feat(playwright-driver): add heuristic-engine adapter for web evidence
5a68928 test(playwright-driver): add integration tests for multi-tab, iframe, e2e
c318708 feat(web-mode): rewrite Stage 5a to JSON script format + add test conftest
6719438 feat(web-mode): implement playwright-driver MCP server skeleton
```

**远程推送状态：** 待用户网络恢复后 `git push -u origin web-mode-phase1`

---

## 待真实产品验证项

以下需要用户在另一台机器上用真实产品验证：

1. **Persistent context 跨会话登录态**：第一次登录后，后续启动是否自动恢复登录态
2. **Non-headless 用户体验**：浏览器弹出后用户是否能正常操作
3. **真实页面拓扑**：新页签 / iframe / 路由错跳 / 遮罩层 等场景
4. **Selector 命中率**：CSS / text / role 在真实复杂页面下的稳定性
5. **重试机制有效性**：RetryPlanner 在真实失败场景下能否成功修正
6. **端到端质量**：从 PRD 到最终报告的完整流程，是否达成 100% 覆盖/准确/置信

测试方式（用户机器）：
```bash
git checkout web-mode-phase1
pip install playwright pydantic pytest
python -m playwright install chromium
python -m pytest mcp-servers/playwright-driver/tests/ -v
# 然后用真实产品 URL + PRD 跑 /uxeval web
```

---

## Phase 1 已知边界

1. **Stage 6 prompt 尚未适配 web mode**：当前 prompt 是为 client mode 写的（消费 image_analysis + evidence_assessment），web mode 下需要适配为消费 dom_data + detection_request
2. **Web mode 专属 golden cases 未定义**：当前 golden case 只是合成测试，需要真实场景的 baseline
3. **延迟模式选择**：Stage 5a 的 prompt 要求生成完整 JSON 脚本，但用户首次进入需要手动登录，这个交互节点需要在真实环境验证

---

## 下一步：Phase C（Skills Factory Template）

按 Governor Spec 阶段顺序，下一步进入 Skills Factory Template 抽取。

目标：从 uxeval（client + web 双模式）中提炼出 8 套通用模板：
1. Input Contract
2. Evidence Contract
3. Delivery Contract
4. Runtime Skeleton
5. Benchmark / Eval Harness
6. Release Skeleton
7. Skill Archetype Model
8. Production Definition of Done

这一步的产出是后续 6 个 skills 的复用基础。
