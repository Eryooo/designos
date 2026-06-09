# ai-analytics Validation Baseline（验证基线）

> 版本：A1 Pilot Baseline ｜ 日期：2026-06-01
> 用途：记录 ai-analytics pilot 的可复现验证命令与已知良好结果，作为后续改动的回归基线。

## 1. 验证命令与结果

### Layer 1 — archetype 结构校验

```bash
cd .factory && python3 -m tools.validate ../skills/ai-analytics --archetype analysis
```

通过标准：`✅ All checks passed`，9 个维度全过（frontmatter / directory / outputs /
stage_slots / checkpoint_slots / gate_slots / mode_semantics / evidence_contract /
constitution）。

最近一次观测：**✅ All checks passed（9/9 dimensions）**。

### Layer 2 — pilot baseline 契约测试

```bash
PYTHONPATH="$PWD" python3 -m pytest -q skills/ai-analytics/tests/
```

通过标准：全 passed。覆盖：
- skill 可被 kernel 加载、声明 4 个 analysis OutputType
- output_type 名精确等于 prd2proto upstream_refs 要的 `design_strategy` / `user_persona`
- 两个 output schema 含 prd2proto stage1 实际消费字段（target_audience / business_goal；
  persona role / goals / pain_points）
- QG1 数据完整度 gate 存在
- 全 stage 为 LLM synthesis（pilot 诚实标注）

最近一次观测：**7 passed**。

### Layer 3 — 下游回归（确认未碰坏 prd2proto 上游接口）

```bash
PYTHONPATH="$PWD" python3 -m pytest -q skills/prd2proto/tests/
```

通过标准：全 passed（ai-analytics 为纯新增 skill，不应影响 prd2proto）。

最近一次观测：**73 passed**。

## 2. 验证语义说明

- 本 pilot 不包含真实数据采集工具，因此**没有需要外部依赖（如 playwright）的 skip 类用例**——
  全部为纯结构 / 契约测试，环境无关，应稳定 pass。
- `eval/golden` 与 `eval/failure` 当前为占位骨架，待首次真实 pilot 跑通后回填 golden case，
  不计入本基线的 pass/fail。

## 3. release blocker 是否为 0

**是 0。** 三层验证全绿，且：
- output 契约与 prd2proto upstream_refs 精确对齐（接口真对得上，非概念）。
- 未改任何现有文件，下游 prd2proto 回归无损。
- pilot 的设计边界（非真自动化、佐证产物不机器消费）已在
  `ai_analytics_pilot_boundary.md` 显式声明，属已知边界而非阻断项。

## 4. 不在本基线范围

- 真实竞品采集、全方法论矩阵、BI 图表：见 pilot_boundary §2。
- prd2proto / factory / web mode / client mode：本批未改动。
