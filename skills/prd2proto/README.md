# prd2proto

从 PRD → 设计推理资产 → 受约束的原型 scaffold。基于 Senior Designer Work Paradigm Engine。

## Status

**状态口径见 `docs/STATUS-DEFINITION.md`（五层 readiness）**

当前真实状态（2026-06-10）：

| readiness 层 | 状态 | 说明 |
|-------------|------|------|
| methodology_ready | ✅ | 方法论底座完整 |
| prompt_ready | ✅ | prompts-v2 17/17 COMPLETE |
| runtime_ready | 🔄 partial | 真实 LLM 链路打通，已验证前 5+ stage，非全 17-stage 稳定 |
| validated | 🔄 进行中 | 真实 PRD 端到端验证（Batch 1） |
| enterprise_ready | ❌ | 未达 |

**not_allowed_claims**（禁止声称）：
- ❌ "终极目标达成" / "达到资深设计师产出水平"
- ❌ "production-ready" / "可生产级生成 runnable 原型"

**本版本定位**：prompt_ready + runtime_partial，**真实验证进行中**。代码生成为框架级 scaffold，非生产级。

## Pipeline 版本

- `pipeline.yaml`: **v2 主线** (17-stage 设计推理链路, 2026-06)
- `pipeline.v1.yaml`: legacy 旧版（8-stage，向后兼容保留）
- `pipeline.v1.yaml`: 旧版保留 (8 stages, 向后兼容)

默认运行 v2:
```bash
python skills/prd2proto/runtime/executor.py
```

显式运行 v1:
```bash
python skills/prd2proto/runtime/executor.py --pipeline skills/prd2proto/pipeline.v1.yaml
```

## Quick checks

```bash
python3 -c 'from kernel.skill_loader import load_pipeline_skill; load_pipeline_skill("./skills/prd2proto")'
```

## 文档

- `SKILL.md`: 技术设计与架构
- `PIPELINE-INTEGRATION.md`: Pipeline 集成说明
- `PILOT-BOUNDARY.md`: Pilot 边界与限制
