# DesignOS

<div align="center">

**AI-native 设计能力包 — 将资深设计专家方法论封装为可共享的 Skill 矩阵**

[![npm version](https://img.shields.io/npm/v/designos.svg)](https://www.npmjs.com/package/designos)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![CI Status](https://github.com/Eryooo/designos/workflows/CI/badge.svg)](https://github.com/Eryooo/designos/actions)

[安装](#安装) • [快速开始](#快速开始) • [核心技能](#核心技能) • [文档](AGENTS.md)

</div>

---

## 什么是 DesignOS？

DesignOS 是一个专为 AI 编程助手设计的**设计智能工作流引擎**，将 UX 评估、品牌设计、原型生成等复杂设计任务，转化为结构化、可复用的技能模块。

**适用于：**
- 产品经理快速验证交互方案
- 设计师批量生成初稿与变体
- 开发者理解设计意图并自查问题
- 创业团队在没有专业设计师时快速启动

**支持的 AI 编程助手：**
- [Claude Code](https://claude.ai/code)
- [Cursor](https://cursor.sh)
- Trae / Codex / Qoder / WorkBuddy

---

## 安装

一行命令，自动配置所有已安装的 IDE：

```bash
npx designos@latest
```

安装后，在任意项目目录的 AI 对话框输入 `/uxeval` 即可启动。

---

## 核心技能

### 🎯 UX 评估与优化
**`/uxeval`** — 基于尼尔森十大原则的启发式 UX 评估引擎
- 自动提取用户旅程与关键任务
- 多证据源交叉验证（截图 + PRD + 脚本）
- 生成可操作的问题报告与优先级建议

**示例：**
```bash
/uxeval screenshots/login-flow
```

---

### 📋 PRD 到原型
**`/prd2proto`** — PRD 文档到交互原型的自动化流水线
- 解析需求文档，生成页面结构与交互规范
- 输出 Figma-ready 的组件清单与流程图
- 支持多模态输入（文本 + 手绘草图）

**示例：**
```bash
/prd2proto docs/feature-spec.md
```

---

### 📊 AI 分析系统审计
**`/ai-analytics`** — AI 驱动的数据分析能力评估
- 审计现有分析系统的 AI 集成度
- 生成技术选型与实施路线图
- 输出成本效益分析报告

---

### 🎨 IP 角色设计
**`/ip-design`** — IP 角色视觉规范生成系统
- 从概念描述到完整视觉规范
- 自动生成多角度参考图与色彩方案
- 输出风格指南与应用示例

---

### 🏷️ 品牌视觉体系
**`/brand-creative`** — 完整品牌识别系统设计工具（6 个子技能）

| 子技能 | 功能 |
|--------|------|
| `brand-strategy` | 品牌定位与核心价值提炼 |
| `competitive-analysis` | 竞品视觉分析与差异化策略 |
| `logo-design` | 标志设计方案生成与变体 |
| `color-system` | 品牌色彩系统与应用规范 |
| `typography-system` | 字体选型与排版规范 |
| `visual-identity` | 完整视觉识别手册 |

**示例：**
```bash
/brand-creative --sub logo-design
/brand-creative --sub color-system
```

---

## 快速开始

### 1. 安装技能包

```bash
npx designos@latest
```

### 2. 在 AI 助手中调用

**UX 评估示例：**
```bash
# 在 Claude Code 或 Cursor 的对话框中
/uxeval screenshots/checkout-flow

# 指定 PRD 文档
/uxeval --prd docs/product-spec.md
```

**品牌设计示例：**
```bash
# 生成标志设计方案
/brand-creative --sub logo-design

# 完整品牌视觉体系
/brand-creative
```

### 3. 查看输出

所有技能会在项目目录下生成结构化输出：
- `output/uxeval/` — UX 评估报告
- `output/brand-creative/` — 品牌设计方案
- `output/prd2proto/` — 原型与交互规范

---

## 质量保证

- ✅ **259 项自动化测试** 覆盖全部核心流程
- ✅ **4/4 真实场景回归测试** 通过
- ✅ **CI/CD 流水线** 持续集成（代码检查 + 类型检查 + 单元测试）
- ✅ **独立版本管理** 每个技能独立演进，互不影响

---

## 文档

| 文档 | 说明 |
|------|------|
| [AGENTS.md](AGENTS.md) | 完整使用指南与 API 参考 |
| [CHANGELOG.md](CHANGELOG.md) | 版本更新日志 |
| [LICENSE](LICENSE) | Apache 2.0 开源许可 |

---

## 技术架构

**核心组件：**
- **Pipeline Engine** — 多阶段任务编排引擎
- **Knowledge Layer** — 领域知识注入系统
- **Multi-modal Input** — 支持文本 + 图像 + 结构化数据
- **Cross-IDE Bridge** — 统一的技能调用接口

**技术栈：**
- Python 3.11+ (核心引擎)
- YAML (流程定义)
- Node.js (CLI 安装器)

---

## 贡献

欢迎提交 Issue 和 Pull Request！

**开发前置要求：**
```bash
# 安装依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
ruff check .
pyright
```

**提交规范：**
- 遵循 [Conventional Commits](https://www.conventionalcommits.org/)
- 所有变更需通过 `ruff check`、`pyright`、`pytest` 三关

---

## 版本说明

**DesignOS 0.6.0** — MVP Trial Baseline

包含 6 个生产就绪技能模块，适合内部试用与快速验证。后续版本将持续扩展更多设计能力。

---

## 许可证

Apache 2.0 — 详见 [LICENSE](LICENSE)

---

## 联系方式

- **NPM:** https://www.npmjs.com/package/designos
- **GitHub:** https://github.com/Eryooo/designos
- **Issues:** https://github.com/Eryooo/designos/issues

---

<div align="center">
Made with ❤️ by DesignOS Team
</div>
