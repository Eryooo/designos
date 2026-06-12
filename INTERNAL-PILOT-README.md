# DesignOS — Internal Pilot

> **Internal pilot only · Not public release · Not enterprise-ready · Not all-skills senior-level · Do not redistribute**

## 这是什么

DesignOS 是一套把**资深设计师工作范式**沉淀为 AI Design Skills 的系统。
本仓库是从已脱敏的 clean snapshot 初始化的**内部试用主线**。

## 当前状态（请如实理解）

- 本 snapshot 已完成 **evidence sanitization**（证据脱敏）+ **口径治理** +
  **公网包引用清理**，当前内容敏感扫描 0 命中。
- **旧仓库历史 cleanup 仍 pending**（本仓库为干净重建，不含旧历史）。
- **npm 旧包处理 pending**（不要从本仓库发公网 npm；公网发布 workflow 已禁用）。
- **prd2proto 是当前推进最深的 seniorization pilot**，仍未 fully validated。
- **其他 skills（uxeval / ai-analytics / ip-design / brand-creative）
  尚未达到 senior-level**。
- DesignOS 的最终目标是**全 skills 达到资深设计师级能力**，仍在推进中。

## 试用口径

> DesignOS internal pilot：以 prd2proto 为样板，验证 AI Design Skills
> 如何沉淀资深设计师工作范式；其他 skills 正在按统一资深能力标准升级中。

**不要**宣传成"所有 skills 已达到资深设计师水准 / enterprise-ready"。

## 安装（内部）

internal pilot **不走公网 npm/pypi**。从内部私有仓库 checkout 后本地安装：

```bash
pip install -e ".[dev]"
```

文档里出现的 `<YOUR_INTERNAL_PACKAGE>` / `<YOUR_INTERNAL_REGISTRY>` /
`<YOUR_ORG>/<YOUR_INTERNAL_REPO>` 均为占位符，请替换为内部实际值。

## 边界

- ❌ not public release
- ❌ not enterprise-ready
- ❌ not all-skills senior-level
- ❌ do not redistribute
- ✅ internal pilot only

## 权威状态源

判断"某个 skill 现在到哪一步"，只看这些（不要看 `docs/archive/`）：
- `skills/status.matrix.yaml` — 逐 skill 五层 readiness
- `docs/STATUS-DEFINITION.md` — readiness 口径定义
- `REVIEW-MANIFEST.md` — 本快照评审清单（来源 commit、扫描、测试、后续路线）
