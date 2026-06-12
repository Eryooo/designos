# DesignOS

<div align="center">

**🎨 AI 驱动的设计工作流引擎**

将设计专业知识转化为可复用的 AI 技能，适用于 Claude Code、Cursor 等工具。

![Skills](https://img.shields.io/badge/技能数-5-purple?style=for-the-badge)
![Status](https://img.shields.io/badge/状态-内部试用-yellow?style=for-the-badge)
[![License](https://img.shields.io/badge/许可证-Apache%202.0-orange?style=for-the-badge)](LICENSE)

> **内部试用版本 — 非公开发布。** 状态以
> [`INTERNAL-PILOT-README.md`](INTERNAL-PILOT-README.md) ·
> [`REVIEW-MANIFEST.md`](REVIEW-MANIFEST.md) 为准。

[快速开始](#-快速开始) • [技能列表](#-技能列表) • [文档](docs/README.md) • [示例](docs/examples/)

</div>

---

## 🚀 快速开始

> 内部试用以干净快照分发，**不是**公网 npm 包。
> 请从内部私有仓库 / registry 安装，而非公网 registry。

```bash
# 在内部私有仓库 checkout 后
pip install -e ".[dev]"
```

然后在任何 AI 编程助手中使用：

```bash
/uxeval screenshots/login-flow        # UX 评估
/brand-creative --sub logo-design     # Logo 设计
/prd2proto docs/feature-spec.md       # PRD 转原型
```

**👉 [完整安装指南](docs/getting-started.md)**

---

## ✨ 技能列表

| 技能 | 描述 | 版本 |
|------|------|------|
| **uxeval** | 启发式 UX 评估引擎 | 1.0.0 |
| **prd2proto** | PRD 到交互式原型的流水线 | 0.2.0 |
| **ai-analytics** | AI 分析系统审计 | 0.1.0 |
| **ip-design** | IP 角色设计系统 | 0.1.0-pilot |
| **brand-creative** | 完整品牌识别工具包（6 个子技能） | 0.1.0-baseline |

**👉 [探索所有技能](docs/skills/)**

---

## 🔄 工作原理

```
用户输入
(截图 / PRD / 设计需求)
         │
         ▼
┌─────────────────────┐
│   知识注入           │  加载设计原则、启发式规则、模板
│                     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   流水线执行         │  多阶段处理：分析 → 评估 → 生成
│                     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   结构化输出         │  Markdown、YAML、HTML 报告
│                     │
└─────────────────────┘
```

---

## 📸 输出示例

### UXEval：电商结账流程评估

**输入**：
```bash
/uxeval screenshots/checkout-flow --prd docs/checkout-spec.md
```

**输出**：
```
output/uxeval/
├── journey-map.md           # 用户旅程 + 痛点标注
├── issues.xlsx              # 优先级问题列表（严重度 × 频率 × 修复成本）
├── html-report/             # 交互式 HTML 报告
│   ├── index.html
│   └── evidence/            # 标注截图
└── delivery-assessment.json # 质量指标 & 覆盖率
```

**示例问题检测**：
```markdown
## 严重问题 #1：隐藏的运费
**严重度**：高 | **Nielsen 原则**：系统状态可见性
**位置**：购物车摘要

**证据**：
- 截图 cart-01.png：价格仅在最后一步显示
- 用户引述："为什么结账时突然多了 ¥50？"

**影响**：
- 严重度：高（影响购买决策）
- 频率：高（100% 用户遇到）
- 修复成本：低（显示逻辑调整）

**建议**：在购物车中显示运费估算
```

### PRD2Proto：SaaS 仪表板原型

**输入**：
```bash
/prd2proto docs/dashboard-spec.md --mode designer-spec --framework react
```

**输出**：
```
output/prd2proto/
├── app/                    # 生成的 React 应用
│   ├── src/
│   │   ├── components/
│   │   └── pages/
│   ├── public/
│   └── package.json
├── design-spec.md          # 设计系统文档
├── tokens.json             # 设计令牌（颜色、间距、字体）
├── quality-report.json     # 保真度评分 & 违规项
└── README.md               # 运行说明
```

**生成的设计规范**：
```yaml
colors:
  primary: "#0066FF"
  secondary: "#6C757D"
  success: "#28A745"
  
typography:
  heading: "Inter, sans-serif"
  body: "Roboto, sans-serif"
  
layout:
  grid: 12
  gutter: 24px
  maxWidth: 1200px
```

### Brand-Creative：完整品牌标识

**输入**：
```bash
/brand-creative briefs/startup-brand.md --styles modern,minimalist
```

**输出**：
```
output/brand-creative/
├── logo/
│   ├── concept.md          # Logo 设计理念
│   ├── simplification-tiers.yaml  # 4 级简化层级
│   └── image-prompt.txt    # AI 图像生成提示词
├── color-system.yaml       # 品牌色彩 + 语义含义
├── typography.yaml         # 字体组合
├── voice-guide.md          # 品牌声音 & 语气
├── rubric-evaluation.json  # 9 维度自评
└── gap-report.md           # 相对高级设计师的质量差距
```

**👉 [查看更多示例](docs/examples/)**

---

## 🎯 为什么选择 DesignOS？

| 工具 | 功能定位 | 适用场景 |
|------|---------|----------|
| **Figma AI** | 可视化设计生成 | 需要像素级精确的设计稿 |
| **ui-ux-pro-max** | 设计系统生成（67 种风格） | 需要完整的设计系统 |
| **DesignOS** | **设计智能工作流** | 需要评估 + 生成 + 分析的全流程 |

**DesignOS = 唯一同时提供评估和生成的设计工具**

---

## 📊 详细技能对比

| 技能 | 输入 | 输出 | 适用场景 | 耗时 |
|------|------|------|---------|------|
| **uxeval** | 截图 + PRD | 旅程地图 + 问题列表 + HTML 报告 | UX 审查、可用性测试 | 2-3 分钟 |
| **prd2proto** | PRD 文档 | 可运行的 React/Vue 原型 | 快速验证、演示 | 4-5 分钟 |
| **brand-creative** | 品牌简报 | Logo + 色彩 + 字体 + 语气 | 品牌建设、重塑 | 3-4 分钟 |
| **logo-design** | 需求描述 | 3 个设计概念 + 图像提示词 | Logo 创作 | 1-2 分钟 |
| **ip-design** | 角色描述 | 人设 + 对话示例 + 视觉指南 | 吉祥物、游戏角色 | 2-3 分钟 |
| **ai-analytics** | 系统文档 | 成熟度评估 + 改进路线图 | 分析系统审计 | 3-4 分钟 |

---

## 📖 文档

- **[快速上手](docs/getting-started.md)** — 安装与首次使用
- **[技能参考](docs/skills/)** — 每个技能的详细文档
- **[示例库](docs/examples/)** — 真实案例
- **[API 参考](docs/api-reference.md)** — CLI 与流水线 API
- **[架构文档](docs/architecture.md)** — 系统架构
- **[性能基准](docs/benchmark.md)** — 性能指标
- **[故障排查](docs/troubleshooting.md)** — 常见问题解决

---

## 💬 社区

- **内部试用反馈** — 请在内部私有仓库提 issue / discussion
- **[更新日志](CHANGELOG.md)** — 版本发布说明

---

## 🎯 使用场景

- **产品经理**：快速验证交互流程
- **设计师**：批量生成设计变体
- **开发者**：理解设计意图 & 自查
- **初创公司**：无需全职设计师也能启动

---

## 📊 质量与状态

> **内部试用 — 非公开发布、未达企业级、并非全 skills 资深水准。**
> 状态以 `INTERNAL-PILOT-README.md` / `REVIEW-MANIFEST.md` 为准。

- ✅ 各 skill 单独运行时单元测试通过（跨 skill 一起收集有已知冲突，
  另有少量既有 pipeline 结构失败，详见 REVIEW-MANIFEST）
- 🧪 **4 种产品原型**用合成 PRD 演练过（未经真实生产使用验证）
- ✅ **CI/CD 流水线**（代码检查 + 类型检查 + 单元测试）
- ✅ **独立版本管理**每个技能单独发版
- ⚠️ **prd2proto** 是当前推进最深的资深化样板；其他 skills
  （uxeval / ai-analytics / ip-design / brand-creative）仍需资深化
- ✅ **基准测试框架**覆盖率、准确度、质量评分

---

## 🚀 性能

**典型执行时间**：
- uxeval（10 张截图）：~2-3 分钟
- prd2proto（5 页 PRD）：~4-5 分钟  
- brand-creative（完整标识）：~3-4 分钟

**资源占用**：
- 内存：每次执行 ~500MB
- 磁盘：每次运行输出 ~10MB

---

## 🤝 贡献

欢迎贡献！查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

```bash
# 克隆并安装（替换为你的内部私有仓库地址）
git clone <YOUR_INTERNAL_PRIVATE_REPO_URL>
cd designos
npm install

# 运行测试
npm test

# 添加新技能
npm run create-skill my-skill
```

---

## 📜 许可证

[Apache 2.0](LICENSE) © 2026 DesignOS Contributors

---

## 🔗 相关项目

- [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) - 设计系统生成器
- [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) - 品牌设计库
- [Claude Code](https://claude.ai/code) - AI 编程助手
- [Cursor](https://cursor.sh) - AI 代码编辑器

---

**语言版本**：[English](README.md) | 简体中文

**最后更新**：2026-06-09 | **版本**：0.6.2
