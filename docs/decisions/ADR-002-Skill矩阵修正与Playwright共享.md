# ADR-002：Skill 矩阵修正与 Playwright 共享方案

> 日期：2026-05-15
> 状态：已批准
> 决策人：young
> 触发：研读 `/Users/young/Documents/trae_projects/design-review` 和 `DVT Agent` 参考项目后修正认知

---

## 背景

通过研读用户已有的两个参考项目，发现对 UXEval 和 Design-System 两个 Skill 的能力定义存在偏差：

1. **UXEval 不是纯文档型 Agent**，而是能驱动 Playwright + Chromium 自动化执行的评估 Agent
2. **Design-System 的核心痛点**是 AI 代码还原度低 + 设计规范不一致，需要 DSL 解析 + Token 提取 + 还原度自检
3. **DVT Agent** 揭示了一个独立场景：「设计还原度验收」，与体验评估目标不同，应作为独立 Skill

---

## 修正记录

> 2026-05-15：在 ADR-002 批准当天，研读 6 个 trae_projects 参考项目后，部分决策被 [ADR-003](ADR-003-Skill矩阵收敛与SkillGroup形态.md) 进一步收敛：
> - **Skill 总数 7 → 6**：design-system 并入 prd2proto（三模式）
> - **brand-creative 升级为 Skill Group**（13+ 子技能）
> - 新增共享 MCP：methodology-advisor、image-analyzer
>
> 本 ADR 的 Playwright 共享 / 双模式 / 用户自装依赖等核心决策**继续生效**。

---

## R6 决策汇总

| # | 决策 | 结论 | 理由 |
|---|---|---|---|
| 6.1 | Skill 矩阵从 6 → 7 | 新增 `design-acceptance` Skill | 设计还原度验收是独立完整的工作场景 |
| 6.2 | Playwright 共享方式 | MCP Server 层共享（`playwright-driver`），Skill 层独立 | 升级、配置、登录策略只改一处 |
| 6.3 | 客户端自动化范围 | v1.0 仅支持「用户提供截图」；v1.1 + 加 Electron；v1.2+ 看需求 | 原生客户端自动化生态不成熟，环境配置复杂 |
| 6.4 | 外部依赖管理 | 用户自装 + Skill 预检 + install_hint | 不打包 Playwright/Mastergo MCP，零运维 |
| 6.5 | UXEval 双模式 | 同一 Skill 的 web/client 两种 mode | 询问用户、共享下游 stage |

---

## Skill 矩阵（修正后）

| Skill | 核心目标 | 双模式 | 关键 MCP 依赖 |
|---|---|---|---|
| **uxeval** | 体验启发式评估 + 可用性测试 | web / client | playwright-driver, heuristic-engine, pdf-parser, excel-builder |
| **design-acceptance** | 设计还原度验收（仅） | web / client | playwright-driver, visual-diff, dsl-parser |
| **prd2proto** | PRD → 可交互原型代码 | — | pdf-parser, frontend-codegen |
| **design-system** | 设计稿 → 高还原度前端代码 | — | dsl-parser, token-extractor, frontend-codegen |
| **ip-design** | IP 形象设计 | — | image-prompt-gen |
| **brand-creative** | 品牌咨询全流程 | — | image-prompt-gen, excel-builder |
| **ai-analytics** | 竞品分析 | — | competitor-scraper, excel-builder |

---

## MCP Server 矩阵（修正后）

### 自建（DesignOS 维护）

| Server | 用途 | 使用方 |
|---|---|---|
| pdf-parser | PRD 解析 | uxeval, prd2proto |
| excel-builder | Excel 报告生成 | 全部需要表格输出的 Skill |
| **playwright-driver** | Web/Electron 自动化 | uxeval, design-acceptance |
| **heuristic-engine** | 启发式检测引擎 | uxeval |
| **visual-diff** | 设计稿 vs 实现视觉对比 | design-acceptance |
| **dsl-parser** | MasterGo/Figma DSL 解析（封装） | design-system, design-acceptance |
| **token-extractor** | Design Token 提取 | design-system |
| **frontend-codegen** | 前端代码生成 | prd2proto, design-system |
| competitor-scraper | 竞品网站抓取 | ai-analytics |
| image-prompt-gen | AI 图像提示词生成 | ip-design, brand-creative |

### 外部（用户自装，DesignOS 仅声明依赖）

| Server | 安装方式 | 使用方 |
|---|---|---|
| mastergo-mcp | 用户从官方/社区安装 | dsl-parser 调用 |
| figma-mcp | 用户从社区安装 | dsl-parser 调用 |

### 外部依赖（操作系统级，用户自装）

| 依赖 | 安装提示 | 必需场景 |
|---|---|---|
| Playwright + Chromium | `pip install playwright && playwright install chromium` | uxeval/design-acceptance 的 web 模式 |
| Node.js | 官网下载 | playwright-driver 运行需要 |

---

## OutputType 枚举增补

```python
# 新增类型
EVALUATION_SCRIPT = "evaluation_script"          # uxeval 生成的 Playwright 脚本
AUTOMATED_EVAL_TRACE = "automated_eval_trace"    # 自动化执行的 trace
VISUAL_DIFF_REPORT = "visual_diff_report"        # 设计稿 vs 实现视觉差异
DESIGN_TOKEN_SPEC = "design_token_spec"          # Design Token 规范
FRONTEND_CODE = "frontend_code"                  # 生成的前端代码
ACCEPTANCE_REPORT = "acceptance_report"          # 设计验收报告
PAGE_MAPPING = "page_mapping"                    # 页面映射表（design-acceptance 输入）
```

---

## 影响

需同步更新：
- [x] `docs/INDEX.md` — Skill 数量、文档地图
- [x] `docs/decisions/ADR-001.md` — 在末尾追加「R6 修正参考 ADR-002」
- [x] `docs/architecture/01-总体架构.md` — Skill 列表、MCP Server 列表
- [x] `docs/schemas/output-types.md` — 新增类型
- [x] `docs/plans/01-项目排期.md` — M2 加 design-acceptance
- [x] `docs/plans/02-并行执行任务.md` — MCP Server 列表更新
