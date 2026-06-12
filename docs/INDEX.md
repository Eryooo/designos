# DesignOS 文档索引

> 最后更新：2026-05-15
> 维护人：young
> 构建状态：M0 启动中

## 文档地图

```
docs/
├── INDEX.md                          ← 你在这里
├── 01-竞品调研.md                    # 开源生态调研报告
├── 02-产品方案-v0.1.md               # 产品+技术方案初版（已被拆分文档取代）
├── architecture/                     # 架构文档（拆分后的正式版）
│   ├── 01-总体架构.md                # 系统全景、分层、技术栈
│   ├── 02-Kernel-设计.md             # Kernel 模块结构 + 接口 + Pipeline/Group 双形态
│   ├── 03-Skill-规范.md              # SKILL.md / GROUP.md 格式、扩展流程
│   ├── 04-MCP-Server-规范.md         # 工具层设计、协议、部署形态（待写）
│   ├── 05-数据契约.md                # Stage 间 Schema、Skill 间传递、OutputType（待写）
│   ├── 06-记忆系统.md                # 三级记忆、GitHub 仓库方案、审批 SOP（待写）
│   └── 07-安全合规.md                # 脱敏、注入防护、审计、离线、开源 checklist（待写）
├── decisions/                        # 架构决策记录 (ADR)
│   ├── ADR-001-五轮决策汇总.md       # R1-R5 所有决策点的最终结论
│   ├── ADR-002-Skill矩阵修正与Playwright共享.md  # R6 修正：Playwright 共享 + 双模式
│   └── ADR-003-Skill矩阵收敛与SkillGroup形态.md  # R7 收敛：6 Skill + Skill Group + 共享 MCP
├── schemas/                          # 数据结构定义
│   └── output-types.md               # OutputType 枚举 + 各 Skill 的 Schema
├── plans/                            # 项目计划
│   ├── 01-项目排期.md                # Gantt + 里程碑 + 关键路径
│   ├── 02-并行执行任务.md            # 4 条并行线分工 + 验收标准
│   └── 03-Sub-agent-分工.md          # M0+M1 sub-agent 任务清单（实操级）
└── legacy/                           # 历史资产（只读参考）
    ├── agent-prototypes/             # 7 个 HTML 原型展示页
    ├── sharing-materials/            # 分享材料
    └── Agent自主进化方案.md           # 原始进化方案（已被正式文档取代）
```

## 快速查找

| 我想了解... | 看这份文档 |
|---|---|
| 项目是什么、为什么做 | `02-产品方案-v0.1.md` §1 |
| 整体架构图 | `architecture/01-总体架构.md` |
| Kernel 怎么设计的 | `architecture/02-Kernel-设计.md` |
| 怎么写一个新 Skill | `architecture/03-Skill-规范.md` |
| MCP Server 怎么接入 | `architecture/04-MCP-Server-规范.md` |
| Stage 之间传什么数据 | `architecture/05-数据契约.md` |
| 记忆怎么存、怎么审批 | `architecture/06-记忆系统.md` |
| 安全/脱敏/开源合规 | `architecture/07-安全合规.md` |
| 为什么选这个技术/方案 | `decisions/ADR-001` + `ADR-002`（Playwright 共享）+ `ADR-003`（Skill 收敛）|
| OutputType 枚举定义 | `schemas/output-types.md` |
| 项目排期和里程碑 | `plans/01-项目排期.md` |
| Sub-agent 怎么分工 | `plans/02-并行执行任务.md` |
| 竞品怎么做的 | `01-竞品调研.md` |
| 原始 Agent 原型长什么样 | `legacy/agent-prototypes/*.html` |

## 文档间引用约定

- 文档内引用用相对路径：`见 [Kernel 设计](architecture/02-Kernel-设计.md)`
- Schema 引用用锚点：`见 [OutputType](schemas/output-types.md#outputtype-枚举)`
- ADR 引用用编号：`见 ADR-001 §1.1`
