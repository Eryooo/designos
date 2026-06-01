# DesignOS Skills Factory

> 把 skill 开发从"读文档理解 → 手写所有契约"，变成"按 archetype 装配 → 工厂保证骨架合规 → 只补业务逻辑"。

---

## 目标与成功标准

完整指标体系见 [`CONTRACT.md`](./CONTRACT.md)。一句话总纲：

> **工厂搭好的标志不是"代码写完"，而是"用工厂装配 ai-analytics 比手写 uxeval 快至少 10 倍，且零质量妥协"。**

---

## 当前状态（Wave 1 + Wave 2 已完成）

| 组件 | 状态 | 说明 |
|---|---|---|
| `CONTRACT.md` | ✅ | 工厂自身的合同 + 验收门 + 指标体系 |
| `_kernel_bridge.py` | ✅ | 复用 kernel 20 个 schema 的单一入口 |
| `archetypes/archetype_schema.py` | ✅ | "什么是 archetype" 的 Pydantic 定义 |
| `archetypes/loader.py` | ✅ | 加载并校验 archetype yaml |
| `archetypes/evaluation.yaml` | ✅ | 从 uxeval 萃取的 evaluation 契约 |
| `archetypes/generation.yaml` | ✅ | 从 prd2proto 萃取的 generation 契约 |
| `archetypes/analysis.yaml` | ✅ pilot | 从 ai-analytics A1 校准的 analysis 契约(已去 provisional) |
| `tools/extract.py` | ✅ | 反向萃取 archetype |
| `tools/validate.py` | ✅ | 校验 skill 是否符合 archetype |
| `tools/scaffold.py` | ✅ | 一键装配新 skill 骨架 |

测试基线：`9/9` 工厂回归 + `180/180` kernel 单元测试零回归。

**archetype 校准状态**:
- `evaluation.yaml`:从 uxeval 萃取,已稳定。
- `generation.yaml`:从 prd2proto 萃取,已稳定。
- `analysis.yaml`:从 ai-analytics A1 pilot 校准,**已去 provisional**。version `0.1.0-pilot`,反映真实 LLM-synthesis 实现(data_collection/report_generation 非真工具)。

---

## 三大 Archetype

按"输出语义"区分，**不要按 skill 名称**：

| Archetype | 输出本质 | 代表 skill | mode 语义 |
|---|---|---|---|
| **evaluation** | 问题清单（带证据） | uxeval, design-acceptance | evidence_collection（web/client） |
| **generation** | 代码 / 文档 / prompt | prd2proto, ip-design | fidelity（pm/designer-spec/designer-dsl） |
| **analysis** | 分析报告 / 上游产物 | ai-analytics | data_source |

⚠️ 同一个词 "mode" 在三类里语义不同，archetype.yaml 必须显式声明 `mode_semantics`。

---

## 目录结构

```
.factory/
├── CONTRACT.md                  # ★ 工厂合同（Agent 必读）
├── README.md                    # 本文件
├── pytest.ini                   # 工厂测试独立 root
├── __init__.py
├── _kernel_bridge.py            # ★ kernel schema 唯一 import 入口
├── archetypes/
│   ├── __init__.py
│   ├── archetype_schema.py      # ArchetypeSpec Pydantic
│   ├── loader.py                # load_archetype("evaluation")
│   └── evaluation.yaml          # 从 uxeval 萃取的契约
├── tools/                       # Wave 2 待填
│   ├── __init__.py
│   ├── extract.py               # ⏳ Agent A
│   ├── validate.py              # ⏳ Agent B
│   └── scaffold.py              # ⏳ Agent C
└── tests/
    ├── conftest.py
    ├── test_kernel_bridge.py    # bridge 不漂移
    └── test_archetype_evaluation.py  # evaluation.yaml 合法
```

---

## 开发约束（来自 CONTRACT §6）

- ❌ 不重新定义 kernel 已有 schema（`SkillConfig` / `StageConfig` …）— 必须从 `_kernel_bridge` import
- ❌ 不修改 `skills/uxeval/`（已冻结）
- ❌ 不修改 `kernel/`（kernel 是真源）
- ❌ 装配出"看起来对"但 kernel 加载不了的骨架
- ❌ 工厂代码 import 任何 skill 内部模块（工厂只能 import kernel）
- ❌ 工厂代码不带 pytest 就提交

---

## 跑测试

```bash
# 工厂自身回归（独立 root，不污染 kernel 测试）
cd .factory && python3 -m pytest tests/ -q

# kernel 零回归确认
cd .. && python3 -m pytest tests/unit/ -q
```

---

## 下一步（Wave 2 — 三个 Agent 并行）

| Agent | 模块 | 闭环要求 |
|---|---|---|
| A | `tools/extract.py` | 从 uxeval 萃取 vs 手写 evaluation.yaml ≥ 90% 一致 |
| B | `tools/validate.py` | uxeval 通过；故意注入违规必拦截 |
| C | `tools/scaffold.py` | 装配产物可被 kernel 加载 + 过 validate + 过 preflight |

每个 Agent 自带 `tests/test_<agent>.py`，提交前必须自跑 ruff/pyright/pytest 全过。
