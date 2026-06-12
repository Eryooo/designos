---
description: 用 UXEval Skill 对产品做体验启发式评估（客户端截图 / Web 自动化）
argument-hint: [--mode web|client] [path-to-prd]
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
model: claude-opus-4-7
---

# /uxeval — 体验启发式评估

@AGENTS.md
@skills/uxeval/SKILL.md
@skills/uxeval/constitution.md
@skills/uxeval/pipeline.yaml

## 你的任务

用户输入了 `/uxeval $ARGUMENTS`。按 AGENTS.md 中定义的 UXEval Skill 完整流程执行。

## 参数解析

- `/uxeval` → 客户端模式，自动检测 PRD
- `/uxeval client` → 客户端模式
- `/uxeval client ./path/to/prd.md` → 客户端模式 + 指定 PRD
- `/uxeval web https://app.example.com` → Web 模式 + 指定 URL
- `/uxeval resume` → 恢复中断的评估
- `/uxeval --help` → 显示帮助

当前参数：`$ARGUMENTS`

## 执行流程

### 1. 自动初始化（AGENTS.md Step 1）

检测当前目录是否已是 DesignOS 工作区：
- 有 `designos.project.yaml` → 跳过初始化
- 没有 → 按 AGENTS.md Step 1 的 7 步自动初始化（找 PRD → 建目录 → 推断 scope → 确认模式）

### 2. 12 阶段流水线（AGENTS.md Step 2）

严格按 pipeline.yaml 定义的 12 stage 顺序执行。每个 LLM stage 加载对应 prompt 文件。

### 3. Checkpoint 处理

遇到 C1/C2/C3 时暂停，展示产物，等用户回复「继续/修改/补充」。

### 4. 评估宪法

每条问题输出必须满足 constitution.md 的 7 条硬约束。违反则重新生成。

## 环境检查

**不要让用户配 ANTHROPIC_API_KEY**。你（Claude Code）当前已经能调用 Claude 模型，直接用即可。

只有当用户明确要在终端批量跑（CLI 模式）时，才提示配 `.env.local`。

## 帮助信息（/uxeval --help 时显示）

```
UXEval — 体验启发式评估 Skill

用法：
  /uxeval                    客户端模式，自动检测 PRD
  /uxeval client [prd-path]  客户端模式，可选指定 PRD 路径
  /uxeval web <URL>          Web 模式（需 Playwright + 账号密码）
  /uxeval resume             恢复中断的评估

输入要求：
  必需：PRD 文档（.md / .pdf / .docx）
  推荐：5+ 张产品截图（客户端模式）
  可选：scope.md（AI 会自动从 PRD 推断）

输出：
  - 用户旅程图
  - 体验任务清单（完整版 + 简洁版）
  - 问题清单（含严重等级 + 证据 + 建议）
  - Excel 报告

耗时：约 6-8 分钟（12 个阶段）
```
