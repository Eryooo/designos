# prd2proto

从 PRD → 可交互前端原型。基于 Senior Designer Work Paradigm Engine 的能力级 pilot。

## Status

**Capability-level Pilot** (2026-06-10)

- ✅ Pipeline v2: 17-stage 设计推理链路
- 🔄 Prompts: 框架完成，资深设计师逻辑补全中
- 🔄 LLM Execution: 从 mock 向真实执行迁移中
- 🔄 Schema Gates: 接入中
- ❌ Code Generation: 框架级占位
- ❌ Production Ready: 否

**本版本目标**: 把 prd2proto 从 framework/mock 推进到真实可执行的能力级 pilot。

## Pipeline 版本

- `pipeline.yaml`: **v2主线** (17 stages, 2026-06)
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
