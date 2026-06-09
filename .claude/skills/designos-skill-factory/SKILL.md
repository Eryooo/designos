---
name: designos-skill-factory
description: DesignOS 新 skill 开发的工厂守则。在新建或扩展任何 DesignOS skill 时调用。强制走 factory archetype、引用 shared knowledge adapter、产出完整目录结构、声明 pilot boundary、跑 validate 与 pytest，并禁止伪装 production ready。
---

# designos-skill-factory — skill 工厂守则

新建或扩展任何 DesignOS skill 时调用本 skill。它保证新 skill 不是手搓孤儿，而是走工厂、接共享知识、有边界、有验证的标准件。

## 1. 必须走 factory archetype

- 新 skill 必须对应一个已存在的 factory archetype(evaluation / generation / analysis；不新增、不改 archetype 除非另有授权)。
- 用 archetype 规定的 stage_slots / outputs / checkpoints / gates 作为骨架，不自创结构。
- 选不到合适 archetype → **停**，回到用户讨论，不强行套。

## 2. 必须引用 shared knowledge adapter

- skill 复用通用知识时，引用 `knowledge/manifest.yaml` 中的资产 **id**，不在 skill 内复制通用正文。
- skill 私有 `reference/m0x-*.md` 只写"本 skill 如何在某 stage 应用该共享资产 id"，绑定 stage / schema / checkpoint。
- 共享层缺所需资产 → 按 `designos-knowledge-architect` 先在 knowledge 层补资产，再在 skill 引用。

## 3. 必须有的完整目录结构

```
skills/<name>/
├── SKILL.md          # frontmatter：name/version/type/description/requires
├── pipeline.yaml     # stage 编排（对齐 archetype）
├── constitution.md   # 该 skill 的硬规则
├── prompts/          # 各 stage prompt
├── reference/        # 私有知识，引用共享层 id
├── templates/        # 产出模板
├── eval/             # golden / failure 样例
└── tests/            # 结构与契约测试
```
任一缺失 → 视为未完成，不得声称落地。

## 4. 必须声明 pilot boundary

- 在 SKILL.md 或 constitution 明确:本 skill 处于 pilot，**能做什么 / 不能做什么 / 哪些是 LLM 合成而非真实工具**。
- 不把"pilot 阶段 LLM 占位"说成"已接真实工具/数据"。

## 5. 必须有 validate 与 pytest

```bash
python3 -m tools.validate skills/<name> --archetype <archetype>
python3 -m pytest -q skills/<name>/tests/
```
- validate 9 维度全过；测试断言**真实解析结果**（解析 yaml / 跑 loader），不是字符串匹配文本。
- 涉及 factory 时加跑 `.factory` 测试确认零回归。

## 6. 不允许伪装 production ready

- pilot 就标 pilot，version 用 `0.x.0-pilot` 之类，不冒充 stable。
- 不写"生产级""已就绪"等夸大表述，除非有真实工具接入 + 证据支撑。
- 收口走 `designos-closeout`，禁止文件 / 旧行为变更照其清单核。
