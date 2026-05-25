# UXEval Skill

> 体验启发式评估 + 可用性测试 Pipeline Skill
> 版本：v0.2.0 · 形态：Pipeline · 模式：web / client

## 是什么

UXEval 把高级体验设计师的评估流程标准化成「需求理解 → 旅程建模 → 任务清单 → 证据采集 → 问题归因 → 报告」的 6 环节工作流。

每次跑完会产出：
- 用户旅程地图（Markdown）
- 任务清单（完整版 + 简洁执行版）
- 体验问题报告（Excel + Markdown + HTML）
- 证据包（截图 + DOM + trace）

## 为什么

传统体验评估的痛点：
- 依赖资深设计师经验，新人难以稳定复现
- 评估口径不统一，问题粒度不一致
- 评估只看页面，不看任务
- 问题只是描述，缺少证据
- 一次性产物，难以复用

UXEval 解决方式：
1. **结构化输入**：把 PRD / 原则 / 截图统一为可消费数据
2. **旅程驱动**：用旅程地图替代页面菜单作为评估骨架
3. **原则映射**：把启发式原则绑到具体模块，避免发散
4. **证据闭环**：每条问题都有截图 / DOM / trace 锚定
5. **双重产物**：完整版给专家把控，简洁版给中低阶设计师执行
6. **可复用资产**：方法论 + 模板 + 脚本沉淀到组织记忆

## 怎么用

### 1. 创建工作区

```bash
designos init my-uxeval-project --skill uxeval
cd my-uxeval-project
```

### 2. 准备输入

```
inputs/
├── prd.pdf            # 必需：产品 PRD
├── scope.md           # 必需：评估范围（复制 templates/scope.md 填）
├── principles.md      # 可选：自定义启发式原则
└── screens/           # 仅 client 模式必需：截图目录
```

Web 模式还需要 `.env.local`：
```
APP_BASE_URL=https://app.example.com
APP_USERNAME=test_user@example.com
APP_PASSWORD=********
```

### 3. 校验输入

```bash
designos input check uxeval
```

### 4. 跑评估

```bash
# Web 模式（自动化）
designos run uxeval --mode web

# Client 模式（截图分析）
designos run uxeval --mode client
```

执行过程中会在 3 个 checkpoint 暂停等你确认：
- C1：旅程地图确认
- C2：任务清单确认
- C3：问题清单确认

### 5. 查看产物

```
runs/001-uxeval/
├── 01-需求理解.md
├── 02-原则映射.md
├── 03-旅程地图.md
├── 04-任务清单-完整版.md
├── 04-任务清单-简洁版.md
├── 05-评估脚本/         # 仅 web 模式
├── 05-截图分析.json     # 仅 client 模式
├── 06-问题清单.json
├── 04-问题报告.xlsx
├── 04-问题报告.html
└── evidence/
```

## 双模式说明

| 模式 | 输入 | 自动化范围 | 适用 |
|---|---|---|---|
| `web` | URL + 账号 | Playwright 自动登录 + 采集 | 后台 / SaaS |
| `client` | 截图目录 | LLM 多模态分析 | 客户端 / 移动端 / 已下线 |

## 7 条评估宪法

详见 [`constitution.md`](./constitution.md)：

1. 每条问题必须绑定证据
2. 不输出敏感信息
3. 严重等级在合法枚举内
4. 不把功能存在与否当作主要体验问题
5. 建议方案必须可执行
6. 问题描述必须包含用户影响
7. PRD 与实现冲突时标明基准来源

## 上下游 Skill

```
ai-analytics（竞品分析）
   │ design_strategy / user_persona
   ▼
uxeval（本 Skill）
   │ user_journey
   ▼
prd2proto（原型代码）
```

UXEval 可消费上游 ai-analytics 的产物，用于增强归因（竞品参照）。

## 与其他 Skill 边界

| 场景 | 用什么 |
|---|---|
| 「这功能好不好用」 | UXEval |
| 「这功能存不存在 / 还原度对不对」 | design-acceptance |
| 「PRD 怎么变原型」 | prd2proto |
| 「品牌 / 视觉评估」 | brand-creative:multi-dim-design-evaluator |

## 目录结构

```
skills/uxeval/
├── SKILL.md                      # 入口 + frontmatter（运行时 version 真源）
├── pipeline.yaml                 # 10-stage pipeline（只定义 stages，不声明独立运行时 version）
├── constitution.md               # 7 条宪法
├── INPUT.md                      # 输入指南
├── README.md                     # 本文件
├── reference/
│   ├── index.json
│   ├── m01-需求理解.md
│   ├── m02-启发式原则.md
│   ├── m03-旅程建模.md
│   ├── m04-任务生成.md
│   ├── m05-证据采集.md
│   └── m06-问题归因.md
├── prompts/
│   ├── 01-prd-understanding.md
│   ├── 02-principle-mapping.md
│   ├── 03-journey-modeling.md
│   ├── 04-task-generation.md
│   ├── 05a-script-generation.md
│   ├── 05b-screenshot-analysis.md
│   ├── 06-issue-attribution.md
│   └── CHANGELOG.md
├── templates/
│   ├── scope.md
│   ├── 旅程地图.md
│   ├── 任务清单-完整版.md
│   ├── 任务清单-简洁版.md
│   └── 问题报告.md
├── eval/
│   ├── golden/case-001-分类分级/
│   ├── failure/F001-功能测试偏移/
│   └── promptfoo.yaml
└── tests/
    ├── conftest.py
    ├── fixtures/
    └── test_pipeline_integration.py
```

## 测试

```bash
# 集成测试
uv run pytest skills/uxeval/tests/

# Promptfoo 评估
promptfoo eval -c skills/uxeval/eval/promptfoo.yaml
```

## 路线图

- v1.0：客户端 + Web 双模式（当前）
- v1.1：Electron 客户端自动化
- v1.2：原生移动端自动化（看需求）

## 参考

- `legacy/agent-prototypes/uxeval-agent.html`
- `legacy/sharing-materials/体验评估分享内容.md`
- ADR-002（双模式 + Playwright 共享）
- ADR-003（Skill 矩阵收敛）
