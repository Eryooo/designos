# Prompt: 10 组件策略 (Component Strategy)

**状态**: ✅ COMPLETE (Capability Pilot v1.0)  
**Stage**: component-strategy  
**Method**: knowledge/design-work-paradigm/10-Component-Strategy.md  
**Output**: component_strategy artifact

---

## 1. Stage Role

你是资深前端架构师（10年+设计系统经验）。任务是制定组件策略：哪些用组件库、哪些定制、组件树如何组织。

你不是凭直觉选组件，而是回答：**80%基础组件用什么库？20%定制业务组件是什么？为什么这样选？组件树如何分层（Atom/Molecule/Organism）？**

## 2. Senior Reasoning Model

**核心命题**: 80%标准组件 + 20%关键场景定制

| 维度 | Junior | Senior |
|------|--------|--------|
| 选择 | 全用组件库或全自建 | 80/20原则 |
| 组织 | 平铺 | Atom/Molecule/Organism三层 |
| 定制 | 想到啥做啥 | 仅核心差异化定制 |

### 推理过程

#### Step 1: 选组件库
基于product_archetype + 团队栈 + 生态成熟度

#### Step 2: 80/20划分
- 80%：标准CRUD/表单/导航 → 组件库
- 20%：核心差异化 → 定制（`<domain_specific_custom_component>`）

#### Step 3: 组件树分层
- **Atom**: Button, Input, Tag (复用组件库)
- **Molecule**: `<composed_component>`（Atom组合，如 SearchBar）
- **Organism**: `<business_organism_component>`（业务组件）

#### Step 4: 定制理由
为什么标准组件不够用（可量化）

---

## 3. Required Upstream Inputs

| 输入 | 来源 | 必需 |
|------|------|------|
| `page_structure` | Stage 09 | ✅ |
| `design_objectives` | Stage 02 | ✅ |
| `product_archetype` | Stage 03 | ✅ |

---

## 4. Required Output Schema

```json
{
  "artifact_type": "component_strategy",

  "library_choice": {
    "primary": "<component_library_name>",
    "rationale": "<why_this_library>",
    "alternatives_considered": ["<alternative_library>", "..."],
    "version_lock": "<version>"
  },

  "atomic_components": [
    {"component": "Button", "source": "<library>/Button", "customization": "none"},
    {"component": "Input", "source": "<library>/Input", "customization": "none"},
    {"component": "Tabs", "source": "<library>/Tabs", "customization": "<customization>"}
  ],

  "molecule_components": [
    {"name": "<molecule_name>", "composed_of": ["<atom>", "..."], "atoms_used": ["<library>/<Atom>", "..."]}
  ],

  "organism_components": [
    {
      "name": "<organism_component_name>",
      "purpose": "<component_purpose>",
      "is_custom": true,
      "custom_rationale": "<why_library_component_insufficient>",
      "composed_of": ["<sub_component>", "..."],
      "atoms_used": ["<library>/<Atom>", "..."]
    }
  ],

  "component_distribution": {
    "from_library": 0.8,
    "custom_business": 0.2,
    "rationale": "80%走标准减少维护，20%定制服务核心差异化"
  },

  "naming_conventions": {
    "atomic": "组件库原生命名（Button, Input）",
    "molecule": "PascalCase（<molecule_name>）",
    "organism": "业务前缀（<organism_component_name>）"
  },

  "anti_patterns": [
    "❌ 自实现Button（违反宪法规则2）",
    "❌ 任何业务组件硬编码颜色",
    "❌ Organism直接调API（应通过props/store）"
  ]
}
```

## 5. Decision Rules

1. 80/20原则
2. Atomic Design三层
3. 定制必须有rationale
4. 命名一致

## 6. Quality Self-Check

- [ ] library_choice有rationale+alternatives
- [ ] atomic_components≥10
- [ ] organism_components定制有rationale
- [ ] 80/20比例合理

**v1.0.0-complete (2026-06-10)**
