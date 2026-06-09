# ip-design Skill

> generation 型 skill,消费 DesignOS 共享设计决策库,产出结构化 IP 设计资产。

**Archetype**: generation  
**Version**: 0.1.0-pilot  
**Status**: pilot

## 快速开始

参见 [SKILL.md](./SKILL.md) 了解定位、边界、核心产出、质量承诺。

## 目录结构

```
skills/ip-design/
├── SKILL.md                   # skill 定位与边界
├── pipeline.yaml              # 六阶段 generation 流水线
├── constitution.md            # 宪章:8 条核心约束
├── prompts/                   # 6 个 stage prompt
│   ├── 01-strategy-alignment.md
│   ├── 02-worldview-building.md
│   ├── 03-persona-modeling.md
│   ├── 04-visual-translation.md
│   ├── 05-narrative-planning.md
│   └── 06-landing-spec.md
├── reference/                 # 6 个 adapter(如何应用共享方法论)
│   ├── adapter-strategy-alignment.md
│   ├── adapter-worldview-building.md
│   ├── adapter-persona-modeling.md
│   ├── adapter-visual-translation.md
│   ├── adapter-narrative-planning.md
│   └── adapter-landing-spec.md
├── templates/                 # 使用共享模板,不维护私有副本
│   └── README.md
├── eval/                      # golden / failure cases + promptfoo
│   ├── golden/
│   ├── failure/
│   └── promptfoo.yaml
├── tests/                     # pytest 测试
│   ├── test_ip_asset_quality.py      # I0 资产壳质量
│   └── test_pilot_structure.py       # I1 pilot 结构
└── knowledge-manifest.yaml    # 引用 22 个共享设计决策资产 id

共享决策库(source of truth):
knowledge/design/{ip,strategy,persona,visual,quality,templates,cases}/
```

## 核心产出

7 类结构化资产:
- brand_brief
- worldview
- persona_profile
- visual_spec
- content_plan
- brand_material_spec
- image_prompt_pack

## 验证

```bash
cd .factory
python3 -m tools.validate ../skills/ip-design --archetype generation

cd ..
python3 -m pytest -q skills/ip-design/tests/
```
